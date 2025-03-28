#!/usr/bin/env python3
"""
slideshow.py - Main slideshow generator for Auto-Slideshow V2

This module ties together all the components to create slideshows from images.
"""

import os
import cv2
import numpy as np
import random
import time
import threading
import json
from typing import List, Dict, Tuple, Optional, Union, Any, Callable
from datetime import datetime

from ..core.image import ImageProcessor
from ..audio.processor import AudioProcessor
from ..text.renderer import TextRenderer
from ..transitions.effects import apply_transition, get_random_transition
from ..utils.config import ConfigManager, parse_aspect_ratio

class SlideshowGenerator:
    """Main class for generating slideshows"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the slideshow generator
        
        Args:
            config_path: Path to configuration file (optional)
        """
        # Initialize components
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.text_renderer = TextRenderer()
        
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Initialize state
        self.current_progress = 0.0
        self.is_cancelled = False
        self.is_paused = False
        self.state_file = None
        self.progress_callback = None
        
        # Parse configuration values
        self._parse_config()
    
    def _parse_config(self):
        """Parse configuration values from config manager"""
        # General settings
        self.transition_duration = float(self.config.get_value("SETTINGS", "transition_duration", "0.5"))
        self.video_duration = float(self.config.get_value("SETTINGS", "video_duration", "59"))
        self.frame_rate = int(self.config.get_value("SETTINGS", "frame_rate", "25"))
        self.transition_type = self.config.get_value("SETTINGS", "transition_type", "random")
        self.image_duration = float(self.config.get_value("SETTINGS", "image_duration", "3"))
        self.output_file = self.config.get_value("SETTINGS", "output_file", "slideshow.mp4")
        
        # Parse aspect ratio
        aspect_ratio_str = self.config.get_value("SETTINGS", "output_aspect_ratio", "16:9")
        self.aspect_ratio = parse_aspect_ratio(aspect_ratio_str)
        
        # Other settings
        self.multithreading = self.config.get_value("SETTINGS", "multithreading", "true").lower() == "true"
        self.ken_burns_enabled = self.config.get_value("SETTINGS", "ken_burns_enabled", "false").lower() == "true"
        self.ken_burns_intensity = float(self.config.get_value("SETTINGS", "ken_burns_intensity", "0.5"))
        
        # Text settings
        self.title_enabled = self.config.get_value("TEXT", "title_enabled", "false").lower() == "true"
        self.title_text = self.config.get_value("TEXT", "title_text", "")
        self.title_font = self.config.get_value("TEXT", "title_font", "Arial")
        self.title_size = int(self.config.get_value("TEXT", "title_size", "48"))
        self.title_color = self.config.get_value("TEXT", "title_color", "#FFFFFF")
        self.title_bg_color = self.config.get_value("TEXT", "title_bg_color", "#00000080")
        self.title_duration = float(self.config.get_value("TEXT", "title_duration", "3"))
        
        self.captions_enabled = self.config.get_value("TEXT", "captions_enabled", "false").lower() == "true"
        self.captions_position = self.config.get_value("TEXT", "captions_position", "bottom")
        self.captions_font = self.config.get_value("TEXT", "captions_font", "Arial")
        self.captions_size = int(self.config.get_value("TEXT", "captions_size", "32"))
        self.captions_color = self.config.get_value("TEXT", "captions_color", "#FFFFFF")
        self.captions_bg_color = self.config.get_value("TEXT", "captions_bg_color", "#00000080")
        
        # Audio settings
        self.audio_enabled = self.config.get_value("AUDIO", "audio_enabled", "false").lower() == "true"
        self.audio_file = self.config.get_value("AUDIO", "audio_file", "")
        self.audio_volume = float(self.config.get_value("AUDIO", "audio_volume", "1.0"))
        self.audio_fade_in = float(self.config.get_value("AUDIO", "audio_fade_in", "2.0"))
        self.audio_fade_out = float(self.config.get_value("AUDIO", "audio_fade_out", "2.0"))
        self.sync_to_beats = self.config.get_value("AUDIO", "sync_to_beats", "false").lower() == "true"
        self.loop_audio = self.config.get_value("AUDIO", "loop_audio", "true").lower() == "true"
        
        # Effects settings
        self.color_adjustment = self.config.get_value("EFFECTS", "color_adjustment", "none")
        self.vignette = self.config.get_value("EFFECTS", "vignette", "false").lower() == "true"
        self.picture_in_picture = self.config.get_value("EFFECTS", "picture_in_picture", "false").lower() == "true"
        self.pip_position = self.config.get_value("EFFECTS", "pip_position", "bottom-right")
    
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """Set a callback function for progress updates
        
        Args:
            callback: Function that takes a progress percentage (0-100) and status message
        """
        self.progress_callback = callback
    
    def _update_progress(self, progress: float, status: str = ""):
        """Update progress and call callback if set
        
        Args:
            progress: Progress percentage (0-100)
            status: Status message
        """
        self.current_progress = progress
        if self.progress_callback:
            self.progress_callback(progress, status)
        else:
            # Print progress to console if no callback is set
            print(f"Progress: {progress:.1f}% {status}", end='\r')
    
    def _save_state(self, frame_count: int, total_frames: int, image_index: int):
        """Save processing state to allow resuming
        
        Args:
            frame_count: Current frame count
            total_frames: Total frames to process
            image_index: Current image index
        """
        if not self.state_file:
            # Create state file based on output name
            base_name = os.path.splitext(self.output_file)[0]
            self.state_file = f"{base_name}.state.json"
        
        state = {
            "frame_count": frame_count,
            "total_frames": total_frames,
            "image_index": image_index,
            "output_file": self.output_file,
            "config_path": self.config.config_path,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
    
    def _load_state(self) -> Optional[Dict[str, Any]]:
        """Load processing state if available
        
        Returns:
            State dictionary or None if no state file exists
        """
        # Check for state file based on output name
        base_name = os.path.splitext(self.output_file)[0]
        state_file = f"{base_name}.state.json"
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                self.state_file = state_file
                return state
            except Exception as e:
                print(f"Warning: Failed to load state file: {e}")
        
        return None
    
    def _clean_state(self):
        """Remove state file after successful completion"""
        if self.state_file and os.path.exists(self.state_file):
            try:
                os.remove(self.state_file)
                self.state_file = None
            except Exception as e:
                print(f"Warning: Failed to remove state file: {e}")
    
    def cancel(self):
        """Cancel slideshow generation"""
        self.is_cancelled = True
    
    def pause(self):
        """Pause slideshow generation"""
        self.is_paused = True
    
    def resume(self):
        """Resume slideshow generation"""
        self.is_paused = False
    
    def create_slideshow(self, folder_path: str) -> bool:
        """Create slideshow from images in folder
        
        Args:
            folder_path: Path to folder containing images
            
        Returns:
            True if slideshow was created successfully, False otherwise
        """
        try:
            # Reset state
            self.is_cancelled = False
            self.is_paused = False
            
            # Get image files
            self._update_progress(1, "Finding images...")
            image_files = self.image_processor.get_image_files(folder_path)
            
            if len(image_files) < 2:
                raise ValueError("At least 2 images are required to create a slideshow")
            
            print(f"Found {len(image_files)} images in {folder_path}")
            
            # Check for existing state to resume
            state = self._load_state()
            
            # Calculate timing
            num_images = len(image_files)
            total_transitions = num_images - 1
            
            # Add title duration if enabled
            extra_duration = 0
            if self.title_enabled and self.title_text:
                extra_duration += self.title_duration
            
            # Calculate image duration based on video duration or use fixed duration
            if self.video_duration > 0:
                # Calculate image duration needed to achieve target video duration
                total_transition_time = total_transitions * self.transition_duration
                remaining_time = self.video_duration - total_transition_time - extra_duration
                
                if remaining_time <= 0:
                    raise ValueError(f"Transition time ({total_transition_time}s) and title time ({extra_duration}s) exceed video duration ({self.video_duration}s)")
                
                # Distribute remaining time among images
                image_duration = remaining_time / num_images
            else:
                # Use fixed duration per image
                image_duration = self.image_duration
                # Calculate total video duration
                self.video_duration = (num_images * image_duration) + (total_transitions * self.transition_duration) + extra_duration
            
            print(f"Using {image_duration:.2f} seconds per image and {self.transition_duration:.2f} seconds per transition")
            
            # Open first image to get dimensions
            self._update_progress(5, "Determining video dimensions...")
            first_image = self.image_processor.read_image(image_files[0])
            if first_image is None:
                raise ValueError(f"Could not read image: {image_files[0]}")
            
            # Get dimensions based on aspect ratio
            h, w = first_image.shape[:2]
            
            # Maintain original width, adjust height to match aspect ratio
            target_w = w
            target_h = int(w * self.aspect_ratio[1] / self.aspect_ratio[0])
            
            print(f"Video dimensions: {target_w}x{target_h} (aspect ratio: {self.aspect_ratio[0]}:{self.aspect_ratio[1]})")
            
            # Create video writer
            self._update_progress(10, "Creating video writer...")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use mp4v codec
            
            # If resuming, create a temporary output file
            if state:
                temp_output = self.output_file + ".temp.mp4"
                out = cv2.VideoWriter(temp_output, fourcc, self.frame_rate, (target_w, target_h))
                
                if not out.isOpened():
                    raise ValueError(f"Could not open temporary output video file: {temp_output}")
                
                # Set initial state
                frame_count = state["frame_count"]
                total_frames = state["total_frames"]
                start_image_index = state["image_index"]
                
                print(f"Resuming from frame {frame_count}/{total_frames} (image {start_image_index})")
            else:
                # Start from scratch
                out = cv2.VideoWriter(self.output_file, fourcc, self.frame_rate, (target_w, target_h))
                
                if not out.isOpened():
                    raise ValueError(f"Could not open output video file: {self.output_file}")
                
                frame_count = 0
                total_frames = int(self.video_duration * self.frame_rate)
                start_image_index = 0
            
            # Calculate frames per image and transition
            frames_per_image = int(image_duration * self.frame_rate)
            transition_frames = int(self.transition_duration * self.frame_rate)
            
            print(f"Creating slideshow with {num_images} images, {total_frames} frames...")
            
            # Process images
            prev_image = None
            
            # Add title screen if enabled
            if self.title_enabled and self.title_text and frame_count == 0:
                self._update_progress(15, "Creating title screen...")
                
                # Create title screen
                title_screen = self.text_renderer.create_title_screen(
                    self.title_text,
                    target_w,
                    target_h,
                    self.title_font,
                    self.title_size,
                    self.title_color,
                    self.title_bg_color
                )
                
                # Add title frames
                title_frames = int(self.title_duration * self.frame_rate)
                for i in range(title_frames):
                    if frame_count < total_frames:
                        out.write(title_screen)
                        frame_count += 1
                        
                        # Update progress periodically
                        if i % 10 == 0:
                            progress = min(100, int((frame_count / total_frames) * 100))
                            self._update_progress(progress, "Rendering title screen...")
                        
                        # Check for cancellation
                        if self.is_cancelled:
                            out.release()
                            print("\nSlideshow creation cancelled.")
                            return False
                        
                        # Handle pause
                        while self.is_paused:
                            time.sleep(0.1)
                
                # First actual image will transition from title
                prev_image = title_screen
            
            # Process each image
            for i in range(start_image_index, num_images):
                # Skip already processed images if resuming
                if state and i < start_image_index:
                    continue
                
                # Check for cancellation
                if self.is_cancelled:
                    out.release()
                    print("\nSlideshow creation cancelled.")
                    return False
                
                # Read and preprocess current image
                self._update_progress(
                    min(95, 15 + (80 * i / num_images)),
                    f"Processing image {i+1}/{num_images}..."
                )
                
                # Read image
                curr_img = self.image_processor.read_image(image_files[i])
                if curr_img is None:
                    print(f"Warning: Could not read image: {image_files[i]}, skipping...")
                    continue
                
                # Resize to target dimensions
                curr_img = self.image_processor.resize_to_aspect_ratio(
                    curr_img, 
                    self.aspect_ratio, 
                    target_w
                )
                
                # Apply color adjustments if enabled
                if self.color_adjustment != "none":
                    curr_img = self.image_processor.apply_color_adjustment(
                        curr_img, 
                        self.color_adjustment
                    )
                
                # Apply vignette if enabled
                if self.vignette:
                    curr_img = self.image_processor.apply_vignette(curr_img, 0.3)
                
                # Add caption if enabled
                if self.captions_enabled:
                    # Use filename without extension as caption
                    caption = os.path.splitext(os.path.basename(image_files[i]))[0]
                    
                    # Remove numeric prefixes (like 01_, 02_, etc.)
                    if caption[0:3].isdigit() and caption[3] in ['_', '-', ' ']:
                        caption = caption[4:]
                    
                    # Replace underscores with spaces
                    caption = caption.replace('_', ' ')
                    
                    # Add caption to image
                    curr_img = self.text_renderer.add_caption(
                        curr_img,
                        caption,
                        self.captions_position,
                        self.captions_font,
                        self.captions_size,
                        self.captions_color,
                        self.captions_bg_color
                    )
                
                # For the first image or if previous image not available
                if prev_image is None:
                    # Add frames for the first image duration
                    for j in range(frames_per_image):
                        if frame_count < total_frames:
                            # Apply Ken Burns effect if enabled
                            if self.ken_burns_enabled:
                                progress = j / frames_per_image
                                frame = self.image_processor.apply_ken_burns(
                                    curr_img, 
                                    'in', 
                                    progress, 
                                    self.ken_burns_intensity
                                )
                            else:
                                frame = curr_img
                                
                            out.write(frame)
                            frame_count += 1
                            
                            # Save state periodically
                            if j % 30 == 0:
                                self._save_state(frame_count, total_frames, i)
                                
                                # Update progress
                                progress = min(100, int((frame_count / total_frames) * 100))
                                self._update_progress(progress, f"Rendering image {i+1}/{num_images}...")
                            
                            # Check for cancellation
                            if self.is_cancelled:
                                out.release()
                                print("\nSlideshow creation cancelled.")
                                return False
                            
                            # Handle pause
                            while self.is_paused:
                                time.sleep(0.1)
                else:
                    # Choose transition for this pair of images
                    if self.transition_type == "random":
                        curr_transition = get_random_transition()
                    else:
                        curr_transition = self.transition_type
                    
                    # Add transition frames
                    for j in range(transition_frames):
                        if frame_count < total_frames:
                            progress = j / transition_frames
                            
                            # Create transition frame
                            frame = apply_transition(prev_image, curr_img, curr_transition, progress)
                            
                            out.write(frame)
                            frame_count += 1
                            
                            # Save state periodically
                            if j % 10 == 0:
                                self._save_state(frame_count, total_frames, i)
                                
                                # Update progress
                                progress = min(100, int((frame_count / total_frames) * 100))
                                self._update_progress(progress, f"Rendering transition {i}/{num_images-1}...")
                            
                            # Check for cancellation
                            if self.is_cancelled:
                                out.release()
                                print("\nSlideshow creation cancelled.")
                                return False
                            
                            # Handle pause
                            while self.is_paused:
                                time.sleep(0.1)
                    
                    # Add frames for current image duration (after transition)
                    for j in range(frames_per_image):
                        if frame_count < total_frames:
                            # Apply Ken Burns effect if enabled
                            if self.ken_burns_enabled:
                                progress = j / frames_per_image
                                frame = self.image_processor.apply_ken_burns(
                                    curr_img, 
                                    'in' if i % 2 == 0 else 'out',
                                    progress, 
                                    self.ken_burns_intensity
                                )
                            else:
                                frame = curr_img
                                
                            out.write(frame)
                            frame_count += 1
                            
                            # Save state periodically
                            if j % 30 == 0:
                                self._save_state(frame_count, total_frames, i)
                                
                                # Update progress
                                progress = min(100, int((frame_count / total_frames) * 100))
                                self._update_progress(progress, f"Rendering image {i+1}/{num_images}...")
                            
                            # Check for cancellation
                            if self.is_cancelled:
                                out.release()
                                print("\nSlideshow creation cancelled.")
                                return False
                            
                            # Handle pause
                            while self.is_paused:
                                time.sleep(0.1)
                
                # Update prev_image for next iteration
                prev_image = curr_img
            
            # Release video writer
            out.release()
            
            # If resuming, replace original file with temporary file
            if state:
                temp_output = self.output_file + ".temp.mp4"
                if os.path.exists(temp_output):
                    if os.path.exists(self.output_file):
                        os.remove(self.output_file)
                    os.rename(temp_output, self.output_file)
            
            # Add audio if enabled
            if self.audio_enabled and self.audio_file and os.path.exists(self.audio_file):
                self._update_progress(96, "Processing audio...")
                
                try:
                    # Prepare audio
                    temp_audio = self.audio_processor.prepare_audio_for_ffmpeg(
                        self.audio_file,
                        self.video_duration,
                        self.audio_volume,
                        self.audio_fade_in,
                        self.audio_fade_out,
                        self.loop_audio
                    )
                    
                    self._update_progress(98, "Adding audio to video...")
                    
                    # Add audio to video
                    temp_output = self.output_file + ".audio_temp.mp4"
                    success = self.audio_processor.add_audio_to_video(
                        self.output_file,
                        temp_audio,
                        temp_output
                    )
                    
                    if success:
                        # Replace original file with audio version
                        if os.path.exists(self.output_file):
                            os.remove(self.output_file)
                        os.rename(temp_output, self.output_file)
                        print(f"Added audio from {self.audio_file} to slideshow")
                    else:
                        print(f"Warning: Failed to add audio to slideshow")
                except Exception as e:
                    print(f"Warning: Error adding audio: {e}")
            
            # Clean up state file
            self._clean_state()
            
            self._update_progress(100, "Slideshow created successfully!")
            print(f"\nSlideshow created successfully: {self.output_file}")
            print(f"Video duration: {frame_count/self.frame_rate:.2f} seconds, {frame_count} frames at {self.frame_rate} FPS")
            
            return True
            
        except Exception as e:
            print(f"Error creating slideshow: {e}")
            return False
