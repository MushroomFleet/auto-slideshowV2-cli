@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Auto-Slideshow Generator V2
echo ========================================
echo.

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Virtual environment not found.
    echo Please run install.bat first.
    echo.
    pause
    exit /b 1
)
echo Done!
echo.

:: Options menu
echo What would you like to do?
echo.
echo 1. Create a basic slideshow
echo 2. Create a slideshow with a template
echo 3. Create a slideshow with custom options
echo 4. List available transitions
echo 5. List available templates
echo 6. Create a new template
echo 7. Exit
echo.

set /p CHOICE="Enter your choice (1-7): "

if "%CHOICE%"=="1" goto basic_slideshow
if "%CHOICE%"=="2" goto template_slideshow
if "%CHOICE%"=="3" goto custom_slideshow
if "%CHOICE%"=="4" goto list_transitions
if "%CHOICE%"=="5" goto list_templates
if "%CHOICE%"=="6" goto create_template
if "%CHOICE%"=="7" goto end

echo Invalid choice. Please try again.
pause
exit /b 1

:basic_slideshow
echo.
echo --- Create a Basic Slideshow ---
echo.

set /p FOLDER_PATH="Enter the path to your images folder: "

:: Validate folder path
if not exist "%FOLDER_PATH%" (
    echo Error: The folder "%FOLDER_PATH%" does not exist.
    echo Please check the path and try again.
    echo.
    pause
    exit /b 1
)

set /p OUTPUT_FILE="Enter the output filename (e.g., my_slideshow.mp4, press Enter for default): "
if "!OUTPUT_FILE!"=="" (
    set OUTPUT_OPTION=
) else (
    set OUTPUT_OPTION=-o "!OUTPUT_FILE!"
)

echo.
echo Creating basic slideshow...
echo.

python autoslideshow.py "%FOLDER_PATH%" %OUTPUT_OPTION%

goto end

:template_slideshow
echo.
echo --- Create a Slideshow with a Template ---
echo.

:: List available templates
python autoslideshow.py --list-templates

echo.
set /p TEMPLATE="Enter template name to use (or press Enter to cancel): "
if "!TEMPLATE!"=="" goto end

set /p FOLDER_PATH="Enter the path to your images folder: "

:: Validate folder path
if not exist "%FOLDER_PATH%" (
    echo Error: The folder "%FOLDER_PATH%" does not exist.
    echo Please check the path and try again.
    echo.
    pause
    exit /b 1
)

set /p OUTPUT_FILE="Enter the output filename (e.g., my_slideshow.mp4, press Enter for default): "
if "!OUTPUT_FILE!"=="" (
    set OUTPUT_OPTION=
) else (
    set OUTPUT_OPTION=-o "!OUTPUT_FILE!"
)

echo.
echo Creating slideshow with template !TEMPLATE!...
echo.

python autoslideshow.py "%FOLDER_PATH%" -t "!TEMPLATE!" %OUTPUT_OPTION%

goto end

:custom_slideshow
echo.
echo --- Create a Slideshow with Custom Options ---
echo.

set /p FOLDER_PATH="Enter the path to your images folder: "

:: Validate folder path
if not exist "%FOLDER_PATH%" (
    echo Error: The folder "%FOLDER_PATH%" does not exist.
    echo Please check the path and try again.
    echo.
    pause
    exit /b 1
)

set /p OUTPUT_FILE="Enter the output filename (e.g., my_slideshow.mp4, press Enter for default): "
if "!OUTPUT_FILE!"=="" (
    set OUTPUT_OPTION=
) else (
    set OUTPUT_OPTION=-o "!OUTPUT_FILE!"
)

set /p DURATION="Enter video duration in seconds (e.g., 60, press Enter for default): "
if "!DURATION!"=="" (
    set DURATION_OPTION=
) else (
    set DURATION_OPTION=-d !DURATION!
)

set /p AUDIO_FILE="Enter path to audio file (optional, press Enter to skip): "
if "!AUDIO_FILE!"=="" (
    set AUDIO_OPTION=
) else (
    set AUDIO_OPTION=-a "!AUDIO_FILE!"
)

set /p TITLE="Enter title text (optional, press Enter to skip): "
if "!TITLE!"=="" (
    set TITLE_OPTION=
) else (
    set TITLE_OPTION=--title "!TITLE!"
)

set /p CAPTIONS="Enable captions? (y/n, press Enter for default): "
if /i "!CAPTIONS!"=="y" (
    set CAPTIONS_OPTION=--captions
) else (
    set CAPTIONS_OPTION=
)

set /p KEN_BURNS="Enable Ken Burns effect? (y/n, press Enter for default): "
if /i "!KEN_BURNS!"=="y" (
    set KEN_BURNS_OPTION=--ken-burns
) else (
    set KEN_BURNS_OPTION=
)

python autoslideshow.py --list-transitions
echo.
set /p TRANSITION="Enter transition type (or 'random', press Enter for default): "
if "!TRANSITION!"=="" (
    set TRANSITION_OPTION=
) else (
    set TRANSITION_OPTION=--transition !TRANSITION!
)

echo.
echo Select color effect:
echo 1. None (default)
echo 2. Warm tones
echo 3. Cold tones
echo 4. Vintage/Sepia
echo 5. Black and White
echo.
set /p COLOR_EFFECT="Enter your choice (1-5, press Enter for default): "

