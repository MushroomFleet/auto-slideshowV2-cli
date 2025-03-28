#!/usr/bin/env python3
"""
config.py - Configuration management for Auto-Slideshow V2

This module handles loading, saving, and managing configuration settings
for the slideshow generator, including template support.
"""

import os
import configparser
import json
from typing import Dict, Any, Optional, List, Tuple

# Default configuration values
DEFAULT_CONFIG = {
    "SETTINGS": {
        "transition_duration": "0.5",  # seconds
        "video_duration": "59",  # seconds
        "frame_rate": "25",  # FPS
        "transition_type": "random",  # Can be specific or "random"
        "image_duration": "3",  # seconds per image
        "output_file": "slideshow.mp4",
        "output_aspect_ratio": "16:9",  # width:height
        "multithreading": "true",
        "quality": "high",
        "ken_burns_enabled": "false",
        "ken_burns_intensity": "0.5",
    },
    "TEXT": {
        "title_enabled": "false",
        "title_text": "",
        "title_font": "Arial",
        "title_size": "48",
        "title_color": "#FFFFFF",
        "title_bg_color": "#00000080",
        "title_duration": "3",
        "captions_enabled": "false",
        "captions_position": "bottom",  # top, bottom, center
        "captions_font": "Arial",
        "captions_size": "32",
        "captions_color": "#FFFFFF",
        "captions_bg_color": "#00000080",
    },
    "AUDIO": {
        "audio_enabled": "false",
        "audio_file": "",
        "audio_volume": "1.0",
        "audio_fade_in": "2.0",
        "audio_fade_out": "2.0",
        "sync_to_beats": "false",
        "loop_audio": "true",
    },
    "EFFECTS": {
        "color_adjustment": "none",  # none, warm, cold, vintage, bw
        "vignette": "false",
        "picture_in_picture": "false",
        "pip_position": "bottom-right",  # top-left, top-right, bottom-left, bottom-right
    }
}

# Template directory
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")

class ConfigManager:
    """Manages configuration settings for Auto-Slideshow"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = configparser.ConfigParser()
        
        # Set defaults
        for section, options in DEFAULT_CONFIG.items():
            if section not in self.config:
                self.config[section] = {}
            for option, value in options.items():
                self.config[section][option] = value
        
        # Read config file if specified
        if config_path and os.path.exists(config_path):
            self.config.read(config_path)
            self.config_path = config_path
        else:
            self.config_path = "config.cfg"
    
    def save(self, config_path: Optional[str] = None) -> str:
        """Save current configuration to file
        
        Args:
            config_path: Path to save configuration file (optional)
            
        Returns:
            Path where configuration was saved
        """
        save_path = config_path or self.config_path
        
        with open(save_path, 'w') as f:
            self.config.write(f)
        
        return save_path
    
    def get_value(self, section: str, option: str, fallback: Any = None) -> Any:
        """Get configuration value
        
        Args:
            section: Configuration section name
            option: Option name within section
            fallback: Default value if option not found
            
        Returns:
            Configuration value
        """
        return self.config.get(section, option, fallback=fallback)
    
    def set_value(self, section: str, option: str, value: Any) -> None:
        """Set configuration value
        
        Args:
            section: Configuration section name
            option: Option name within section
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][option] = str(value)
    
    def as_dict(self) -> Dict[str, Dict[str, str]]:
        """Export configuration as nested dictionary
        
        Returns:
            Dictionary representation of configuration
        """
        result = {}
        for section in self.config.sections():
            result[section] = {}
            for option in self.config[section]:
                result[section][option] = self.config[section][option]
        return result


class TemplateManager:
    """Manages slideshow templates"""
    
    def __init__(self):
        """Initialize template manager"""
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
    
    def list_templates(self) -> List[str]:
        """List available templates
        
        Returns:
            List of template names
        """
        templates = []
        for filename in os.listdir(TEMPLATE_DIR):
            if filename.endswith('.ini') or filename.endswith('.cfg'):
                templates.append(os.path.splitext(filename)[0])
        return templates
    
    def load_template(self, template_name: str) -> Optional[ConfigManager]:
        """Load a template
        
        Args:
            template_name: Name of template to load
            
        Returns:
            ConfigManager with template settings, or None if template not found
        """
        # Try both .ini and .cfg extensions
        template_path = os.path.join(TEMPLATE_DIR, f"{template_name}.ini")
        if not os.path.exists(template_path):
            template_path = os.path.join(TEMPLATE_DIR, f"{template_name}.cfg")
            if not os.path.exists(template_path):
                return None
        
        return ConfigManager(template_path)
    
    def save_template(self, template_name: str, config: ConfigManager) -> str:
        """Save a template
        
        Args:
            template_name: Name to save template as
            config: ConfigManager with settings to save
            
        Returns:
            Path where template was saved
        """
        template_path = os.path.join(TEMPLATE_DIR, f"{template_name}.ini")
        
        # Add template metadata
        if "TEMPLATE" not in config.config:
            config.config["TEMPLATE"] = {}
        
        config.config["TEMPLATE"]["name"] = template_name
        
        # Save template
        return config.save(template_path)
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, str]]:
        """Get template metadata
        
        Args:
            template_name: Name of template
            
        Returns:
            Dictionary with template metadata or None if not found
        """
        template_config = self.load_template(template_name)
        if not template_config:
            return None
        
        if "TEMPLATE" in template_config.config:
            return dict(template_config.config["TEMPLATE"])
        
        return {"name": template_name}


def parse_aspect_ratio(ratio_str: str) -> Tuple[int, int]:
    """Parse aspect ratio string (e.g. "16:9") into width and height
    
    Args:
        ratio_str: String in format "width:height"
        
    Returns:
        Tuple of (width, height)
    """
    if ":" not in ratio_str:
        return (16, 9)  # Default to 16:9
        
    try:
        width, height = ratio_str.split(":")
        return (int(width), int(height))
    except (ValueError, TypeError):
        return (16, 9)  # Default to 16:9 on error
