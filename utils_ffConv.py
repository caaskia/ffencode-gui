import os
import subprocess
import logging
from pathlib import WindowsPath, Path
import shlex

logging.basicConfig(
    filename="transcoding.log",
    level=logging.NOTSET,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)

workDir = "/media/data/store_hdd/Music/mp4/test"
# workDir = '/media/data/store/Music/mp4'
# ffOptions =   'hevc_nvenc', '750k',  '375k', '1500k', 'mkv'
# ffOptions = 'hevc_vaapi', '750k',  '375k', '1500k', 'mkv'
# ffOptions = 'libvpx-vp9', '2M', 'webm'
# ffOptions = 'vp9_vaapi_opus', '750k',  '375k', '1500k', 'webm'
# ffOptions = 'libx264',        '992k', '375k', '1984k', 'mkv'
ffOptions = "libx264", "750k", "375k", "1500k", "mkv"
# ffOptions = 'libx264',    '750k',  '375k', '1500k', 'mp4'
# ffOptions = 'h264_vaapi', '750k',  '375k', '1500k', 'mp4'


def getSendFiles(workDir):
    work_files = os.listdir(workDir)
    for workFile in work_files:
        checkwork_file = os.path.join(workDir, workFile)
        if os.path.isdir(checkwork_file):
            work_files.remove(workFile)

    lock_files = []
    # lock_files = [x for x in work_files if (x.endswith(".part") or x.endswith(".busy"))]
    # if len(lock_files) > 0:
    #     for lockFile in lock_files:
    #         # namelockFile, ext = os.path.splitext(lockFile)
    #         for workFile in work_files:
    #             if workFile == lockFile:
    #                 work_files.remove(workFile)

    work_files = [
        x
        for x in work_files
        if (
            x.endswith(".mp4")
            # or x.endswith(".m4a")
            or x.endswith(".mkv")
            or x.endswith(".AVI")
            or x.endswith(".avi")
            or x.endswith(".3gp")
            or x.endswith(".MOV")
            or x.endswith(".MTS")
        )
    ]

    if len(work_files) > 0:
        # sorted(work_files, reverse=False)
        work_files.sort(reverse=False)
        # work_files.sort(key = lambda x: os.stat(os.path.join(workDir, x)).st_mtime)
    return work_files


