from typing import Optional

from pydantic import BaseModel, ConfigDict


class FFEncodeConfigPydantic(BaseModel):
    id: Optional[int] = None
    name: str
    active: bool = False
    period: int = 30
    fcodec: str = "libx264"
    size: str = "480p"
    VBRate: str = "700k"
    minVBR: str = "300k"
    maxVBR: str = "1000k"
    ext: str = "mkv"
    workDir: str = "/mnt/data/test/in/"
    postDir: str = "/mnt/data/test/in/converted/"
    targetDir: str = "/mnt/data/test/result/"
    ffmpeg: str = "/usr/bin/ffmpeg"

    model_config = ConfigDict(
        from_attributes=True,
    )

