from tortoise.models import Model
from tortoise import fields


class FFEncodeConfig(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    active = fields.BooleanField(default=False)
    period = fields.IntField(default=30)
    fcodec = fields.CharField(max_length=50, default="libx264")
    size = fields.CharField(max_length=20, default="480p")
    VBRate = fields.CharField(max_length=20, default="700k")
    minVBR = fields.CharField(max_length=20, default="300k")
    maxVBR = fields.CharField(max_length=20, default="1000k")
    ext = fields.CharField(max_length=10, default="mkv")
    workDir = fields.CharField(max_length=255, default="/mnt/data/test/in/")
    postDir = fields.CharField(max_length=255, default="/mnt/data/test/in/converted/")
    targetDir = fields.CharField(max_length=255, default="/mnt/data/test/result/")
    ffmpeg = fields.CharField(max_length=255, default="/usr/bin/ffmpeg")

    class Meta:
        table = "ffencode_config"
