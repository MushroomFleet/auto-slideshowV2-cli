#!/usr/bin/env python3
"""
image.py - Image processing functionality for Auto-Slideshow V2

This module handles loading, resizing, and manipulating images for the slideshow,
including the Ken Burns effect and color adjustments.
"""

import os
import cv2
import numpy as np
from glob import glob
from typing import List, Tuple, Dict, Optional, Union, Any

class ImageProcessor:
    """Handles image processing operations for slideshow creation"""
    
    def __init__(self):
        """Initialize the image processor"""
        self.supported_extensions = [
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'
        ]
    
    def get_image_files(self, folder_path: str, sort: bool = True) -> List[str]:
        """Get list of image files from folder
        
        Args:
            folder_path: Path to the folder containing images
            sort: Whether to sort files by name (default: True)
            
        Returns:
            List of image file paths
            
        Raises:
            ValueError: If no image files found in folder
        """
        image_files = []
        
        # Get files with all supported extensions (case insensitive)
        for ext in self.supported_extensions:
            image_files.extend(glob(os.path.join(folder_path, f"*{ext}")))
            image_files.extend(glob(os.path.join(folder_path, f"*{ext.upper()}")))
        
        # Sort files by name if requested
        if sort:
            image_files.sort()
        
        if not image_files:
            raise ValueError(f"No image files found in {folder_path}")
            
        return image_files
    
    def read_image(self, image_path: str) -> Optional[np.ndarray]:
        """Read an image from file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image as numpy array or None if reading fails
        """
        img = cv2.imread(image_path)
        return img
    
    def resize_to_aspect_ratio(
        self, 
        image: np.ndarray, 
        target_aspect_ratio: Tuple[int, int] = (16, 9),
        target_width: Optional[int] = None
    ) -> np.ndarray:
        """Resize image to target aspect ratio
        
        Args:
            image: Input image
            target_aspect_ratio: Tuple of (width, height) ratio (default: 16:9)
            target_width: Target width in pixels (optional, calc from original if not specified)
            
        Returns:
            Resized image
        """
        h, w = image.shape[:2]
        target_w, target_h = target_aspect_ratio
        
        # Calculate target dimensions
        current_ratio = w / h
        target_ratio = target_w / target_h
        
        if target_width is None:
            # Keep original width and adjust height
            target_width = w
        
        target_height = int(target_width * target_h / target_w)
        
        # If already close to target ratio, just resize
        if abs(current_ratio - target_ratio) < 0.01:
            return cv2.resize(image, (target_width, target_height))
        
        # Resize and crop to maintain aspect ratio
        if current_ratio > target_ratio:  # Image is wider
            new_h = target_height
            new_w = int(target_height * current_ratio)
            img_resized = cv2.resize(image, (new_w, new_h))
            # Crop to center
            start_x = (new_w - target_width) // 2
            return img_resized[:, start_x:start_x+target_width]
        else:  # Image is taller
            new_w = target_width
            new_h = int(target_width / current_ratio)
            img_resized = cv2.resize(image, (new_w, new_h))
            # Crop to center
            start_y = (new_h - target_height) // 2
            return img_resized[start_y:start_y+target_height, :]
    
    def apply_ken_burns(
        self, 
        image: np.ndarray, 
        zoom_direction: str = 'in',
        progress: float = 0.0,
        intensity: float = 0.5
    ) -> np.ndarray:
        """Apply Ken Burns effect to an image
        
        Args:
            image: Input image
            zoom_direction: 'in' or 'out' (default: 'in')
            progress: Float between 0.0 and 1.0 indicating effect progress
            intensity: Float between 0.0 and 1.0 indicating effect strength
            
        Returns:
            Image with Ken Burns effect applied
        """
        h, w = image.shape[:2]
        
        # Scale intensity to a reasonable zoom range (5-20%)
        max_zoom = 0.05 + (intensity * 0.15)
        
        if zoom_direction == 'in':
            # Start zoomed out, end zoomed in
            scale = 1.0 + (max_zoom * progress)
            # Also add slight pan
            shift_x = int(w * 0.1 * progress * intensity)
            shift_y = int(h * 0.1 * progress * intensity)
        else:  # zoom out
            # Start zoomed in, end zoomed out
            scale = 1.0 + (max_zoom * (1.0 - progress))
            # Also add slight pan in opposite direction
            shift_x = int(w * 0.1 * (1.0 - progress) * intensity)
            shift_y = int(h * 0.1 * (1.0 - progress) * intensity)
        
        # Calculate dimensions
        scaled_w = int(w * scale)
        scaled_h = int(h * scale)
        
        # Resize image
        img_scaled = cv2.resize(image, (scaled_w, scaled_h))
        
        # Create result image (same size as original)
        result = np.zeros_like(image)
        
        # Calculate crop region
        if zoom_direction == 'in':
            # When zooming in, we start with full frame and end with crop
            start_x = max(0, (scaled_w - w) // 2 + shift_x)
            start_y = max(0, (scaled_h - h) // 2 + shift_y)
        else:  # zoom out
            # When zooming out, we start with crop and end with full frame
            start_x = max(0, (scaled_w - w) // 2 - shift_x)
            start_y = max(0, (scaled_h - h) // 2 - shift_y)
        
        # Ensure we don't go out of bounds
        end_x = min(start_x + w, scaled_w)
        end_y = min(start_y + h, scaled_h)
        
        # Place cropped region into result
        copy_w = end_x - start_x
        copy_h = end_y - start_y
        
        result[:copy_h, :copy_w] = img_scaled[start_y:end_y, start_x:end_x]
        
        return result
    
    def apply_color_adjustment(
        self, 
        image: np.ndarray, 
        adjustment: str = 'none'
    ) -> np.ndarray:
        """Apply color adjustment to an image
        
        Args:
            image: Input image
            adjustment: Color adjustment type ('none', 'warm', 'cold', 'vintage', 'bw')
            
        Returns:
            Image with color adjustment applied
        """
        if adjustment == 'none':
            return image
        
        result = image.copy()
        
        if adjustment == 'warm':
            # Add warm tone (increase red, decrease blue)
            result = result.astype(np.float32)
            result[:,:,2] = np.clip(result[:,:,2] * 1.2, 0, 255)  # Increase red
            result[:,:,0] = np.clip(result[:,:,0] * 0.8, 0, 255)  # Decrease blue
            return result.astype(np.uint8)
            
        elif adjustment == 'cold':
            # Add cold tone (increase blue, decrease red)
            result = result.astype(np.float32)
            result[:,:,0] = np.clip(result[:,:,0] * 1.2, 0, 255)  # Increase blue
            result[:,:,2] = np.clip(result[:,:,2] * 0.8, 0, 255)  # Decrease red
            return result.astype(np.uint8)
            
        elif adjustment == 'vintage':
            # Add vintage/sepia effect
            result = result.astype(np.float32)
            
            # Convert to sepia tone
            sepia = np.array([[0.393, 0.769, 0.189],
                             [0.349, 0.686, 0.168],
                             [0.272, 0.534, 0.131]])
            
            # Apply sepia matrix
            sepia_img = cv2.transform(result, sepia)
            
            # Add slight vignette
            h, w = result.shape[:2]
            center_x, center_y = w // 2, h // 2
            radius = np.sqrt(w**2 + h**2) / 2
            
            Y, X = np.ogrid[:h, :w]
            dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
            
            # Create vignette mask
            mask = dist_from_center / radius
            mask = np.clip(mask, 0, 1)
            mask = 1 - mask * 0.3  # Adjust vignette strength
            
            # Apply vignette
            for c in range(3):
                sepia_img[:,:,c] = sepia_img[:,:,c] * mask
            
            return np.clip(sepia_img, 0, 255).astype(np.uint8)
            
        elif adjustment == 'bw':
            # Convert to black and white
            return cv2.cvtColor(cv2.cvtColor(result, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        
        return result
    
    def apply_vignette(self, image: np.ndarray, intensity: float = 0.3) -> np.ndarray:
        """Apply vignette effect to an image
        
        Args:
            image: Input image
            intensity: Float between 0.0 and 1.0 indicating effect strength
            
        Returns:
            Image with vignette effect applied
        """
        h, w = image.shape[:2]
        center_x, center_y = w // 2, h // 2
        radius = np.sqrt(w**2 + h**2) / 2
        
        Y, X = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        
        # Create vignette mask
        mask = dist_from_center / radius
        mask = np.clip(mask, 0, 1)
        mask = 1 - mask * intensity
        
        # Convert mask to 3-channel
        mask_3ch = np.stack([mask] * 3, axis=2)
        
        # Apply vignette
        result = image.astype(np.float32) * mask_3ch
        
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def estimate_image_complexity(self, image: np.ndarray) -> float:
        """Estimate image visual complexity to determine duration
        
        Args:
            image: Input image
            
        Returns:
            Complexity score between 0.0 and 1.0
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate complexity based on edge density and variance
        # 1. Edge detection using Sobel
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Combine Sobel X and Y
        edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Normalize edge magnitude
        edge_density = np.mean(edge_magnitude) / 255.0
        
        # 2. Image variance (higher variance = more complex)
        variance = np.var(gray) / (255.0 * 255.0)
        
        # Combine metrics
        complexity = (edge_density * 0.7) + (variance * 0.3)
        
        # Scale result to 0.5-1.0 range (to ensure minimum complexity is 0.5)
        scaled_complexity = 0.5 + (complexity * 0.5)
        
        return min(1.0, scaled_complexity)
