import asyncio
import sys

import qasync
from PySide6.QtWidgets import QApplication
from tortoise import run_async

from db_client.client_tortoise import init_db, close_db
from service.db_service import get_active_config
from service.ui_service import MyApplication


async def main():
    await init_db()

    # Check if there are configurations in the database, if not - load from TOML
    try:
        await get_active_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        raise

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
