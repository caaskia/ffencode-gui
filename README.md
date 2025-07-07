# FFEncode GUI

FFEncode GUI is a desktop application for batch video transcoding using FFmpeg. It provides a user-friendly interface to convert video files between different formats and codecs with customizable encoding parameters.

## Features

- **Batch Processing**: Convert multiple video files in a directory
- **Multiple Codecs Support**: Includes support for H.264, H.265 (HEVC), VP9, and more
- **Hardware Acceleration**: Supports hardware-accelerated encoding (NVIDIA NVENC, Intel VA-API)
- **Customizable Settings**: Adjust bitrates, codecs, and output formats
- **Watch Folder**: Automatically processes new files added to the input directory
- **Logging**: Detailed logging of the transcoding process

## Supported Input Formats
- MP4, MKV, AVI, 3GP, and other common video formats

## Supported Output Codecs
- H.264 (libx264, h264_vaapi)
- H.265/HEVC (hevc_nvenc, hevc_vaapi)
- VP9 (libvpx-vp9, vp9_vaapi)
- OPUS audio codec

## System Requirements
- Python 3.10 or higher
- FFmpeg
- NVIDIA GPU (for NVENC) or Intel/AMD GPU (for VA-API) - optional but recommended for hardware acceleration

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/caaskia/ffencode-gui.git
   cd ffencode-gui
   ```

2. Install `uv` (if not already installed):
   ```bash
   curl -sSf https://astral.sh/uv/install.sh | sh
   ```
   Or using pip:
   ```bash
   pip install uv
   ```

3. Create and activate a virtual environment with `uv`:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install dependencies using `uv`:
   ```bash
   uv pip sync requirements.txt --link-mode=copy
   ```
   
   Or to compile and sync from pyproject.toml:
   ```bash
   uv pip compile pyproject.toml -o requirements.txt
   uv pip sync requirements.txt --link-mode=copy
   ```

## Configuration

Edit the `config/config.toml` file to set default directories and encoding presets:

```toml
[directories]
work_dir = "/path/to/input/folder"
target_dir = "/path/to/output/folder"
post_dir = "/path/to/processed/files"

[encoding]
codec = "libx264"
video_bitrate = "750k"
audio_bitrate = "128k"
max_bitrate = "1500k"
container = "mkv"
```

## Usage

1. Launch the application:
   ```bash
   python main_ffencode.py
   ```

2. Configure the following settings in the GUI:
   - Source directory (where your input files are located)
   - Target directory (where encoded files will be saved)
   - Processed files directory (where successfully processed files will be moved)
   - Encoding parameters (codec, bitrates, etc.)

3. Click "Start" to begin the transcoding process
4. The application will automatically process all compatible video files in the source directory
5. Processed files will be moved to the processed files directory

## Building from Source

### Prerequisites

Make sure you have the required build tools installed:

```bash
# On Ubuntu/Debian
sudo apt update
sudo apt install patchelf
```

### Creating Standalone Executable with Nuitka

1. Ensure you're in the activated virtual environment with all dependencies installed.

2. Basic build (recommended):
   ```bash
   python -m nuitka --standalone --plugin-enable=pyside6 ./main_ffencode.py
   ```
   This will create a `main_ffencode.dist` directory containing the standalone executable.

3. Additional build options (advanced):
   - For better optimization (slower build):
     ```bash
     python -m nuitka --standalone --plugin-enable=pyside6 --follow-imports --show-progress ./main_ffencode.py
     ```
   
   - For static linking with Python (larger binary but more portable):
     ```bash
     python -m nuitka --standalone --plugin-enable=pyside6 --static-libpython=yes ./main_ffencode.py
     ```

4. The resulting executable will be in the `main_ffencode.dist` directory. You can run it directly:
   ```bash
   ./main_ffencode.dist/main_ffencode
   ```

### Distribution

To distribute your application, package the entire `main_ffencode.dist` directory. It contains all necessary dependencies to run the application on other machines with the same operating system.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Caaskia (caaskia@gmail.com)