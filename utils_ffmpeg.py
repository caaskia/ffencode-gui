import os
from pathlib import Path
import datetime
import subprocess
import shutil

import logging
logging.basicConfig(level=logging.DEBUG, format="%(module)s - %(message)s")


def ffcmd_prepare(config):
    cmd = "ffmpeg -y -hide_banner -i {input_file}"
    cmd_input = ""
    cmd_ffmpeg = ""
    cmd_audio = ""
    cmd_video = ""
    cmd_size = ""
    cmd_output = ""

    cmd_ffmpeg = config.get("cmd_ffmpeg")
    if cmd_ffmpeg:
        cmd += f" {cmd_ffmpeg}"

    # cmd_input += f" -i {config['input_dir']}/" + "{input_file}"

    audio_codec_name = config.get("audio_codec_name")
    audio_bitrate = config.get("audio_bitrate")
    audio_channel = 1

    if audio_codec_name and audio_bitrate and audio_channel:
        cmd_audio = f" -c:a {audio_codec_name}"
        if audio_codec_name != "copy":
            cmd_audio += f" -b:a {audio_bitrate}k"
            cmd_audio += f" -ac {audio_channel}"
    else:
        if cmd_audio := config.get("cmd_audio"):
            cmd_audio = cmd_audio.format(
                audio_bitrate=audio_bitrate, channel=audio_channel
            )

    cmd += cmd_audio

    video_codec_name = config.get("video_codec_name")
    preset = config.get("preset")
    video_bitrate = config.get("video_bitrate")

    if video_codec_name:
        cmd_video = f" -c:v {video_codec_name}"
        if preset:
            cmd_video += f" -preset {preset}"
    else:
        if cmd_video := config.get("cmd_video"):
            cmd_video = cmd_video.format(preset=preset)

    if cmd_video != "" and video_bitrate:
        cmd_video += f" -b:v {video_bitrate}k"

    # cmd_video += "-r " + str(config['video_framerate']) + " "

    video_resolution_width = config.get("video_resolution_width")
    if cmd_video != "" and video_resolution_width and video_resolution_width != 0:
        cmd_video += f" -vf scale={video_resolution_width}:-1"

    cmd += cmd_video

    def replace_сolon(dir_name):
        a, b, c = dir_name.partition(':')
        if b == ':':
            dir_name = f"/mnt/{a.lower()}{c}"
        path = Path(dir_name.replace("\\", "/"))
        return path

    input_dir = config.get("input_dir")  # Получаем путь из конфигурации
    input_path = replace_сolon(input_dir)
    logging.debug(f"input_path: {input_path}")

    output_dir = config.get("output_dir")
    output_path = replace_сolon(output_dir)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        if not os.path.exists(output_path):
            print(f"Не удалось создать папку {output_dir}")
            exit(1)
    logging.debug(f"output_path: {output_path}")

    output_ext = config.get("output_ext")

    post_dir = config.get("post_dir")
    post_path = replace_сolon(post_dir)
    if not os.path.exists(post_path):
        os.makedirs(post_path)
        if not os.path.exists(post_path):
            print(f"Не удалось создать папку {post_dir}")
            exit(1)
    logging.debug(f"post_path: {post_path}")

    post_remove = config.get("post_remove")

    return cmd, input_path, output_path, output_ext, post_remove, post_path


def move_file(infile, target_dir):
    target_dir = Path(target_dir).as_posix()
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        if not os.path.exists(target_dir):
            logging.error(f"Не удалось создать папку {target_dir}")
            return None

    copy_file = os.path.join(target_dir, os.path.basename(infile))
    try:
        shutil.move(infile, copy_file)
        # shutil.copyfile(infile, copy_file)
    except OSError:
        logging.error(f"Не удалось переместить файл {infile} в {target_dir}")
    else:
        if os.path.exists(copy_file):
            # os.remove(infile)
            logging.debug(f"Файл {infile} перемещен в {target_dir}")
        else:
            logging.debug(
                f"Файл {infile} перемещен в {target_dir}, но не обнаружен"
            )


def ff_run(cmd, infile, out_dir, output_ext, post_remove, post_dir=None):
    short_name = os.path.splitext(os.path.basename(infile))[0]
    convert_file = os.path.join(out_dir, f"{short_name}.part.{output_ext}")
    ffcmd = cmd.format(input_file=infile) + f" {convert_file}"
    print(ffcmd)

    now1 = datetime.datetime.now()
    try:
        subprocess.call(ffcmd, shell=True)
    except OSError:
        logging.error(f"Не удалось запустить команду: {ffcmd}")
        return None

    now2 = datetime.datetime.now()
    delta_convert = now2 - now1
    logging.debug(f" Время конвертирования: {delta_convert.total_seconds():.2f} секунд")

    if not os.path.exists(convert_file):
        logging.error(f" Файл не сконвертирован {infile}")
        error_dir = os.path.join(out_dir, "error")
        move_file(infile, error_dir)
        return None

    output_file = os.path.join(out_dir, f"{short_name}.{output_ext}")
    try:
        os.rename(convert_file, output_file)
    except OSError:
        logging.error(
            f"Не удалось переименовать файл {convert_file} в {output_file}"
        )
        output_file = convert_file

    logging.debug(f"Выходной файл: {output_file}")

    if post_remove == "delete":
        os.remove(infile)
    elif post_dir != "":
        move_file(infile, post_dir)

    return output_file
