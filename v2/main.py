#!/usr/bin/env python3
"""
Auto-Slideshow Generator V2

This is the main entry point for the Auto-Slideshow Generator V2 CLI application.
"""

import os
import sys
import argparse
import time
from typing import Optional, Dict, Any, List

from .core.slideshow import SlideshowGenerator
from .utils.config import ConfigManager, TemplateManager
from .transitions.effects import list_transitions

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Auto-Slideshow Generator V2 - Create beautiful slideshows from your images",
        epilog="Example: autoslideshow path/to/images -o my_slideshow.mp4 -t dynamic_story"
    )
    
    # Required arguments
    parser.add_argument(
        "folder", 
        help="Folder containing the images"
    )
    
    # Optional arguments
    parser.add_argument(
        "-o", "--output", 
        help="Output file path (overrides config)"
    )
    
    parser.add_argument(
        "-c", "--config", 
        default="config.cfg", 
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "-t", "--template", 
        help="Use a specific template (e.g., 'dynamic_story', 'social_media')"
    )
    
    parser.add_argument(
        "-d", "--duration", 
        type=float, 
        help="Total video duration in seconds"
    )
    
    parser.add_argument(
        "-a", "--audio", 
        help="Path to audio file to use as background music"
    )
    
    parser.add_argument(
        "--title", 
        help="Add a title screen with the specified text"
    )
    
    parser.add_argument(
        "--captions", 
        action="store_true", 
        help="Enable automatic captions based on filenames"
    )
    
    parser.add_argument(
        "--transition", 
        help="Specific transition type to use (or 'random')"
    )
    
    parser.add_argument(
        "--list-transitions", 
        action="store_true", 
        help="List all available transition effects"
    )
    
    parser.add_argument(
        "--list-templates", 
        action="store_true", 
        help="List all available templates"
    )
    
    parser.add_argument(
        "--save-template", 
        help="Save current settings as a new template with the specified name"
    )
    
    parser.add_argument(
        "--ken-burns", 
        action="store_true", 
        help="Enable Ken Burns effect"
    )
    
    parser.add_argument(
        "--aspect-ratio", 
        help="Specify output aspect ratio (e.g., '16:9', '4:3', '1:1')"
    )
    
    parser.add_argument(
        "--color-effect", 
        choices=["none", "warm", "cold", "vintage", "bw"], 
        help="Apply color effect to images"
    )
    
    return parser.parse_args()

def list_available_transitions():
    """Print a list of all available transition effects"""
    transitions = list_transitions()
    
    print("\nAvailable Transition Effects:")
    print("-----------------------------")
    
    for name, description in transitions.items():
        print(f"{name}: {description}")
    
    print("\nUse with --transition option (e.g., --transition cube_rotation)")
    print("Use 'random' to select a random transition for each image")

def list_available_templates():
    """Print a list of all available templates"""
    template_manager = TemplateManager()
    templates = template_manager.list_templates()
    
    if not templates:
        print("\nNo templates found.")
        print(f"Templates directory: {os.path.abspath(template_manager.TEMPLATE_DIR)}")
        return
    
    print("\nAvailable Templates:")
    print("-------------------")
    
    for template_name in templates:
        # Get template info
        info = template_manager.get_template_info(template_name)
        description = info.get("description", "No description available")
        
        print(f"{template_name}: {description}")
    
    print("\nUse with --template option (e.g., --template dynamic_story)")

def update_config_from_args(config: ConfigManager, args: argparse.Namespace):
    """Update configuration based on command-line arguments
    
    Args:
        config: Configuration manager to update
        args: Parsed command-line arguments
    """
    # Update output file if specified
    if args.output:
        config.set_value("SETTINGS", "output_file", args.output)
    
    # Update video duration if specified
    if args.duration:
        config.set_value("SETTINGS", "video_duration", str(args.duration))
    
    # Update transition type if specified
    if args.transition:
        config.set_value("SETTINGS", "transition_type", args.transition)
    
    # Update aspect ratio if specified
    if args.aspect_ratio:
        config.set_value("SETTINGS", "output_aspect_ratio", args.aspect_ratio)
    
    # Update Ken Burns effect if specified
    if args.ken_burns:
        config.set_value("SETTINGS", "ken_burns_enabled", "true")
    
    # Update color effect if specified
    if args.color_effect:
        config.set_value("EFFECTS", "color_adjustment", args.color_effect)
    
    # Update audio settings if specified
    if args.audio:
        config.set_value("AUDIO", "audio_enabled", "true")
        config.set_value("AUDIO", "audio_file", args.audio)
    
    # Update title settings if specified
    if args.title:
        config.set_value("TEXT", "title_enabled", "true")
        config.set_value("TEXT", "title_text", args.title)
    
    # Update captions if specified
    if args.captions:
        config.set_value("TEXT", "captions_enabled", "true")

def save_template(config: ConfigManager, template_name: str) -> bool:
    """Save current configuration as a template
    
    Args:
        config: Configuration manager with current settings
        template_name: Name for the new template
        
    Returns:
        True if the template was saved successfully
    """
    try:
        template_manager = TemplateManager()
        template_path = template_manager.save_template(template_name, config)
        
        print(f"\nTemplate '{template_name}' saved successfully.")
        print(f"Template path: {template_path}")
        
        return True
    except Exception as e:
        print(f"Error saving template: {e}")
        return False

def print_progress_bar(progress: float, status: str = ""):
    """Print a progress bar to the console
    
    Args:
        progress: Progress percentage (0-100)
        status: Status message
    """
    width = 40  # Width of the progress bar
    
    # Calculate number of filled positions in the bar
    filled = int(width * progress / 100)
    
    # Create the progress bar
    bar = '#' * filled + '-' * (width - filled)
    
    # Print the progress bar
    print(f"\r[{bar}] {progress:.1f}% {status}", end='', flush=True)

def main():
    """Main entry point for the application"""
    # Parse arguments
    args = parse_arguments()
    
    # Handle special commands
    if args.list_transitions:
        list_available_transitions()
        return 0
    
    if args.list_templates:
        list_available_templates()
        return 0
    
    # Verify folder exists
    if not os.path.isdir(args.folder):
        print(f"Error: Folder does not exist: {args.folder}")
        return 1
    
    # Load configuration
    config_path = args.config
    template_manager = TemplateManager()
    
    if args.template:
        # Load template if specified
        template_config = template_manager.load_template(args.template)
        if template_config:
            config = template_config
            print(f"Using template: {args.template}")
        else:
            print(f"Warning: Template '{args.template}' not found. Using default configuration.")
            config = ConfigManager(config_path if os.path.exists(config_path) else None)
    else:
        # Load configuration from file
        config = ConfigManager(config_path if os.path.exists(config_path) else None)
    
    # Update configuration from command-line arguments
    update_config_from_args(config, args)
    
    # Save as template if requested
    if args.save_template:
        save_template(config, args.save_template)
    
    # Create slideshow generator
    slideshow_generator = SlideshowGenerator(config)
    
    # Register progress callback
    slideshow_generator.set_progress_callback(print_progress_bar)
    
    print(f"\nCreating slideshow from images in {args.folder}")
    print(f"Output file: {slideshow_generator.output_file}")
    
    # Record start time
    start_time = time.time()
    
    # Create slideshow
    result = slideshow_generator.create_slideshow(args.folder)
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    if result:
        print(f"\nSlideshow created successfully in {minutes}m {seconds}s.")
        return 0
    else:
        print(f"\nFailed to create slideshow.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
