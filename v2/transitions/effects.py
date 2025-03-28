#!/usr/bin/env python3
"""
effects.py - Transition effects for Auto-Slideshow V2

This module contains all the transition effect implementations for
creating smooth transitions between images in slideshows.
"""

import numpy as np
import cv2
from typing import Callable, Dict, Tuple, Optional

# Type hint for transition function
TransitionFunc = Callable[[np.ndarray, np.ndarray, float], np.ndarray]

def fade(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Cross-fade transition between frames
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    return cv2.addWeighted(prev_frame, 1 - progress, next_frame, progress, 0)

def wipe_left(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Wipe from right to left
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    cut = int(w * progress)
    result = prev_frame.copy()
    result[:, :cut] = next_frame[:, :cut]
    return result

def wipe_right(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Wipe from left to right
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    cut = int(w * (1 - progress))
    result = prev_frame.copy()
    result[:, cut:] = next_frame[:, cut:]
    return result

def wipe_up(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Wipe from bottom to top
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    cut = int(h * progress)
    result = prev_frame.copy()
    result[:cut, :] = next_frame[:cut, :]
    return result

def wipe_down(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Wipe from top to bottom
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    cut = int(h * (1 - progress))
    result = prev_frame.copy()
    result[cut:, :] = next_frame[cut:, :]
    return result

def zoom_in(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Zoom in transition - next image starts small and grows
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    center_x, center_y = w // 2, h // 2
    
    # For zoom in, start with next_frame small and grow it
    zoom_factor = progress
    if zoom_factor < 0.1:  # Avoid too small scaling
        zoom_factor = 0.1
        
    # Size of the scaled image
    scaled_w = int(w * zoom_factor)
    scaled_h = int(h * zoom_factor)
    
    # Ensure minimum size
    scaled_w = max(scaled_w, 10)
    scaled_h = max(scaled_h, 10)
    
    # Resize next_frame
    scaled_next = cv2.resize(next_frame, (scaled_w, scaled_h))
    
    # Create result with prev_frame as background
    result = prev_frame.copy()
    
    # Calculate position to place the scaled image centered
    start_x = max(0, center_x - scaled_w // 2)
    start_y = max(0, center_y - scaled_h // 2)
    end_x = min(w, start_x + scaled_w)
    end_y = min(h, start_y + scaled_h)
    
    # Account for partial image placement near edges
    scaled_start_x = 0
    scaled_start_y = 0
    if start_x == 0:
        scaled_start_x = (scaled_w - (end_x - start_x)) // 2
    if start_y == 0:
        scaled_start_y = (scaled_h - (end_y - start_y)) // 2
        
    # Place scaled image onto result
    try:
        result[start_y:end_y, start_x:end_x] = scaled_next[
            scaled_start_y:scaled_start_y + (end_y - start_y), 
            scaled_start_x:scaled_start_x + (end_x - start_x)
        ]
    except ValueError:
        # Fallback to fade if dimensions don't align
        return fade(prev_frame, next_frame, progress)
    
    return result

def zoom_out(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Zoom out transition - current image shrinks revealing new image
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    center_x, center_y = w // 2, h // 2
    
    # For zoom out, start with prev_frame full size and shrink it
    zoom_factor = 1 - progress
    if zoom_factor < 0.1:  # Avoid too small scaling
        zoom_factor = 0.1
        
    # Size of the scaled image
    scaled_w = int(w * zoom_factor)
    scaled_h = int(h * zoom_factor)
    
    # Ensure minimum size
    scaled_w = max(scaled_w, 10)
    scaled_h = max(scaled_h, 10)
    
    # Resize prev_frame
    scaled_prev = cv2.resize(prev_frame, (scaled_w, scaled_h))
    
    # Create result with next_frame as background
    result = next_frame.copy()
    
    # Calculate position to place the scaled image centered
    start_x = max(0, center_x - scaled_w // 2)
    start_y = max(0, center_y - scaled_h // 2)
    end_x = min(w, start_x + scaled_w)
    end_y = min(h, start_y + scaled_h)
    
    # Account for partial image placement near edges
    scaled_start_x = 0
    scaled_start_y = 0
    if start_x == 0:
        scaled_start_x = (scaled_w - (end_x - start_x)) // 2
    if start_y == 0:
        scaled_start_y = (scaled_h - (end_y - start_y)) // 2
        
    # Place scaled image onto result
    try:
        result[start_y:end_y, start_x:end_x] = scaled_prev[
            scaled_start_y:scaled_start_y + (end_y - start_y), 
            scaled_start_x:scaled_start_x + (end_x - start_x)
        ]
    except ValueError:
        # Fallback to fade if dimensions don't align
        return fade(prev_frame, next_frame, progress)
    
    return result

def slide_left(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Slide left transition - current image slides left, new image enters from right
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    offset = int(w * progress)
    
    result = np.zeros_like(prev_frame)
    # Place part of prev_frame
    if offset < w:
        result[:, :w-offset] = prev_frame[:, offset:]
    
    # Place part of next_frame
    if offset > 0:
        result[:, w-offset:] = next_frame[:, :offset]
        
    return result

def slide_right(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Slide right transition - current image slides right, new image enters from left
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    offset = int(w * progress)
    
    result = np.zeros_like(prev_frame)
    # Place part of prev_frame
    if offset < w:
        result[:, offset:] = prev_frame[:, :w-offset]
    
    # Place part of next_frame
    if offset > 0:
        result[:, :offset] = next_frame[:, w-offset:]
        
    return result

def cube_rotation(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """3D cube rotation transition effect
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    
    # Simple approximation of 3D cube rotation using perspective transformation
    if progress < 0.5:
        # First half: rotate prev_frame out
        p = progress * 2  # Rescale to 0-1 for first half
        
        # Define the perspective transformation
        src_points = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        dst_points = np.float32([
            [w * p/2, h * p/2],
            [w - (w * p/2), h * p/2],
            [w - (w * p/2), h - (h * p/2)],
            [w * p/2, h - (h * p/2)]
        ])
        
        # Apply perspective transformation
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(prev_frame, matrix, (w, h))
        
        return warped
    else:
        # Second half: rotate next_frame in
        p = (progress - 0.5) * 2  # Rescale to 0-1 for second half
        p = 1 - p  # Invert so we start from compressed and expand out
        
        # Define the perspective transformation
        src_points = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        dst_points = np.float32([
            [w * p/2, h * p/2],
            [w - (w * p/2), h * p/2],
            [w - (w * p/2), h - (h * p/2)],
            [w * p/2, h - (h * p/2)]
        ])
        
        # Apply perspective transformation
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped = cv2.warpPerspective(next_frame, matrix, (w, h))
        
        return warped

def door_open(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Door opening transition effect - current image splits in middle and opens like doors
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    center_x = w // 2
    
    # Calculate the width of each moving door panel
    door_width = int(center_x * (1 - progress))
    
    # Create result with next_frame as background
    result = next_frame.copy()
    
    # If still in transition
    if door_width > 0:
        # Left door
        result[:, 0:door_width] = prev_frame[:, center_x-door_width:center_x]
        
        # Right door
        result[:, w-door_width:w] = prev_frame[:, center_x:center_x+door_width]
    
    return result

def pixelate(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Pixelate transition effect - prev image pixelates then next image forms
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    
    # Determine the pixel size based on transition progress
    if progress < 0.5:
        # First half - prev_frame pixelates
        p = progress * 2  # 0-0.5 -> 0-1
        pixel_size = int(max(2, min(64, p * 64)))  # Max pixel size 64
        
        # Pixelate by downscaling and upscaling
        temp = cv2.resize(prev_frame, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
        
        return pixelated
    else:
        # Second half - next_frame forms from pixels
        p = (progress - 0.5) * 2  # 0.5-1 -> 0-1
        p = 1 - p  # Invert so pixels get smaller
        pixel_size = int(max(2, min(64, p * 64)))  # Max pixel size 64
        
        # Pixelate by downscaling and upscaling
        temp = cv2.resize(next_frame, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
        
        return pixelated

def radial_wipe(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Radial wipe transition effect - wipe in a circular motion
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    
    # Create a mask for the transition
    mask = np.zeros((h, w), dtype=np.uint8)
    center = (w // 2, h // 2)
    radius = int(np.sqrt(w**2 + h**2) * progress)
    
    # Create circular mask
    cv2.circle(mask, center, radius, 255, -1)
    
    # Create result using the mask
    mask_3channel = cv2.merge([mask, mask, mask])
    prev_masked = cv2.bitwise_and(prev_frame, cv2.bitwise_not(mask_3channel))
    next_masked = cv2.bitwise_and(next_frame, mask_3channel)
    
    return cv2.add(prev_masked, next_masked)

def split_vertical(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Split vertical transition - current image splits in half, revealing new image
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    
    # Calculate the offset for each half
    offset = int(w * progress * 0.5)  # Each half moves by half the total progress
    
    # Create a result frame starting with the next image
    result = next_frame.copy()
    
    if offset > 0:
        # Copy left half of prev_frame (shifted left)
        left_width = w // 2
        result[:, 0:left_width-offset] = prev_frame[:, offset:left_width]
        
        # Copy right half of prev_frame (shifted right)
        result[:, left_width+offset:w] = prev_frame[:, left_width:w-offset]
    
    return result

def page_curl(prev_frame: np.ndarray, next_frame: np.ndarray, progress: float) -> np.ndarray:
    """Page curl transition effect - simplified approximation
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Resulting frame with transition applied
    """
    h, w = prev_frame.shape[:2]
    
    # Simplified page curl using shearing and masking
    # Create a mask based on progress
    mask = np.zeros((h, w), dtype=np.uint8)
    curl_x = int(w * progress)
    
    # Fill the mask with white where the next image should be visible
    cv2.rectangle(mask, (0, 0), (curl_x, h), 255, -1)
    
    # Add a gradient near the curl for a smoother effect
    gradient_width = int(w * 0.1)  # 10% of width for gradient
    if curl_x > gradient_width:
        for i in range(gradient_width):
            # Draw a vertical line with decreasing intensity
            intensity = 255 - int(255 * i / gradient_width)
            cv2.line(mask, (curl_x-i, 0), (curl_x-i, h), intensity, 1)
    
    # Create a sheared version of prev_frame to simulate curling
    shear_factor = 0.2 * progress
    M = np.float32([
        [1, shear_factor, 0],
        [0, 1, 0]
    ])
    sheared_prev = cv2.warpAffine(prev_frame, M, (w, h))
    
    # Create result using the mask
    mask_3channel = cv2.merge([mask, mask, mask])
    prev_masked = cv2.bitwise_and(sheared_prev, cv2.bitwise_not(mask_3channel))
    next_masked = cv2.bitwise_and(next_frame, mask_3channel)
    
    return cv2.add(prev_masked, next_masked)

# Dictionary mapping transition names to functions
TRANSITION_FUNCTIONS: Dict[str, TransitionFunc] = {
    "fade": fade,
    "wipe_left": wipe_left,
    "wipe_right": wipe_right,
    "wipe_up": wipe_up,
    "wipe_down": wipe_down,
    "zoom_in": zoom_in,
    "zoom_out": zoom_out,
    "slide_left": slide_left,
    "slide_right": slide_right,
    "cube_rotation": cube_rotation,
    "door_open": door_open,
    "pixelate": pixelate,
    "radial_wipe": radial_wipe,
    "split_vertical": split_vertical,
    "page_curl": page_curl,
}

# Dictionary mapping transition IDs to names (for backward compatibility)
TRANSITION_IDS: Dict[int, str] = {
    0: "fade",
    1: "wipe_left",
    2: "wipe_right",
    3: "wipe_up",
    4: "wipe_down",
    5: "zoom_in",
    6: "zoom_out",
    7: "slide_left",
    8: "slide_right",
    9: "cube_rotation",
    10: "door_open",
    11: "pixelate",
    12: "radial_wipe",
    13: "split_vertical",
    14: "page_curl",
}

def apply_transition(
    prev_frame: np.ndarray, 
    next_frame: np.ndarray, 
    transition: str or int, 
    progress: float
) -> np.ndarray:
    """Apply a transition effect between two frames
    
    Args:
        prev_frame: The current/outgoing frame
        next_frame: The new/incoming frame
        transition: Transition name or ID
        progress: Float between 0.0 and 1.0 indicating transition progress
        
    Returns:
        Frame with transition applied
    """
    # Convert transition ID to name if needed
    if isinstance(transition, int):
        if transition in TRANSITION_IDS:
            transition = TRANSITION_IDS[transition]
        else:
            # Default to fade for unknown transitions
            transition = "fade"
    
    # Get transition function
    if transition in TRANSITION_FUNCTIONS:
        transition_func = TRANSITION_FUNCTIONS[transition]
    else:
        # Default to fade for unknown transitions
        transition_func = TRANSITION_FUNCTIONS["fade"]
    
    # Apply transition
    return transition_func(prev_frame, next_frame, progress)

def get_random_transition() -> str:
    """Get a random transition name
    
    Returns:
        Random transition name
    """
    import random
    return random.choice(list(TRANSITION_FUNCTIONS.keys()))

def list_transitions() -> Dict[str, str]:
    """List all available transitions with descriptions
    
    Returns:
        Dictionary mapping transition names to descriptions
    """
    descriptions = {
        "fade": "Smooth cross-dissolve between images",
        "wipe_left": "New image wipes in from right to left",
        "wipe_right": "New image wipes in from left to right",
        "wipe_up": "New image wipes in from bottom to top",
        "wipe_down": "New image wipes in from top to bottom",
        "zoom_in": "New image zooms in from center",
        "zoom_out": "Current image zooms out to reveal new image",
        "slide_left": "Current image slides left, new image enters from right",
        "slide_right": "Current image slides right, new image enters from left",
        "cube_rotation": "3D cube rotation effect",
        "door_open": "Current image splits and opens like doors",
        "pixelate": "Current image pixelates out, then new image forms",
        "radial_wipe": "Circular wipe from center",
        "split_vertical": "Image splits vertically revealing the new image",
        "page_curl": "Page curl effect like turning a book page"
    }
    
    # Return only descriptions for transitions that are actually implemented
    return {k: descriptions.get(k, "No description available") 
            for k in TRANSITION_FUNCTIONS.keys()}