if "!COLOR_EFFECT!"=="1" (
    set COLOR_OPTION=--color-effect none
) else if "!COLOR_EFFECT!"=="2" (
    set COLOR_OPTION=--color-effect warm
) else if "!COLOR_EFFECT!"=="3" (
    set COLOR_OPTION=--color-effect cold
) else if "!COLOR_EFFECT!"=="4" (
    set COLOR_OPTION=--color-effect vintage
) else if "!COLOR_EFFECT!"=="5" (
    set COLOR_OPTION=--color-effect bw
) else (
    set COLOR_OPTION=
)

set /p ASPECT_RATIO="Enter aspect ratio (e.g., 16:9, 4:3, 1:1, press Enter for default): "
if "!ASPECT_RATIO!"=="" (
    set ASPECT_RATIO_OPTION=
) else (
    set ASPECT_RATIO_OPTION=--aspect-ratio !ASPECT_RATIO!
)

echo.
echo Creating custom slideshow...
echo.

python autoslideshow.py "%FOLDER_PATH%" %OUTPUT_OPTION% %DURATION_OPTION% %AUDIO_OPTION% %TITLE_OPTION% %CAPTIONS_OPTION% %KEN_BURNS_OPTION% %TRANSITION_OPTION% %COLOR_OPTION% %ASPECT_RATIO_OPTION%

goto end

:list_transitions
echo.
echo --- Available Transitions ---
echo.

python autoslideshow.py --list-transitions

pause
goto end

:list_templates
echo.
echo --- Available Templates ---
echo.

python autoslideshow.py --list-templates

pause
goto end

:create_template
echo.
echo --- Create a New Template ---
echo.

set /p TEMPLATE_NAME="Enter name for the new template: "
if "!TEMPLATE_NAME!"=="" goto end

:: Let the user select settings for the template
echo.
echo Enter settings for template "!TEMPLATE_NAME!"
echo (Press Enter to keep defaults)
echo.

set /p DURATION="Enter video duration in seconds (e.g., 60): "
if "!DURATION!"=="" (
    set DURATION_OPTION=
) else (
    set DURATION_OPTION=-d !DURATION!
)

set /p TITLE="Enable title screen? (y/n): "
if /i "!TITLE!"=="y" (
    set TITLE_OPTION=--title "Demo Title"
) else (
    set TITLE_OPTION=
)

set /p CAPTIONS="Enable captions? (y/n): "
if /i "!CAPTIONS!"=="y" (
    set CAPTIONS_OPTION=--captions
) else (
    set CAPTIONS_OPTION=
)

set /p KEN_BURNS="Enable Ken Burns effect? (y/n): "
if /i "!KEN_BURNS!"=="y" (
    set KEN_BURNS_OPTION=--ken-burns
) else (
    set KEN_BURNS_OPTION=
)

python autoslideshow.py --list-transitions
echo.
set /p TRANSITION="Enter transition type (or 'random'): "
if "!TRANSITION!"=="" (
    set TRANSITION_OPTION=
) else (
    set TRANSITION_OPTION=--transition !TRANSITION!
)

echo.
echo Select color effect:
echo 1. None (default)
echo 2. Warm tones
echo 3. Cold tones
echo 4. Vintage/Sepia
echo 5. Black and White
echo.
set /p COLOR_EFFECT="Enter your choice (1-5): "

if "!COLOR_EFFECT!"=="1" (
    set COLOR_OPTION=--color-effect none
) else if "!COLOR_EFFECT!"=="2" (
    set COLOR_OPTION=--color-effect warm
) else if "!COLOR_EFFECT!"=="3" (
    set COLOR_OPTION=--color-effect cold
) else if "!COLOR_EFFECT!"=="4" (
    set COLOR_OPTION=--color-effect vintage
) else if "!COLOR_EFFECT!"=="5" (
    set COLOR_OPTION=--color-effect bw
) else (
    set COLOR_OPTION=
)

set /p ASPECT_RATIO="Enter aspect ratio (e.g., 16:9, 4:3, 1:1): "
if "!ASPECT_RATIO!"=="" (
    set ASPECT_RATIO_OPTION=
) else (
    set ASPECT_RATIO_OPTION=--aspect-ratio !ASPECT_RATIO!
)

echo.
echo Creating sample image for template preview...
echo.

:: Create a sample template by running with a dummy folder and saving as template
:: First create a temp directory with a sample image
mkdir temp_template_dir 2>nul

:: Create a dummy image if it doesn't exist
if not exist "temp_template_dir\sample.png" (
    echo Creating sample image...
    python -c "import numpy as np; import cv2; img = np.zeros((720, 1280, 3), dtype=np.uint8); img[:] = (0, 0, 255); cv2.putText(img, 'Sample Image', (480, 360), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3); cv2.imwrite('temp_template_dir/sample.png', img)"
)

echo.
echo Saving template !TEMPLATE_NAME!...
echo.

:: Run with --save-template to create the template
python autoslideshow.py "temp_template_dir" %DURATION_OPTION% %TITLE_OPTION% %CAPTIONS_OPTION% %KEN_BURNS_OPTION% %TRANSITION_OPTION% %COLOR_OPTION% %ASPECT_RATIO_OPTION% --save-template "!TEMPLATE_NAME!"

rmdir /s /q temp_template_dir 2>nul

pause
goto end

:end
echo.
echo Thank you for using Auto-Slideshow Generator V2!
echo.
endlocal
pause
