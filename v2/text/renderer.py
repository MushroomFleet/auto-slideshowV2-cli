#!/usr/bin/env python3
"""
renderer.py - Text rendering functionality for Auto-Slideshow V2

This module handles rendering text overlays, captions, and title screens for slideshows.
"""

import os
import cv2
import numpy as np
from typing import Tuple, Dict, Optional, Union, List
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw

class TextRenderer:
    """Handles text rendering for slideshow creation"""
    
    def __init__(self):
        """Initialize the text renderer"""
        self.system_fonts = self._get_system_fonts()
        
        # Default settings
        self.default_font = 'Arial'
        self.default_size = 32
        self.default_color = '#FFFFFF'  # White
        self.default_bg_color = '#00000080'  # Semi-transparent black
    
    def _get_system_fonts(self) -> Dict[str, str]:
        """Get available system fonts
        
        Returns:
            Dictionary mapping font names to font file paths
        """
        # Start with common font locations
        font_locations = {
            'Arial': self._find_system_font(['arial.ttf', 'Arial.ttf']),
            'Helvetica': self._find_system_font(['helvetica.ttf', 'Helvetica.ttf']),
            'Times New Roman': self._find_system_font(['times.ttf', 'Times.ttf']),
            'Courier New': self._find_system_font(['cour.ttf', 'CourierNew.ttf']),
            'Verdana': self._find_system_font(['verdana.ttf', 'Verdana.ttf']),
            'Georgia': self._find_system_font(['georgia.ttf', 'Georgia.ttf']),
            'Comic Sans MS': self._find_system_font(['comic.ttf', 'ComicSansMS.ttf']),
            'Impact': self._find_system_font(['impact.ttf', 'Impact.ttf']),
        }
        
        # Return only fonts that were actually found
        return {name: path for name, path in font_locations.items() if path is not None}
    
    def _find_system_font(self, font_filenames: List[str]) -> Optional[str]:
        """Find a system font by filename
        
        Args:
            font_filenames: List of possible font filenames
            
        Returns:
            Font file path if found, None otherwise
        """
        # Common font directories
        font_dirs = []
        
        # Windows
        font_dirs.append(os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'))
        
        # macOS
        font_dirs.append('/Library/Fonts')
        font_dirs.append('/System/Library/Fonts')
        font_dirs.append(os.path.expanduser('~/Library/Fonts'))
        
        # Linux
        font_dirs.append('/usr/share/fonts')
        font_dirs.append('/usr/local/share/fonts')
        font_dirs.append(os.path.expanduser('~/.fonts'))
        
        # Try to find the font
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for font_filename in font_filenames:
                    font_path = os.path.join(font_dir, font_filename)
                    if os.path.exists(font_path):
                        return font_path
        
        return None
    
    def get_font(self, font_name: str, size: int) -> PIL.ImageFont.FreeTypeFont:
        """Get PIL font object
        
        Args:
            font_name: Font name
            size: Font size in points
            
        Returns:
            PIL font object
        """
        # Get font path
        if font_name in self.system_fonts:
            font_path = self.system_fonts[font_name]
        else:
            # Use default font if requested font is not available
            font_path = self.system_fonts.get(
                self.default_font, 
                # Last resort: use default PIL font
                None
            )
        
        # Load font
        try:
            if font_path:
                return PIL.ImageFont.truetype(font_path, size)
            else:
                return PIL.ImageFont.load_default()
        except Exception:
            # Fallback to default font
            return PIL.ImageFont.load_default()
    
    def _hex_to_bgr(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to BGR tuple
        
        Args:
            hex_color: Color in hex format (e.g. '#FFFFFF')
            
        Returns:
            Tuple of (blue, green, red) values
        """
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Parse RGB values
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Return as BGR (for OpenCV)
        return (b, g, r)
    
    def _parse_color_with_alpha(self, color_str: str) -> Tuple[Tuple[int, int, int], int]:
        """Parse color string with optional alpha
        
        Args:
            color_str: Color in hex format with optional alpha (e.g. '#FFFFFF' or '#FFFFFF80')
            
        Returns:
            Tuple of ((blue, green, red), alpha)
        """
        # Remove '#' if present
        color_str = color_str.lstrip('#')
        
        # Parse RGB values
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
        
        # Parse alpha if present
        if len(color_str) >= 8:
            alpha = int(color_str[6:8], 16)
        else:
            alpha = 255  # Fully opaque
        
        # Return as BGR (for OpenCV) and alpha
        return ((b, g, r), alpha)
    
    def create_title_screen(
        self,
        title_text: str,
        width: int,
        height: int,
        font_name: str = None,
        font_size: int = None,
        text_color: str = None,
        bg_color: str = None
    ) -> np.ndarray:
        """Create a title screen image
        
        Args:
            title_text: Text for the title
            width: Image width
            height: Image height
            font_name: Font name (default: Arial)
            font_size: Font size (default: calculated based on image dimensions)
            text_color: Text color in hex format (default: white)
            bg_color: Background color in hex format (default: black)
            
        Returns:
            Title screen image as numpy array
        """
        # Use default values if not specified
        font_name = font_name or self.default_font
        text_color = text_color or self.default_color
        bg_color = bg_color or '#000000FF'  # Fully opaque black
        
        # If font size not specified, calculate based on image dimensions
        if font_size is None:
            font_size = max(32, min(height // 10, width // (len(title_text) + 5)))
        
        # Parse colors
        (b, g, r), _ = self._parse_color_with_alpha(text_color)
        bg_bgr, bg_alpha = self._parse_color_with_alpha(bg_color)
        
        # Create background
        image = np.zeros((height, width, 3), dtype=np.uint8)
        image[:] = bg_bgr
        
        # Convert to PIL Image for text rendering
        pil_image = PIL.Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = PIL.ImageDraw.Draw(pil_image)
        
        # Get font
        font = self.get_font(font_name, font_size)
        
        # Calculate text size
        try:
            text_width, text_height = draw.textsize(title_text, font=font)
        except AttributeError:
            # For newer versions of Pillow
            bbox = draw.textbbox((0, 0), title_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        
        # Calculate text position (center)
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        # Draw text
        draw.text((text_x, text_y), title_text, font=font, fill=(r, g, b))
        
        # Convert back to OpenCV format
        result = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return result
    
    def add_caption(
        self,
        image: np.ndarray,
        caption_text: str,
        position: str = 'bottom',
        font_name: str = None,
        font_size: int = None,
        text_color: str = None,
        bg_color: str = None
    ) -> np.ndarray:
        """Add caption to an image
        
        Args:
            image: Input image
            caption_text: Caption text
            position: Caption position ('top', 'bottom', or 'center')
            font_name: Font name (default: Arial)
            font_size: Font size (default: calculated based on image dimensions)
            text_color: Text color in hex format (default: white)
            bg_color: Background color in hex format (default: semi-transparent black)
            
        Returns:
            Image with caption added
        """
        # Use default values if not specified
        font_name = font_name or self.default_font
        text_color = text_color or self.default_color
        bg_color = bg_color or self.default_bg_color
        
        height, width = image.shape[:2]
        
        # If font size not specified, calculate based on image dimensions
        if font_size is None:
            font_size = max(16, min(height // 20, width // 40))
        
        # Parse colors
        (b, g, r), _ = self._parse_color_with_alpha(text_color)
        bg_bgr, bg_alpha = self._parse_color_with_alpha(bg_color)
        
        # Create a copy of the image
        result = image.copy()
        
        # Convert to PIL Image for text rendering
        pil_image = PIL.Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        draw = PIL.ImageDraw.Draw(pil_image)
        
        # Get font
        font = self.get_font(font_name, font_size)
        
        # Calculate text size
        try:
            text_width, text_height = draw.textsize(caption_text, font=font)
        except AttributeError:
            # For newer versions of Pillow
            bbox = draw.textbbox((0, 0), caption_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        
        # Add padding
        padding = font_size // 2
        caption_height = text_height + (padding * 2)
        
        # Calculate caption position
        if position == 'top':
            caption_y = 0
        elif position == 'center':
            caption_y = (height - caption_height) // 2
        else:  # bottom
            caption_y = height - caption_height
        
        # Create caption background
        caption_bg = np.zeros((caption_height, width, 3), dtype=np.uint8)
        caption_bg[:] = bg_bgr
        
        # Create mask for semi-transparency
        if bg_alpha < 255:
            alpha = bg_alpha / 255.0
            caption_region = result[caption_y:caption_y+caption_height, :]
            caption_bg = cv2.addWeighted(caption_region, 1 - alpha, caption_bg, alpha, 0)
        
        # Place caption background on image
        result[caption_y:caption_y+caption_height, :] = caption_bg
        
        # Calculate text position (center horizontally)
        text_x = (width - text_width) // 2
        text_y = caption_y + padding
        
        # Draw text on image
        cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        cv2.putText(
            cv2_image,
            caption_text,
            (text_x, text_y + text_height),  # Add text_height because OpenCV text position is baseline
            cv2.FONT_HERSHEY_SIMPLEX,
            font_size / 30,  # Scale factor
            (r, g, b),
            1,  # Thickness
            cv2.LINE_AA
        )
        
        return cv2_image
    
    def list_available_fonts(self) -> List[str]:
        """List available fonts
        
        Returns:
            List of available font names
        """
        return sorted(list(self.system_fonts.keys()))
