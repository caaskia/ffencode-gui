from typing import Optional, TypeVar, Any, Type

from pydantic import BaseModel, ConfigDict

# Type variable for Pydantic model subclasses
ModelT = TypeVar("ModelT", bound="FFEncodeConfigPydantic")


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

    @classmethod
    async def from_tortoise_orm(cls: Type[ModelT], obj: Any) -> ModelT:
        """Create a Pydantic model instance from a Tortoise ORM model.

        Args:
            obj: The Tortoise ORM model instance to convert

        Returns:
            An instance of the Pydantic model

        Raises:
            ValueError: If the input object is not a valid ORM model
        """
        if not hasattr(obj, "model_dump"):
            # If the object doesn't have model_dump, try to get its attributes manually
            if hasattr(obj, "__dict__"):
                data = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
            else:
                raise ValueError("Input object is not a valid ORM model")
        else:
            data = obj.model_dump()

        # Create the Pydantic model instance
        return cls.model_validate(data)
