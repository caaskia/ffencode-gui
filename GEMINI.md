# Technical Overview: ffencode-gui

This document provides a detailed technical breakdown of the `ffencode-gui` project components for development and maintenance purposes.

## Technologies

### Core Technologies
- **Python**: Version 3.11+ is required for running the application.
- **uv**: Ultra-fast Python package installer and resolver.
- **PySide6**: Used for building the cross-platform GUI application.
- **FFmpeg**: Handles all video/audio transcoding operations.
- **Nuitka**: Used for compiling Python code into standalone executables.

### Development Tools
- **TOML**: Configuration file format for application settings.
- **Git**: Version control system.
- **Linux**: Primary development and deployment platform.

### Python Libraries
- **ffmpy**: Python wrapper for FFmpeg command-line interface.
- **python-ffmpeg**: Additional FFmpeg integration tools.
- **toml**: Library for parsing TOML configuration files.
- **subprocess**: Used for executing FFmpeg commands.
- **logging**: For application logging and debugging.
- **pathlib**: For cross-platform path handling.
- **os**: For file system operations.

## Project Architecture

The application is built using Python and the PySide6 framework for the graphical user interface. It follows a modular structure, separating the UI logic from the core transcoding functionality.

- **UI Layer**: Managed by `service/ui_service.py`, which handles all user interactions and window management.
- **Business Logic Layer**: The core transcoding work is performed in a separate thread managed by `service/conv_service.py` to keep the UI responsive.
- **Utilities**: Helper functions for FFmpeg command generation, file operations, and configuration management are located in the `utils/` directory.
- **Configuration**: Application settings are externalized to a `config.toml` file.

## Component Breakdown

### 1. `main_ffencode.py`

- **Purpose**: The main entry point of the application.
- **Functionality**:
  - Initializes the `QApplication` instance.
  - Creates an instance of `MyApplication` from `ui_service.py`.
  - Displays the main window.
  - Starts the Qt event loop.

### 2. `service/ui_service.py`

- **Class**: `MyApplication(QMainWindow, Ui_Form)`
- **Purpose**: Acts as the main controller for the application's UI. It connects user actions (like button clicks) to the corresponding backend logic.
- **Key Responsibilities**:
  - **Initialization**: Sets up the UI from the `Ui_Form` class (generated from a `.ui` file) and initializes class variables.
  - **Signal/Slot Connections**: Connects widget signals (e.g., `clicked`, `valueChanged`) to application slots (handler methods).
    - `workDir_button`, `targetDir_button`, `postDir_button`: Open file dialogs to select directories.
    - `start_button`: Emits the `sig_start_transcoding` signal to begin the transcoding process.
    - `stop_button`: Emits the `sig_stop_transcoding` signal to halt the process.
  - **Configuration Management**: Calls `load_config()` to load settings from `config/config.toml` on startup.
  - **State Management**: Enables/disables widgets (like the `stop_button`) based on the application's state (e.g., transcoding active/inactive).
  - **Event Handling**: Contains methods like `event_prepare_start` and `stop_transcoding` that prepare for and manage the lifecycle of the `TranscodingThread`.
  - **Output Display**: Connects the `sig_print` signal to the `update_output` method to display logs and status messages in the UI's text area.

### 3. `service/conv_service.py`

- **Class**: `TranscodingThread(QThread)`
- **Purpose**: Executes the long-running transcoding tasks in a background thread to prevent the GUI from freezing.
- **Key Responsibilities**:
  - **Initialization**: Receives necessary parameters like directories, FFmpeg options, and the watch folder polling period.
  - **Main Loop (`run` method)**: Contains a `while` loop that periodically scans the `workDir` for new video files.
  - **File Discovery**: Uses `getSendFiles` from `utils_ffConv.py` to find valid video files to process.
  - **Transcoding**: For each file, it calls `ffConv` from `utils_ffConv.py` to execute the FFmpeg transcoding command.
  - **File Management**: After successful transcoding, it moves the original file to the `postDir` using `move_file`.
  - **Communication**: Uses Qt signals (`sig_show_message`, `sig_replace_message`) to send status updates and log messages back to the main UI thread.
  - **Termination**: The `transcoding_active` flag can be set to `False` to gracefully exit the `while` loop and stop the thread.

### 4. `utils/utils_ffConv.py`

- **Purpose**: Contains the core logic for finding files and constructing/executing FFmpeg commands.
- **Key Functions**:
  - `getSendFiles(workDir)`: Scans a directory, filters for specific video file extensions (e.g., `.mp4`, `.mkv`), and returns a list of files to be processed.
  - `ffConv(inFile, dirOut, ffOptions)`: This is the heart of the transcoding logic. It constructs a complex FFmpeg command line based on the input file, output directory, and a tuple of `ffOptions` (codec, bitrates, container). It then executes this command using `subprocess`.

### 5. `utils/utils_ffmpeg.py`

- **Purpose**: Provides helper functions related to file system operations.
- **Key Functions**:
  - `move_file(source_path, destination_path)`: Moves a file from the source to the destination, used for archiving processed files.

### 6. `utils/utils_toml.py`

- **Purpose**: Handles reading and parsing of the TOML configuration file.
- **Key Functions**:
  - `load_toml(config_path)`: Reads the `.toml` file and returns a dictionary.
  - `get_config_value(...)`: Safely retrieves a value from the configuration dictionary.

### 7. `config/config.toml`

- **Purpose**: Stores user-configurable settings to avoid hardcoding paths and encoding parameters.
- **Structure**:
  - `[directories]`: Defines default paths for `work_dir`, `target_dir`, and `post_dir`.
  - `[encoding]`: Defines default FFmpeg options like `codec`, `video_bitrate`, etc.

## Development Workflow

1.  **Setup**: Use `uv` to create a virtual environment and install dependencies from `requirements.txt` as described in `README.md`.
2.  **Running**: Execute `python main_ffencode.py` to launch the application.
3.  **Building**: Use Nuitka to compile a standalone executable as per the `README.md` instructions.

## Useful Links

* [Documentation PySide6](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html)
* [Documentation PySide6 tutorial](https://www.pythonguis.com/pyside6-tutorial/)
* [Documentation ffmpy](https://github.com/Ch00k/ffmpy)
* [Documentation ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
* [Documentation Pydantic](https://docs.pydantic.dev/)
