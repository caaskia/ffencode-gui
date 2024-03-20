import os
import sys
from pathlib import Path

# from PySide6.QtCore import QObject, pyqtSignal
from PySide6.QtCore import Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from transcoding_ui import Ui_Form

from utils_toml import load_toml
from utils_task import TranscodingThread


class MyApplication(QMainWindow, Ui_Form):
    start_transcoding_signal = Signal()
    stop_transcoding_signal = Signal()
    show_message_signal = Signal(str)

    def __init__(self):
        super().__init__()
        # self.ui = Ui_Form()
        # self.ui.setupUi(self)

        self.setupUi(self)

        self.workDir = None
        self.targetDir = None
        self.postDir = None
        self.ffOptions = None

        self.transcoding_thread = None

        self.workDir_button.clicked.connect(self.select_work_dir)
        self.targetDir_button.clicked.connect(self.select_target_dir)
        self.postDir_button.clicked.connect(self.select_post_dir)

        # Connect signals to slots
        self.start_button.clicked.connect(self.start_transcoding_signal.emit)
        self.stop_button.clicked.connect(self.stop_transcoding_signal.emit)

        # Connect slots to functions
        self.start_transcoding_signal.connect(self.start_event)
        self.stop_transcoding_signal.connect(self.stop_transcoding)

        # Connect the valueChanged signal of the periodSlider to the update_period_edit slot
        self.periodSlider.valueChanged.connect(self.update_period_edit)

        # Connect the textChanged signal of the periodEdit to the update_period_slider slot
        self.periodEdit.textChanged.connect(self.update_period_slider)

        self.show_message_signal.connect(self.print_to_output)

        # get current path
        DIR_PARAMS = os.path.join(os.path.dirname(__file__), "config")
        path_config = os.path.join(DIR_PARAMS, "config.toml")
        main_config = load_toml(path_config)

        if "app" in main_config:
            app_config = main_config["app"]
        else:
            print("transcoding_params not found in config file")
            sys.exit(1)

        workDir = app_config["workDir"] if "workDir" in app_config else ""
        self.workDir_label.setText(workDir)
        self.workDir = Path(workDir)

        postDir = (
            app_config["postDir"]
            if "postDir" in app_config
            else os.path.join(self.workDir, "converted")
        )
        self.postDir_label.setText(postDir)
        self.postDir = Path(postDir)

        targetDir = app_config["targetDir"] if "targetDir" in app_config else ""
        self.targetDir_label.setText(targetDir)
        self.targetDir = Path(targetDir)

        self.period = app_config["period"] if "period" in app_config else 60
        self.periodSlider.setValue(self.period)
        self.periodEdit.setText(str(self.period))

        if "dict" in main_config:
            dict_config = main_config["dict"]
        else:
            print("transcoding_params not found in config file")
            sys.exit(1)

        size_default = app_config["size"] if "size" in app_config else "480p"
        size = (
            dict_config["size"]
            if "size" in dict_config
            else ["1080p", "720p", "576p", "480p", "360p", "240p"]
        )
        self.resize_combo.addItems(size)
        self.resize_combo.setCurrentText(size_default)

        fCodec_default = app_config["fCodec"] if "fCodec" in app_config else "libx264"
        fCodec = (
            dict_config["fCodec"] if "fCodec" in dict_config else ["libx264", "libx265"]
        )
        self.fCodec_combo.addItems(fCodec)
        self.fCodec_combo.setCurrentText(fCodec_default)

        VBRate_default = app_config["VBRate"] if "VBRate" in app_config else "500k"
        VBRate = (
            dict_config["VBRate"]
            if "VBRate" in dict_config
            else [
                "100k",
                "200k",
                "300k",
                "400k",
                "500k",
                "600k",
                "700k",
                "800k",
                "900k",
                "1000k",
                "2000k",
                "3000k",
                "4000k",
                "5000k",
            ]
        )
        self.VBRate_combo.addItems(VBRate)
        self.VBRate_combo.setCurrentText(VBRate_default)

        minVBR_default = app_config["minVBR"] if "minVBR" in app_config else "100k"
        minVBR = (
            dict_config["minVBR"]
            if "minVBR" in dict_config
            else [
                "100k",
                "200k",
                "300k",
                "400k",
                "500k",
                "600k",
                "700k",
                "800k",
                "900k",
                "1000k",
            ]
        )
        self.minVBR_combo.addItems(minVBR)
        self.minVBR_combo.setCurrentText(minVBR_default)

        maxVBR_default = app_config["maxVBR"] if "maxVBR" in app_config else "1000k"
        maxVBR = (
            dict_config["maxVBR"]
            if "maxVBR" in dict_config
            else [
                "1000k",
                "2000k",
                "3000k",
                "4000k",
                "5000k",
                "6000k",
                "7000k",
                "8000k",
                "9000k",
                "10000k",
            ]
        )
        self.maxVBR_combo.addItems(maxVBR)
        self.maxVBR_combo.setCurrentText(maxVBR_default)

        ext_default = app_config["ext"] if "ext" in app_config else "mp4"
        ext = dict_config["ext"] if "ext" in dict_config else ["mp4", "mkv", "avi"]
        self.ext_combo.clear()
        self.ext_combo.addItems(ext)
        self.ext_combo.setCurrentText(ext_default)

    def select_work_dir(self):
        workDir = QFileDialog.getExistingDirectory(self, "Select Work Directory")
        if workDir != "":
            self.workDir_label.setText(workDir)
            self.workDir = Path(workDir)

    def select_target_dir(self):
        targetDir = QFileDialog.getExistingDirectory(self, "Выберите целевой каталог")
        if targetDir != "":
            self.targetDir_label.setText(targetDir)
            self.targetDir = Path(targetDir)

    def select_post_dir(self):
        postDir = QFileDialog.getExistingDirectory(
            self, "Выберите папку для перемещения оригинала"
        )
        if postDir != "":
            self.postDir_label.setText(postDir)
            self.postDir = Path(postDir)

    def update_period_edit(self, value):
        self.period = value
        # Update the text of the periodEdit element with the current value of the periodSlider
        self.periodEdit.setText(str(value))

    def update_period_slider(self, text):
        try:
            # Convert the text to an integer and set it as the value of the periodSlider
            value = int(text)
            self.period = value
            self.periodSlider.setValue(value)
        except Exception as e:
            print(e)

    def print_to_output(self, text):
        print(text)
        # Append the text to the output pane
        self.output_pane.appendPlainText(text)

        # Scroll to the bottom to display the latest messages
        cursor = self.output_pane.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_pane.setTextCursor(cursor)

        self.output_pane.repaint()

    def start_event(self):
        if self.workDir == "":
            self.print_to_output("Please select a Work Directory")
            # qreate  QT6 error message
            QMessageBox.critical(self, "Error", "Please select a work directory")
            return

        if self.targetDir == "":
            self.print_to_output("Please select a Work Directory")
            # qreate  QT6 error message
            QMessageBox.critical(self, "Error", "Please select a target directory")
            return

        self.fCodec = self.fCodec_combo.currentText()
        self.VBRate = self.VBRate_combo.currentText()
        self.minVBR = self.minVBR_combo.currentText()
        self.maxVBR = self.maxVBR_combo.currentText()
        self.ext = self.ext_combo.currentText()
        self.resize = self.resize_combo.currentText()

        self.print_to_output(f"Work Directory: {self.workDir}")
        self.print_to_output('')
        self.print_to_output(f"fCodec: {self.fCodec}")
        self.print_to_output(f"VBRate: {self.VBRate}")
        self.print_to_output(f"minVBR: {self.minVBR}")
        self.print_to_output(f"maxVBR: {self.maxVBR}")
        self.print_to_output(f"ext: {self.ext}")
        self.print_to_output('')

        self.ffOptions = (
            self.fCodec,
            self.VBRate,
            self.minVBR,
            self.maxVBR,
            self.ext,
            self.resize,
        )

        self.start_transcoding()

    def start_transcoding(self):
        self.transcoding_thread = TranscodingThread(
            self.workDir, self.targetDir, self.postDir,
            self.ffOptions, self.period
        )
        self.transcoding_thread.show_message.connect(self.print_to_output)
        self.transcoding_thread.transcoding_active = True
        self.transcoding_thread.start()
        # change color text button to green
        self.start_button.setStyleSheet("color: green")
        self.stop_button.setStyleSheet("color: black")

    def stop_transcoding(self):
        self.print_to_output("Stopping transcoding...")
        if hasattr(self, 'transcoding_thread') and self.transcoding_thread:
            self.transcoding_thread.stop()

        self.stop_button.setStyleSheet("color: red")
        self.start_button.setStyleSheet("color: black")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApplication()
    window.show()
    sys.exit(app.exec())