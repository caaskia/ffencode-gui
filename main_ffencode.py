import sys
import asyncio
from PySide6.QtWidgets import QApplication
from service.ui_service import MyApplication
from service.db_service import load_config_from_toml, get_active_config
from db.config_tortoise import init_db, close_db
from tortoise import run_async
import qasync


async def main():
    await init_db()

    # Проверяем, есть ли конфигурации в базе, если нет - загружаем из toml
    try:
        await get_active_config()
    except Exception:
        await load_config_from_toml()

    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MyApplication()
    window.show()

    try:
        await loop.run_forever()
    finally:
        await close_db()
        loop.close()


if __name__ == "__main__":
    try:
        run_async(main())
    except KeyboardInterrupt:
        print("Application closed by user.")
