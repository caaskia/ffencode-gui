from typing import List

import toml
from tortoise import run_async

from db.config_tortoise import init_db, close_db
from models.models_tortoise import FFEncodeConfig
from models.models_pydantic import FFEncodeConfigPydantic


async def load_config_from_toml(
    file_path: str = "/mnt/data/storeSoft/projPyW/ffencode-gui/config/config.toml",
):
    try:
        config_data = toml.load(file_path)
        app_config = config_data.get("app", {})

        # Проверяем, существует ли уже конфигурация с именем 'default'
        existing_config = await FFEncodeConfig.filter(name="default").first()
        if not existing_config:
            config = FFEncodeConfig(
                name="default",
                active=True,
                period=app_config.get("period", 30),
                fcodec=app_config.get("fcodec", "libx264"),
                size=app_config.get("size", "480p"),
                VBRate=app_config.get("VBRate", "700k"),
                minVBR=app_config.get("minVBR", "300k"),
                maxVBR=app_config.get("maxVBR", "1000k"),
                ext=app_config.get("ext", "mkv"),
                workDir=app_config.get("workDir", "/mnt/data/test/in/"),
                postDir=app_config.get("postDir", "/mnt/data/test/in/converted/"),
                targetDir=app_config.get("targetDir", "/mnt/data/test/result/"),
                ffmpeg=app_config.get("ffmpeg", "/usr/bin/ffmpeg"),
            )
            await config.save()
            print("Default configuration loaded from TOML and saved to database.")
        else:
            print("Default configuration already exists in the database.")

    except FileNotFoundError:
        print(f"TOML config file not found at {file_path}")
    except Exception as e:
        print(f"An error occurred while loading config from TOML: {e}")


async def get_active_config() -> FFEncodeConfigPydantic:
    config = await FFEncodeConfig.filter(active=True).first()
    if not config:
        # Если активной конфигурации нет, загружаем из toml
        await load_config_from_toml()
        config = await FFEncodeConfig.filter(active=True).first()
        if not config:
            raise Exception(
                "No active configuration found and could not load from TOML."
            )

    return await FFEncodeConfigPydantic.from_tortoise_orm(config)


async def get_all_configs() -> List[FFEncodeConfigPydantic]:
    configs = await FFEncodeConfig.all()
    return [
        await FFEncodeConfigPydantic.from_tortoise_orm(config) for config in configs
    ]


async def update_config(config_data: FFEncodeConfigPydantic):
    config = await FFEncodeConfig.get(id=config_data.id)
    config.name = config_data.name
    config.active = config_data.active
    config.period = config_data.period
    config.fcodec = config_data.fcodec
    config.size = config_data.size
    config.VBRate = config_data.VBRate
    config.minVBR = config_data.minVBR
    config.maxVBR = config_data.maxVBR
    config.ext = config_data.ext
    config.workDir = config_data.workDir
    config.postDir = config_data.postDir
    config.targetDir = config_data.targetDir
    config.ffmpeg = config_data.ffmpeg
    await config.save()


async def backup_configs_to_toml(
    file_path: str = "/mnt/data/storeSoft/projPyW/ffencode-gui/config/config_backup.toml",
):
    configs = await get_all_configs()
    backup_data = {"configurations": [config.dict() for config in configs]}
    with open(file_path, "w") as f:
        toml.dump(backup_data, f)
    print(f"Configuration backup created at {file_path}")


if __name__ == "__main__":

    async def main():
        await init_db()
        count = await FFEncodeConfig.all().count()
        if count == 0:
            await load_config_from_toml()

        active_config = await get_active_config()
        print("Active Config:", active_config)

        await backup_configs_to_toml()

        await close_db()

    run_async(main())
