from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "ffencode_config" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "active" INT NOT NULL DEFAULT 0,
    "period" INT NOT NULL DEFAULT 30,
    "fcodec" VARCHAR(50) NOT NULL DEFAULT 'libx264',
    "size" VARCHAR(20) NOT NULL DEFAULT '480p',
    "VBRate" VARCHAR(20) NOT NULL DEFAULT '700k',
    "minVBR" VARCHAR(20) NOT NULL DEFAULT '300k',
    "maxVBR" VARCHAR(20) NOT NULL DEFAULT '1000k',
    "ext" VARCHAR(10) NOT NULL DEFAULT 'mkv',
    "workDir" VARCHAR(255) NOT NULL DEFAULT '/mnt/data/test/in/',
    "postDir" VARCHAR(255) NOT NULL DEFAULT '/mnt/data/test/in/converted/',
    "targetDir" VARCHAR(255) NOT NULL DEFAULT '/mnt/data/test/result/',
    "ffmpeg" VARCHAR(255) NOT NULL DEFAULT '/usr/bin/ffmpeg'
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
