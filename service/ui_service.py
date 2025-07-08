import os
from pathlib import Path
import asyncio

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from service.conv_service import TranscodingThread
from service.transcoding_ui import Ui_Form
from service.db_service import get_active_config, update_config
from models.models_pydantic import FFEncodeConfigPydantic


class MyApplication(QMainWindow, Ui_Form):
    sig_start_transcoding = Signal()
    sig_stop_transcoding = Signal()
    sig_show_message = Signal(str)
    sig_print = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.config: FFEncodeConfigPydantic = None
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
        asyncio.create_task(self.load_config_from_db())

    async def load_config_from_db(self):
        self.config = await get_active_config()

        self.workDir = Path(self.config.workDir)
        self.workDir_label.setText(str(self.workDir))

        self.targetDir = Path(self.config.targetDir)
        self.targetDir_label.setText(str(self.targetDir))

        self.postDir = Path(self.config.postDir)
        self.postDir_label.setText(str(self.postDir))

        self.period = self.config.period
        self.periodSlider.setValue(self.period)
        self.periodEdit.setText(str(self.period))

        # For now, we'll keep the dict_config part as it was, assuming it's for UI choices
        # In the future, this could also be moved to the database
        config_path = Path(__file__).resolve().parent.parent / "config/config.toml"
        import toml

        main_config = toml.load(config_path)
        dict_config = main_config.get("dict", {})

        self.init_combo_box(
            self.resize_combo,
            dict_config.get("size", ["1080p", "720p", "576p", "480p", "360p", "240p"]),
            self.config.size,
        )
        self.init_combo_box(
            self.fCodec_combo,
            dict_config.get("fCodec", ["libx264", "libx265"]),
            self.config.fcodec,
        )
        self.init_combo_box(
            self.VBRate_combo,
            dict_config.get("VBRate", ["500k"]),
            self.config.VBRate,
        )
        self.init_combo_box(
            self.minVBR_combo,
            dict_config.get("minVBR", ["100k"]),
            self.config.minVBR,
        )
        self.init_combo_box(
            self.maxVBR_combo,
            dict_config.get("maxVBR", ["1000k"]),
            self.config.maxVBR,
        )
        self.init_combo_box(
            self.ext_combo,
            dict_config.get("ext", ["mp4", "mkv", "avi"]),
            self.config.ext,
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
            self.config.workDir = workDir
            asyncio.create_task(update_config(self.config))
        else:
            self.print_to_output("No work directory selected.")

    def select_target_dir(self):
        targetDir = QFileDialog.getExistingDirectory(self, "Выберите целевой каталог")
        if targetDir:
            self.targetDir_label.setText(targetDir)
            self.targetDir = Path(targetDir)
            self.config.targetDir = targetDir
            asyncio.create_task(update_config(self.config))

    def select_post_dir(self):
        postDir = QFileDialog.getExistingDirectory(
            self, "Выберите папку для перемещени�� оригинала"
        )
        if postDir:
            self.postDir_label.setText(postDir)
            self.postDir = Path(postDir)
            self.config.postDir = postDir
            asyncio.create_task(update_config(self.config))

    def update_period_edit(self, value):
        self.period = value
        self.periodEdit.setText(str(value))
        self.config.period = value
        asyncio.create_task(update_config(self.config))

    def update_period_slider(self, text):
        try:
            value = int(text)
            self.period = value
            self.periodSlider.setValue(value)
            self.config.period = value
            asyncio.create_task(update_config(self.config))
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
            cursor.movePosition(
                QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor
            )
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

        self.config.fcodec = self.fCodec_combo.currentText()
        self.config.VBRate = self.VBRate_combo.currentText()
        self.config.minVBR = self.minVBR_combo.currentText()
        self.config.maxVBR = self.maxVBR_combo.currentText()
        self.config.ext = self.ext_combo.currentText()
        self.config.size = self.resize_combo.currentText()
        asyncio.create_task(update_config(self.config))

        self.ffOptions = (
            self.config.fcodec,
            self.config.VBRate,
            self.config.minVBR,
            self.config.maxVBR,
            self.config.ext,
            self.config.size,
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
