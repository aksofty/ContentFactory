import asyncio
from datetime import datetime
from loguru import logger
from telethon import TelegramClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app import LOG_PATH
from app.config import Config
from app.cruds.source_cruds import get_source, get_source_list
from app.database import AsyncSessionLocal, engine
from app.models.base import Base
from app.utils.scheduler_utils import add_all_jobs
from app.utils.tg_utils import tg_auth_qr

logger.remove()
logger.add(lambda msg: print(msg, end=""), level="DEBUG")
logger.add(LOG_PATH, rotation="1 MB")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Связь с БД установлена")



async def main():
    logger.info(f"Стартуем {datetime.now()}")

    await init_db()

    client = TelegramClient(
        Config.SESSION_NAME, int(Config.CLIENT_ID), str(Config.CLIENT_TOKEN))
    await client.connect() 
    await tg_auth_qr(client, True)
    logger.info(f"Авторизация в Телеграм прошла успешно!")

     
    scheduler = AsyncIOScheduler()
    await add_all_jobs(
        scheduler, client, Config.GEN_API_KEY, Config.VK_TOKEN)
    scheduler.start()

    try:
        await client.run_until_disconnected()
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Получен сигнал остановки")
    finally:
        scheduler.shutdown()
        await client.disconnect()
        logger.info("Сервис остановлен!")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass