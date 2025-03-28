# Auto-Slideshow V2 Templates

Auto-Slideshow V2 introduces a powerful template system that allows you to save and reuse your favorite slideshow settings. This documentation explains how to create, use, and customize templates.

## What is a Template?

A template is a saved configuration that defines the look and behavior of your slideshows. Templates can include settings for:

- Transitions effects and duration
- Video settings (duration, frame rate, aspect ratio)
- Text settings (title screens, captions)
- Audio settings
- Visual effects (Ken Burns, color adjustments, etc.)

Templates are stored as `.ini` files in the `v2/templates` directory.

## Using Templates

You can use templates in several ways:

### Command Line

```bash
# Use a template for your slideshow
python -m v2.main path/to/images -t template_name

# List available templates
python -m v2.main --list-templates
```

### Windows Batch Script

Run `run.bat` and select option 2: "Create a slideshow with a template"

## Creating Templates

### Method 1: Save Current Settings

The easiest way to create a template is to save the current settings:

```bash
# Create a slideshow with your desired settings and save as a template
python -m v2.main path/to/images --ken-burns --transition cube_rotation --color-effect vintage --save-template "my_template"
```

### Method 2: Create Template Via Batch Script

If you're on Windows, you can use the `run.bat` script, select option 6: "Create a new template" and follow the prompts.

### Method 3: Create Template Manually

Templates are standard INI files that you can create or edit manually. Create a file in the `v2/templates` directory with the extension `.ini` or `.cfg`.

## Template File Format

A template file follows this format:

```ini
[TEMPLATE]
name = My Template
description = Description of this template

[SETTINGS]
transition_duration = 0.8
video_duration = 60
frame_rate = 30
transition_type = random
output_aspect_ratio = 16:9
multithreading = true
ken_burns_enabled = true
ken_burns_intensity = 0.7

[TEXT]
title_enabled = true
title_font = Arial
title_size = 48
title_color = #FFFFFF
title_bg_color = #00000080
captions_enabled = true
captions_position = bottom
captions_font = Arial
captions_size = 32
captions_color = #FFFFFF
captions_bg_color = #00000080

[AUDIO]
audio_enabled = false
audio_volume = 1.0
audio_fade_in = 2.0
audio_fade_out = 2.0
sync_to_beats = false
loop_audio = true

[EFFECTS]
color_adjustment = vintage
vignette = true
picture_in_picture = false
```

## Template Examples

### Example 1: "Dynamic Story" Template

This template creates dynamic storytelling slideshows with Ken Burns effects and smooth transitions:

```ini
[TEMPLATE]
name = Dynamic Story
description = Create dynamic storytelling slideshows with pan and zoom effects

[SETTINGS]
transition_duration = 1.2
frame_rate = 30
transition_type = fade
ken_burns_enabled = true
ken_burns_intensity = 0.7

[TEXT]
title_enabled = true
title_font = Arial
title_size = 48
captions_enabled = true
captions_position = bottom

[AUDIO]
audio_enabled = true
audio_fade_in = 2.0
audio_fade_out = 3.0
sync_to_beats = false
```

### Example 2: "Social Media Quick" Template

Optimized for short social media content with fast transitions:

```ini
[TEMPLATE]
name = Social Media Quick
description = Fast-paced slideshow optimized for social media

[SETTINGS]
transition_duration = 0.3
frame_rate = 60
transition_type = random
output_aspect_ratio = 1:1

[TEXT]
title_enabled = false
captions_enabled = true
captions_font = Helvetica
captions_size = 36
captions_position = center

[AUDIO]
audio_enabled = true
audio_fade_in = 0.5
audio_fade_out = 0.5
volume_boost = 1.2
```

## Available Settings

### SETTINGS Section

