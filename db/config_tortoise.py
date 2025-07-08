from tortoise import Tortoise

DB_CONFIG = {
    "connections": {
        "default": "sqlite:///mnt/data/storeSoft/projPyW/ffencode-gui/db/config.db"
    },
    "apps": {
        "models": {
            "models": ["models.models_tortoise", "aerich.models"],
            "default_connection": "default",
        }
    },
}


async def init_db():
    await Tortoise.init(config=DB_CONFIG)
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_connections()
