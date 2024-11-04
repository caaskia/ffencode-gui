import os
import subprocess
import json
import ffmpy
from pathlib import Path

from PySide6.QtCore import QThread, QTimer, Signal

from utils.utils_ffConv import ffConv, getSendFiles
from utils.utils_ffmpeg import move_file


class TranscodingThread(QThread):
    show_message = Signal(str)

    def __init__(self, work_dir, target_dir, ffOptions, period=60, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.workDir = work_dir
        self.targetDir = target_dir
        self.postDir = self.parent.postDir
        self.ffOptions = ffOptions
        self.set_period(period)
        self.transcoding_active = True

    def set_period(self, period_text):
        try:
            period = max(int(period_text), 10)
        except ValueError:
            period = 60
        self.period = period

    def send_msg(self, msg):
        # self.parent.show_message_signal.emit(msg)
        self.show_message.emit(msg)

    def run(self):
        QTimer.singleShot(0, self.process_work_files)
        # timer = QTimer(self)
        # timer.timeout.connect(self.process_work_files)
        # timer.start(self.period * 1000)

    def process_work_files(self):
        work_files = getSendFiles(self.workDir)
        target_dir = self.targetDir

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        if not work_files:
            self.send_msg(f"No files found in {self.workDir}")
        else:
            for item in work_files:
                if not self.transcoding_active:
                    return
                in_file = os.path.join(self.workDir, item)
                in_file = Path(str(in_file))
                self.send_msg(f"Transcoding: {in_file}")
                info = self.get_video_info(in_file)

                self.process_audio_info(info)
                self.process_video_info(info)

                out_file = ffConv(in_file, self.targetDir, ffOptions=self.ffOptions)
                if os.path.exists(Path(out_file)):
                    self.send_msg(f"Transcoding complete: {out_file}")
                    self.send_msg("")
                    move_file(in_file, self.postDir)
                else:
                    self.send_msg(f"Transcoding failed: {in_file}")

        if self.transcoding_active:
            QTimer.singleShot(self.period * 1000, self.process_work_files)
        else:
            return

    def process_audio_info(self, info):
        audio_info = info.get("audio_info")
        if audio_info:
            self.send_msg(f"Audio channels: {info['audio_channels']}")
            self.send_msg(
                f"Audio codec name: {info['audio_codec_name']} ({info['audio_codec_long_name']})"
            )
            self.send_msg(f"Audio sample rate: {info['audio_sample_rate']}")

            audio_bitrate = info.get("audio_bitrate")
            if audio_bitrate is not None:
                try:
                    audio_bitrate = int(audio_bitrate)
                except ValueError:
                    self.send_msg(f"Audio bitrate: {audio_bitrate}")
                else:
                    self.send_msg(f"Audio bitrate: {audio_bitrate / 1000:.1f} kbps")
            else:
                self.send_msg("Audio bitrate is not available")

            audio_duration = info.get("audio_duration")
            if audio_duration is not None:
                try:
                    audio_duration = float(info["audio_duration"])
                    minutes, seconds = divmod(audio_duration, 60)
                    self.send_msg(
                        f"Audio duration: {audio_duration:.1f} sec ({int(minutes)} min {seconds:.1f} sec)"
                    )
                except Exception as e:
                    print(e)
            else:
                self.send_msg("Audio duration is not available")

    def process_video_info(self, info):
        video_info = info.get("video_info")
        if video_info:
            self.send_msg(
                f"Video codec: {info['video_codec']} ({info['video_codec_long_name']})"
            )
            self.send_msg(f"Video frame size: {info['video_frame_size']}")
            self.send_msg(
                f"Video display aspect ratio: {info['video_display_aspect_ratio']}"
            )
            self.send_msg(f"Video average frame rate: {info['video_avg_frame_rate']}")

            video_bitrate = info.get("video_bitrate")
            if video_bitrate is not None:
                try:
                    video_bitrate = int(info["video_bitrate"])
                except ValueError:
                    self.send_msg(f"Video bitrate: {info['video_bitrate']}")
                else:
                    self.send_msg(f"Video bitrate: {video_bitrate / 1000:.1f} kbps")
            else:
                self.send_msg("Video bitrate is not available")

            video_duration = info.get("video_duration")
            if video_duration is not None:
                try:
                    video_duration = float(info["video_duration"])
                    minutes, seconds = divmod(video_duration, 60)
                    self.send_msg(
                        f"Video duration: {video_duration:.1f} sec ({int(minutes)} min {seconds:.1f} sec)"
                    )
                    self.send_msg("")
                except Exception as e:
                    print(e)
            else:
                self.send_msg("Video duration is not available")

    @staticmethod
    def get_video_info(file_path):
        info = {
            "audio_info": False,
            "audio_codec_name": None,
            "audio_codec_long_name": None,
            "audio_bits_per_sample": None,
            "audio_sample_rate": None,
            "audio_bitrate": None,
            "audio_channels": None,
            "audio_duration": None,
            "video_info": False,
            "video_codec": None,
            "video_codec_long_name": None,
            "video_frame_size": None,
            "video_avg_frame_rate": None,
            "video_display_aspect_ratio": None,
            "video_bitrate": None,
            "video_duration": None,
        }

        try:
            ffprobe_cmd = ffmpy.FFprobe(
                inputs={file_path: None},
                global_options="-v error -show_streams -of json",
            )
            output, _ = ffprobe_cmd.run(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            probe_data = json.loads(output)

            video_stream = next(
                (
                    stream
                    for stream in probe_data["streams"]
                    if stream["codec_type"] == "video"
                ),
                None,
            )
            audio_stream = next(
                (
                    stream
                    for stream in probe_data["streams"]
                    if stream["codec_type"] == "audio"
                ),
                None,
            )

            if audio_stream:
                info["audio_info"] = True
                info["audio_codec_name"] = (
                    audio_stream["codec_name"] if "codec_name" in audio_stream else None
                )
                info["audio_codec_long_name"] = (
                    audio_stream["codec_long_name"]
                    if "codec_long_name" in audio_stream
                    else None
                )
                info["audio_sample_rate"] = (
                    audio_stream["sample_rate"]
                    if "sample_rate" in audio_stream
                    else None
                )
                # info['audio_bits_per_sample'] = audio_stream[
                #     'bits_per_sample'] if 'bits_per_sample' in audio_stream else None
                info["audio_bitrate"] = (
                    audio_stream["bit_rate"] if "bit_rate" in audio_stream else None
                )
                info["audio_channels"] = (
                    audio_stream["channels"] if "channels" in audio_stream else None
                )
                info["audio_duration"] = (
                    audio_stream["duration"] if "duration" in audio_stream else None
                )

            if video_stream:
                info["video_info"] = True
                info[
                    "video_frame_size"
                ] = f"{video_stream.get('width')}x{video_stream.get('height')}"
                info["video_avg_frame_rate"] = (
                    video_stream["avg_frame_rate"]
                    if "avg_frame_rate" in video_stream
                    else None
                )
                info["video_codec"] = (
                    video_stream["codec_name"] if "codec_name" in video_stream else None
                )
                info["video_codec_long_name"] = (
                    video_stream["codec_long_name"]
                    if "codec_long_name" in video_stream
                    else None
                )
                info["video_bitrate"] = (
                    video_stream["bit_rate"] if "bit_rate" in video_stream else None
                )
                info["video_display_aspect_ratio"] = (
                    video_stream["display_aspect_ratio"]
                    if "display_aspect_ratio" in video_stream
                    else None
                )
                info["video_duration"] = (
                    video_stream["duration"] if "duration" in video_stream else None
                )

        except ffmpy.FFExecutableNotFoundError:
            print("FFmpeg/FFprobe executable not found.")
        except ffmpy.FFRuntimeError as e:
            print(f"Error occurred while getting video info: {e.stderr}")

        return info
