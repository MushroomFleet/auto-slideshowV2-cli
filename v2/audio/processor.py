#!/usr/bin/env python3
"""
processor.py - Audio processing functionality for Auto-Slideshow V2

This module handles loading, processing, and integrating audio files
into slideshow videos, including volume adjustment, and fades.
"""

import os
import numpy as np
import subprocess
import tempfile
import librosa
import soundfile as sf
from typing import List, Tuple, Dict, Optional, Union, Any

class AudioProcessor:
    """Handles audio processing operations for slideshow creation"""
    
    def __init__(self):
        """Initialize the audio processor"""
        self.supported_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
        self.temp_files = []  # Track temporary files for cleanup
    
    def __del__(self):
        """Clean up any temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass
    
    def is_audio_file(self, file_path: str) -> bool:
        """Check if a file is a supported audio file
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if file is a supported audio file, False otherwise
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions
    
    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Tuple of (audio data, sample rate)
            
        Raises:
            ValueError: If file cannot be loaded or is not a supported audio file
        """
        if not self.is_audio_file(audio_path):
            raise ValueError(f"Unsupported audio file format: {audio_path}")
        
        try:
            # Use librosa to handle a variety of audio formats
            audio_data, sample_rate = librosa.load(audio_path, sr=None)
            return audio_data, sample_rate
        except Exception as e:
            raise ValueError(f"Could not load audio file {audio_path}: {str(e)}")
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Duration in seconds
            
        Raises:
            ValueError: If file cannot be loaded or duration cannot be determined
        """
        try:
            return librosa.get_duration(filename=audio_path)
        except Exception as e:
            raise ValueError(f"Could not determine audio duration for {audio_path}: {str(e)}")
    
    def adjust_audio_length(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int, 
        target_duration: float,
        loop: bool = True
    ) -> np.ndarray:
        """Adjust audio length to match target duration
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate of audio
            target_duration: Target duration in seconds
            loop: Whether to loop audio if it's too short (otherwise will be padded with silence)
            
        Returns:
            Adjusted audio data
        """
        # Calculate current duration
        current_duration = len(audio_data) / sample_rate
        
        # If current duration is very close to target, return as is
        if abs(current_duration - target_duration) < 0.1:
            return audio_data
        
        # Calculate target length in samples
        target_samples = int(target_duration * sample_rate)
        
        if current_duration > target_duration:
            # Trim audio if too long
            return audio_data[:target_samples]
        else:
            # Create result array
            result = np.zeros(target_samples)
            
            if loop:
                # Loop audio if it's too short
                full_loops = int(target_duration // current_duration)
                remainder_samples = int((target_duration % current_duration) * sample_rate)
                
                # Fill with full loops
                for i in range(full_loops):
                    start_idx = i * len(audio_data)
                    end_idx = start_idx + len(audio_data)
                    result[start_idx:end_idx] = audio_data
                
                # Fill remainder
                if remainder_samples > 0:
                    start_idx = full_loops * len(audio_data)
                    end_idx = min(start_idx + remainder_samples, target_samples)
                    result[start_idx:end_idx] = audio_data[:remainder_samples]
            else:
                # Just place the audio at the beginning, rest will be silence
                result[:len(audio_data)] = audio_data
            
            return result
    
    def apply_fade(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int, 
        fade_in_duration: float = 0.0, 
        fade_out_duration: float = 0.0
    ) -> np.ndarray:
        """Apply fade-in and fade-out to audio
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate of audio
            fade_in_duration: Fade-in duration in seconds
            fade_out_duration: Fade-out duration in seconds
            
        Returns:
            Audio data with fades applied
        """
        result = audio_data.copy()
        
        # Calculate fade lengths in samples
        fade_in_samples = int(fade_in_duration * sample_rate)
        fade_out_samples = int(fade_out_duration * sample_rate)
        
        # Apply fade-in
        if fade_in_samples > 0:
            fade_in_curve = np.linspace(0, 1, fade_in_samples)
            result[:fade_in_samples] *= fade_in_curve
        
        # Apply fade-out
        if fade_out_samples > 0:
            fade_out_curve = np.linspace(1, 0, fade_out_samples)
            result[-fade_out_samples:] *= fade_out_curve
        
        return result
    
    def adjust_volume(self, audio_data: np.ndarray, volume_multiplier: float = 1.0) -> np.ndarray:
        """Adjust audio volume
        
        Args:
            audio_data: Audio data array
            volume_multiplier: Volume multiplier (1.0 = no change)
            
        Returns:
            Audio data with adjusted volume
        """
        return audio_data * volume_multiplier
    
    def detect_beats(self, audio_data: np.ndarray, sample_rate: int) -> List[float]:
        """Detect beat timestamps in audio
        
        Args:
            audio_data: Audio data array
            sample_rate: Sample rate of audio
            
        Returns:
            List of beat timestamps in seconds
        """
        try:
            # Get beat frames
            tempo, beat_frames = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            
            # Convert frames to time (seconds)
            beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)
            
            return list(beat_times)
        except Exception:
            # Return empty list if beat detection fails
            return []
    
    def prepare_audio_for_ffmpeg(
        self, 
        audio_path: str,
        target_duration: float,
        volume: float = 1.0,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
        loop: bool = True
    ) -> str:
        """Prepare audio for use with FFmpeg in slideshow creation
        
        Args:
            audio_path: Path to audio file
            target_duration: Target duration in seconds
            volume: Volume multiplier (1.0 = no change)
            fade_in: Fade-in duration in seconds
            fade_out: Fade-out duration in seconds
            loop: Whether to loop audio if it's too short
            
        Returns:
            Path to processed audio file (temporary file)
            
        Raises:
            ValueError: If audio processing fails
        """
        try:
            # Load audio
            audio_data, sample_rate = self.load_audio(audio_path)
            
            # Process audio
            audio_data = self.adjust_audio_length(audio_data, sample_rate, target_duration, loop)
            audio_data = self.adjust_volume(audio_data, volume)
            audio_data = self.apply_fade(audio_data, sample_rate, fade_in, fade_out)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.close()
            sf.write(temp_file.name, audio_data, sample_rate)
            
            # Track for cleanup
            self.temp_files.append(temp_file.name)
            
            return temp_file.name
        except Exception as e:
            raise ValueError(f"Failed to process audio: {str(e)}")
    
    def add_audio_to_video(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> bool:
        """Add audio to video using FFmpeg
        
        Args:
            video_path: Path to input video
            audio_path: Path to audio file
            output_path: Path to output video
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use FFmpeg to add audio to video
            cmd = [
                'ffmpeg',
                '-i', video_path,  # Input video
                '-i', audio_path,  # Input audio
                '-c:v', 'copy',    # Copy video stream without re-encoding
                '-c:a', 'aac',     # Encode audio as AAC
                '-shortest',       # Match shortest stream
                '-y',              # Overwrite output without asking
                output_path
            ]
            
            # Run FFmpeg subprocess
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            _, stderr = process.communicate()
            
            # Check if successful
            if process.returncode != 0:
                print(f"FFmpeg error: {stderr.decode('utf-8')}")
                return False
                
            return True
        except Exception as e:
            print(f"Error adding audio to video: {str(e)}")
            return False
