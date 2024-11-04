import os
from pathlib import Path

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from service.conv_service import TranscodingThread
from service.transcoding_ui import Ui_Form
from utils.utils_toml import load_toml, get_config_value


class MyApplication(QMainWindow, Ui_Form):
    sig_start_transcoding = Signal()
    sig_stop_transcoding = Signal()
    sig_show_message = Signal(str)
    sig_print = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.workDir = None
        self.targetDir = None
        self.postDir = None
        self.ffOptions = None
        self.period = None
        self.transcoding_thread = None

        # Connect signals
        self.sig_print.connect(self.update_output)
        self.workDir_button.clicked.connect(self.select_work_dir)
        self.targetDir_button.clicked.connect(self.select_target_dir)
        self.postDir_button.clicked.connect(self.select_post_dir)

        self.start_button.clicked.connect(self.sig_start_transcoding.emit)
        self.sig_start_transcoding.connect(self.event_prepare_start)

        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.sig_stop_transcoding.emit)
        self.sig_stop_transcoding.connect(self.stop_transcoding)

        self.periodSlider.valueChanged.connect(self.update_period_edit)
        self.periodEdit.textChanged.connect(self.update_period_slider)

        # Загрузка конфигурации
        self.load_config()

    def load_config(self):
        config_path = Path(__file__).resolve().parent.parent / "config/config.toml"
        main_config = load_toml(config_path)
        app_config = main_config.get("app", {})
        dict_config = main_config.get("dict", {})

        self.workDir = Path(get_config_value(app_config, "workDir", ""))
        self.workDir_label.setText(str(self.workDir))

        self.targetDir = Path(get_config_value(app_config, "targetDir", ""))
        self.targetDir_label.setText(str(self.targetDir))

        self.postDir = Path(
            get_config_value(
                app_config, "postDir", os.path.join(self.workDir, "converted")
            )
        )
        self.postDir_label.setText(str(self.postDir))

        self.period = get_config_value(app_config, "period", 60)
        self.periodSlider.setValue(self.period)
        self.periodEdit.setText(str(self.period))

        self.init_combo_box(
            self.resize_combo,
            dict_config.get("size", ["1080p", "720p", "576p", "480p", "360p", "240p"]),
            app_config.get("size", "480p"),
        )
        self.init_combo_box(
            self.fCodec_combo,
            dict_config.get("fCodec", ["libx264", "libx265"]),
            app_config.get("fCodec", "libx264"),
        )
        self.init_combo_box(
            self.VBRate_combo,
            dict_config.get("VBRate", ["500k"]),
            app_config.get("VBRate", "500k"),
        )
        self.init_combo_box(
            self.minVBR_combo,
            dict_config.get("minVBR", ["100k"]),
            app_config.get("minVBR", "100k"),
        )
        self.init_combo_box(
            self.maxVBR_combo,
            dict_config.get("maxVBR", ["1000k"]),
            app_config.get("maxVBR", "1000k"),
        )
        self.init_combo_box(
            self.ext_combo,
            dict_config.get("ext", ["mp4", "mkv", "avi"]),
            app_config.get("ext", "mp4"),
        )

    def init_combo_box(self, combo, items, default):
        combo.clear()
        combo.addItems(items)
        combo.setCurrentText(default)

    def select_work_dir(self):
        workDir = QFileDialog.getExistingDirectory(self, "Select Work Directory")
        if workDir:
            self.workDir_label.setText(workDir)
            self.workDir = Path(workDir)
        else:
            self.print_to_output("No work directory selected.")

    def select_target_dir(self):
        targetDir = QFileDialog.getExistingDirectory(self, "Выберите целевой каталог")
        if targetDir:
            self.targetDir_label.setText(targetDir)
            self.targetDir = Path(targetDir)

    def select_post_dir(self):
        postDir = QFileDialog.getExistingDirectory(
            self, "Выберите папку для перемещения оригинала"
        )
        if postDir:
            self.postDir_label.setText(postDir)
            self.postDir = Path(postDir)

    def update_period_edit(self, value):
        self.period = value
        self.periodEdit.setText(str(value))

    def update_period_slider(self, text):
        try:
            value = int(text)
            self.period = value
            self.periodSlider.setValue(value)
        except ValueError:
            self.print_to_output("Invalid input! Please enter a numeric value")

    def print_to_output(self, text):
        self.sig_print.emit(text)

    @Slot(str)
    def update_output(self, text):
        self.output_pane.appendPlainText(text)
        cursor = self.output_pane.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_pane.setTextCursor(cursor)
        self.output_pane.repaint()

    @Slot(str, bool)
    def replace_output(self, text, replace=False):
        cursor = self.output_pane.textCursor()

        # Move cursor to the end of the document
        cursor.movePosition(QTextCursor.MoveOperation.End)

        if replace:
            # Move to the start of the last line
            cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()  # Clear the line's content

        # Insert new text at the cursor's position
        cursor.insertText(text)
        cursor.movePosition(QTextCursor.MoveOperation.End)  # Move the cursor to the end
        self.output_pane.setTextCursor(cursor)
        self.output_pane.repaint()

    def event_prepare_start(self):
        if not self.workDir or not self.targetDir:
            self.print_to_output("Please select directories.")
            QMessageBox.critical(
                self, "Error", "Please select both work and target directories."
            )
            return

        self.ffOptions = (
            self.fCodec_combo.currentText(),
            self.VBRate_combo.currentText(),
            self.minVBR_combo.currentText(),
            self.maxVBR_combo.currentText(),
            self.ext_combo.currentText(),
            self.resize_combo.currentText(),
        )
        self.start_transcoding()

    def start_transcoding(self):
        if self.transcoding_thread and self.transcoding_thread.isRunning():
            self.sig_print.emit("Transcoding is already running.")
            return

        self.transcoding_thread = TranscodingThread(
            self.workDir, self.targetDir, self.postDir, self.ffOptions, self.period
        )

        self.transcoding_thread.sig_show_message.connect(self.print_to_output)
        self.transcoding_thread.sig_replace_message.connect(self.replace_output)
        self.transcoding_thread.sig_stop.connect(self.on_transcoding_stopped)

        self.transcoding_thread.start()  # Start the transcoding thread
        self.start_button.setStyleSheet("color: green")
        self.start_button.setText("Transcoding in process...")

        self.stop_button.setStyleSheet("color: black")
        self.stop_button.setEnabled(True)
        self.sig_print.emit("Transcoding started...")

    def stop_transcoding(self):
        if self.transcoding_thread:
            self.stop_button.setStyleSheet("color: red")
            self.stop_button.setText("Stopping in process")

            self.start_button.setStyleSheet("color: gray")
            self.start_button.setEnabled(False)

            self.sig_print.emit("Stopping transcoding...")
            self.transcoding_thread.stop()  # Stop the thread safely
        else:
            self.sig_print.emit("No transcoding thread to stop.")

    def on_transcoding_stopped(self):
        self.sig_print.emit("Transcoding has been stopped.")

        self.start_button.setStyleSheet("color: black")
        self.start_button.setText("Start transcoding")
        self.start_button.setEnabled(True)

        self.stop_button.setStyleSheet("color: gray")
        self.stop_button.setText("Stop transcoding")
        self.stop_button.setEnabled(False)

        self.transcoding_thread = None  # Reset the thread reference