def ffConv(inFile, dirOut, ffOptions):
    ffmpeg_cmd = None
    # if in Windows use WindowsPath, else use PosixPath
    if os.name == "nt":
        inFile = WindowsPath(inFile)
        dirOut = WindowsPath(dirOut)
    else:
        inFile = Path(inFile)
        dirOut = Path(dirOut)

    # Extract filename without extension from the infile path
    short_name = inFile.stem

    # Join the filename without extension with the dirOut directory and the extension
    out_file = dirOut.joinpath(short_name)

    # name_infile = inFile.rpartition("/")[2]
    # short_name, b, ext = name_infile.partition(".")
    # out_file = os.path.join(dirOut, short_name)
    # print(out_file)

    try:
        fCodec, VBRate, minVBR, maxVBR, ext, resize = ffOptions

        # "ffmpeg -i audio.aac audio.wav"
        # ffmpeg_cmd = "ffmpeg -i '{input}' -ac 2 -c:a aac -ab 28k '{output}'".format(input=inFile, output=out_file)
        # ffmpeg_cmd = "ffmpeg -i '{input}' -y -c:a pcm_s16le '{output}'".format(input=inFile, output=out_file)
        # ffmpeg_cmd = "ffmpeg -i '{input}' -y -ac 1 -acodec pcm_s16le -ar 24000 '{output}'".format(input=inFile, output=out_file)

        if fCodec.__contains__("vaapi"):
            # subprocess.call(['export LIBVA_DRIVER_NAME=i965'], shell=True)
            os.environ["LIBVA_DRIVER_NAME"] = "i965"
            print(os.environ["LIBVA_DRIVER_NAME"])

        if fCodec == "copy":
            ffmpeg_cmd = "ffmpeg -y -i '{input}'".format(input=inFile)
            ffmpeg_cmd += " -c:v copy"
            ffmpeg_cmd += " -c:a aac -b:a 96k -ac 2 '{output}.{ext}'".format(
                output=out_file, ext=ext
            )
        # elif fCodec == 'libx264':
        #     ffmpeg_cmd = "ffmpeg -y -i '{input}'".format(input=inFile)
        #     if resize := True:
        #         ffmpeg_cmd += " -vf scale=-2:480"
        #     #     ffmpeg_cmd += f" -vf scale=640:480"  # Set the desired width and height for resizing
        #     ffmpeg_cmd += " -c:v libx264 -preset veryfast -b:v {VBRate} -maxrate {maxVBR} -bufsize 3968k".format(VBRate = VBRate, maxVBR = maxVBR)
        #     ffmpeg_cmd += " -c:a aac -b:a 96k -ac 2 '{output}.{ext}'".format(output=out_file, ext=ext)
        elif fCodec == "libx264":
            ffmpeg_cmd = f"ffmpeg -y -i '{inFile}'"
            if resize == "240p":
                ffmpeg_cmd += " -vf scale=-2:240"
                # ffmpeg_cmd += f" -vf scale=426:240"  # Set the width and height for 240p
            elif resize == "480p":
                ffmpeg_cmd += " -vf scale=-2:480"
            elif resize == "576p":
                ffmpeg_cmd += " -vf scale=-2:576"
            elif resize == "720p":
                ffmpeg_cmd += " -vf scale=-2:720"
            ffmpeg_cmd += f" -c:v libx264 -preset veryfast -b:v {VBRate} -maxrate {maxVBR} -bufsize 3968k"
            ffmpeg_cmd += f" -c:a aac -b:a 96k -ac 2 '{out_file}.{ext}'"
        elif fCodec == "h264_vaapi":
            ffmpeg_cmd = "ffmpeg -y -vaapi_device /dev/dri/renderD128 -i '{input}' -vf 'format=nv12,hwupload'".format(
                input=inFile
            )
            ffmpeg_cmd += " -c:v h264_vaapi -b:v {vbr}".format(vbr=VBRate)
            ffmpeg_cmd += " -c:a aac -b:a 96k '{output}.{ext}'".format(
                output=out_file, ext=ext
            )
        elif fCodec == "libx265":
            ffmpeg_cmd = "ffmpeg -y -i '{input}'".format(input=inFile)
            ffmpeg_cmd += " -c:v libx265 -crf 17 -b:v {vbr}".format(vbr=VBRate)
            ffmpeg_cmd += " -c:a aac -b:a 96k -ac 2 '{output}.{ext}'".format(
                output=out_file, ext=ext
            )
        elif fCodec == "hevc_vaapi":
            ffmpeg_cmd = "ffmpeg -y -vaapi_device /dev/dri/renderD128 -i '{input}' -vf 'format=nv12,hwupload'".format(
                input=inFile
            )
            ffmpeg_cmd += " -c:v hevc_vaapi -b:v {vbr} -minrate {minVBR} -maxrate {maxVBR}".format(
                vbr=VBRate, minVBR=minVBR, maxVBR=maxVBR
            )
            ffmpeg_cmd += " -c:a aac -b:a 96k '{output}.{ext}'".format(
                output=out_file, ext=ext
            )
        elif fCodec == "hevc_nvenc":
            ffmpeg_cmd = "ffmpeg -y -i '{input}'".format(input=inFile)
            ffmpeg_cmd += " -c:v hevc_nvenc -preset hq -rc vbr -profile:v main10 -b:v {vbr}".format(
                vbr=VBRate
            )
            # ffmpeg_cmd += " -c:v hevc_nvenc -preset hq -rc vbr -cq 33 -qmin 35 -qmax 27 -profile:v main10 -b:v {vbr}".format(vbr = VBRate)
            ffmpeg_cmd += " -c:a aac -b:a 96k -ac 2 '{output}.{ext}'".format(
                output=out_file, ext=ext
            )
        elif fCodec == "libvpx-vp9":
            ffmpeg_cmd = " ffmpeg -y -i '{input}'".format(input=inFile)
            ffmpeg_cmd += (
                " -c:v libvpx-vp9 -crf 33 -minrate {minVBR} -maxrate {maxVBR}".format(
                    vbr=VBRate, minVBR=minVBR, maxVBR=maxVBR
                )
            )
            ffmpeg_cmd += " -c:a aac -b:a 96k -ac 2 '{output}.{ext}'".format(
                output=out_file, ext=ext
            )
        elif fCodec == "vp9_vaapi_aac":
            ffmpeg_cmd = "ffmpeg -y -vaapi_device /dev/dri/renderD128 -i '{input}' -vf 'format=nv12,hwupload'".format(
                input=inFile
            )
            ffmpeg_cmd += " -c:v vp9_vaapi -minrate {minVBR} -maxrate {maxVBR}".format(
                vbr=VBRate, minVBR=minVBR, maxVBR=maxVBR
            )
            ffmpeg_cmd += " -c:a aac -b:a 96k '{output}'".format(output=out_file)
        elif fCodec == "vp9_vaapi_opus":
            ffmpeg_cmd = "ffmpeg -y -vaapi_device /dev/dri/renderD128 -i '{input}' -vf 'format=nv12,hwupload'".format(
                input=inFile
            )
            ffmpeg_cmd += " -c:v vp9_vaapi -crf 33 -b:v {vbr} -minrate {minVBR} -maxrate {maxVBR}".format(
                vbr=VBRate, minVBR=minVBR, maxVBR=maxVBR
            )
            ffmpeg_cmd += " -c:a libopus -b:a 96k '{output}.{ext}'".format(
                output=out_file, ext=ext
            )
    except Exception as e:
        print(e)
        return None

    if ffmpeg_cmd is None:
        print("No ffmpeg_cmd")
        return None

    try:
        # subprocess.call(ffmpeg_cmd, shell=True)
        # print("Convert {} sub process exited".format(fCodec))

        cmd = shlex.split(ffmpeg_cmd)
        subprocess.check_call(cmd, shell=False)
        print("Conversion successful!")
    except subprocess.CalledProcessError as e:
        print("Conversion failed with error:", e)
        return None
    return f"{out_file}.{ext}"


if __name__ == "__main__":
    workFiles = getSendFiles(workDir)
    # targetDir = os.path.join(workDir, 'mkv')
    targetDir = workDir
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)
    for item in workFiles:
        inFile = os.path.join(workDir, item)
        ffConv(inFile, targetDir, ffOptions=ffOptions)
    pass