| Option | Description | Default |
|--------|-------------|---------|
| `transition_duration` | Duration of transitions in seconds | 0.5 |
| `video_duration` | Total video duration in seconds | 59 |
| `frame_rate` | Frames per second | 25 |
| `transition_type` | Type of transition (name or "random") | random |
| `output_file` | Output filename | slideshow.mp4 |
| `output_aspect_ratio` | Aspect ratio in format "width:height" | 16:9 |
| `multithreading` | Use multiple CPU threads | true |
| `ken_burns_enabled` | Enable Ken Burns pan and zoom effect | false |
| `ken_burns_intensity` | Intensity of Ken Burns effect (0.0-1.0) | 0.5 |

### TEXT Section

| Option | Description | Default |
|--------|-------------|---------|
| `title_enabled` | Show title screen | false |
| `title_text` | Text for title screen | "" |
| `title_font` | Font for title | Arial |
| `title_size` | Font size for title | 48 |
| `title_color` | Text color in hex format | #FFFFFF |
| `title_bg_color` | Background color in hex format with optional alpha | #00000080 |
| `title_duration` | Duration of title screen in seconds | 3 |
| `captions_enabled` | Show captions | false |
| `captions_position` | Caption position (top, bottom, center) | bottom |
| `captions_font` | Font for captions | Arial |
| `captions_size` | Font size for captions | 32 |
| `captions_color` | Caption text color in hex format | #FFFFFF |
| `captions_bg_color` | Caption background color in hex with optional alpha | #00000080 |

### AUDIO Section

| Option | Description | Default |
|--------|-------------|---------|
| `audio_enabled` | Enable background audio | false |
| `audio_file` | Path to audio file | "" |
| `audio_volume` | Audio volume multiplier | 1.0 |
| `audio_fade_in` | Fade-in duration in seconds | 2.0 |
| `audio_fade_out` | Fade-out duration in seconds | 2.0 |
| `sync_to_beats` | Attempt to sync transitions to audio beats | false |
| `loop_audio` | Loop audio if shorter than video | true |

### EFFECTS Section

| Option | Description | Default |
|--------|-------------|---------|
| `color_adjustment` | Color effect (none, warm, cold, vintage, bw) | none |
| `vignette` | Add vignette effect to images | false |
| `picture_in_picture` | Enable picture-in-picture effect | false |
| `pip_position` | PiP position (top-left, top-right, bottom-left, bottom-right) | bottom-right |

## Transition Types

The following transition types are available:

- `fade`: Smooth cross-dissolve between images
- `wipe_left`: New image wipes in from right to left
- `wipe_right`: New image wipes in from left to right
- `wipe_up`: New image wipes in from bottom to top
- `wipe_down`: New image wipes in from top to bottom
- `zoom_in`: New image zooms in from center
- `zoom_out`: Current image zooms out to reveal new image
- `slide_left`: Current image slides left, new image enters from right
- `slide_right`: Current image slides right, new image enters from left
- `cube_rotation`: 3D cube rotation effect
- `door_open`: Current image splits and opens like doors
- `pixelate`: Current image pixelates out, then new image forms
- `radial_wipe`: Circular wipe from center
- `split_vertical`: Image splits vertically revealing the new image
- `page_curl`: Page curl effect like turning a book page

For a full list of available transitions, run:
```bash
python -m v2.main --list-transitions
```

## Tips for Creating Great Templates

1. **Consider the Content**: Different content benefits from different settings. Fast transitions work well for energetic content, while slower transitions suit contemplative subjects.

2. **Match Effects to Mood**: Color adjustments can significantly impact mood. Warm tones for nostalgic content, cold for more dramatic scenes, etc.

3. **Balance Duration**: For social media, aim for shorter durations (15-30 seconds). For presentations, 1-2 minutes is often appropriate.

4. **Test Different Transitions**: Some transitions work better with specific types of images. Experiment to find what works best for your content.

5. **Font Matters**: Choose fonts that match the tone of your slideshow. Script fonts for romantic/elegant, sans-serif for modern/clean.

6. **Create Multiple Variations**: Create different versions of your templates for different situations - quick versions for social media, detailed versions for presentations.
