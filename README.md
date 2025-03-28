# 🎬 Auto-Slideshow Generator V2 🎬

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Create stunning slideshows from your image collections with advanced features and customization options! Auto-Slideshow V2 is a powerful command-line tool that transforms your images into professional-looking videos with smooth transitions, effects, audio support, and much more.

## 🌟 What's New in V2

Auto-Slideshow V2 has been completely redesigned with a modular architecture and many new features:

- 🖼️ **Custom Aspect Ratios**: Support for various output formats (16:9, 4:3, 1:1 for social media)
- 🎵 **Audio Integration**: Add background music with auto fade-in/out and beat detection
- 🔠 **Text Capabilities**: Add title screens and automatic captions
- 🎞️ **More Transitions**: 6 new transition effects (15 total including cube rotation, page curl, pixelate)
- 🌈 **Color Effects**: Apply warm, cold, vintage, or B&W filters to your images
- 🔄 **Ken Burns Effect**: Dynamic pan and zoom for more engaging slideshows
- 💾 **Progress Recovery**: Resume interrupted slideshow creation
- ⚡ **Performance Improvements**: Optional multi-threading support
- 📋 **Template System**: Save and reuse your favorite settings

## 📋 Requirements

- 🐍 Python 3.6 or higher
- 📚 OpenCV, NumPy, Pillow, Librosa, and SoundFile libraries

## 🔧 Installation

### Windows

Simply run the installation batch script:

```bash
install.bat
```

This will create a virtual environment, install all dependencies, and set up the application.

### Manual Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Using the interactive launcher (Windows)

Run the interactive batch script:

```bash
run.bat
```

This will guide you through creating slideshows with different options.

### Command Line Usage

```bash
# Basic usage
python autoslideshow.py path/to/your/images

# Specify output file
python autoslideshow.py path/to/your/images -o my_slideshow.mp4

# Use a template
python autoslideshow.py path/to/your/images -t dynamic_story

# Create a custom slideshow
python autoslideshow.py path/to/your/images --title "My Vacation" --captions --ken-burns --transition fade --color-effect vintage
```

## ⚙️ Configuration

Auto-Slideshow V2 supports highly customizable options:

### Command-Line Options

| Option | Description |
|--------|-------------|
| `-o, --output` | Output file path |
| `-c, --config` | Path to configuration file |
| `-t, --template` | Use a specific template |
| `-d, --duration` | Total video duration in seconds |
| `-a, --audio` | Path to audio file for background music |
| `--title` | Add a title screen with the specified text |
| `--captions` | Enable automatic captions based on filenames |
| `--transition` | Specific transition type to use |
| `--ken-burns` | Enable Ken Burns effect |
| `--aspect-ratio` | Specify output aspect ratio (e.g., "16:9", "1:1") |
| `--color-effect` | Apply color effect (none, warm, cold, vintage, bw) |
| `--list-transitions` | List all available transition effects |
| `--list-templates` | List all available templates |
| `--save-template` | Save current settings as a template |

## 🎛️ Template System

Auto-Slideshow V2 includes a powerful template system that allows you to save and reuse your favorite settings.

### Included Templates

- **Dynamic Story**: Perfect for creating narrative slideshows with Ken Burns effects and smooth transitions
- **Social Media Quick**: Optimized for short social media content with fast transitions and square format

### Creating Custom Templates

You can create your own custom templates:

```bash
# Create slideshow with your desired settings and save as a template
python autoslideshow.py path/to/images --ken-burns --transition cube_rotation --duration 60 --save-template "my_template"

# Use your template
python autoslideshow.py path/to/images -t my_template
```

For more details on creating templates, see the [Templates Documentation](v2/docs/templates.md).

## 🌟 Features

### Transitions

Auto-Slideshow V2 supports 15 different transition effects:

- **Fade**: Smooth cross-dissolve
- **Wipes**: Left, right, up, down
- **Zooms**: Zoom in, zoom out
- **Slides**: Slide left, slide right
- **Advanced Effects**: Cube rotation, door open, pixelate, radial wipe, split vertical, page curl

### Audio Support

Add background music to your slideshows:

- Automatic looping for short audio files
- Fade in/out effects
- Experimental beat synchronization 

### Text Features

- **Title Screens**: Add attractive title screens to introduce your slideshow
- **Captions**: Automatically generate captions from filenames
- **Font Selection**: Use various system fonts 

### Visual Effects

- **Ken Burns Effect**: Dynamic pan and zoom movement for images
- **Color Adjustments**: Apply warm, cold, vintage, or black & white filters
- **Vignette Effect**: Add subtle vignette for a more professional look

## 🛠️ Advanced Usage Examples

### Create a 30-second slideshow for Instagram:

```bash
python autoslideshow.py my_vacation_photos -o instagram.mp4 -d 30 --aspect-ratio 1:1 --transition slide_right --captions --color-effect warm
```

### Create a presentation slideshow with title:

```bash
python autoslideshow.py presentation_images -o presentation.mp4 --title "Quarterly Results" --transition fade --ken-burns
```

### Add background music:

```bash
python autoslideshow.py wedding_photos -o wedding.mp4 -a background_music.mp3
```

## 🔧 Recent Updates

- Fixed installation issues by simplifying the dependency installation process
- Resolved a type mismatch in the slideshow generator initialization
- Updated command interface to use a more straightforward entry point

## 📚 Documentation

- [Template System Documentation](v2/docs/templates.md)

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ by the Auto-Slideshow Team

Enjoy creating beautiful slideshows with your images! 🎬✨
