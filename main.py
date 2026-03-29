import asyncio
from datetime import datetime
from loguru import logger
from telethon import TelegramClient
from app import LOG_PATH
from app.config import Config
from app.cruds.source_cruds import get_source
from app.database import AsyncSessionLocal, engine
from app.models.base import Base
from app.senders.factory import SenderFactory
from app.loaders.factory import LoaderFactory
from app.services.notification import NotificationService
from app.utils.common_utils import is_url
from app.utils.rss_utils import get_new_rss_posts
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

    async with AsyncSessionLocal() as session:  
        source = await get_source(session, 2)
        if source:
            loader_factory = LoaderFactory(session=session, tg_client=client, gen_api_token=Config.GEN_API_KEY)
            loader = loader_factory.get_loader(source)
            await loader.load()

            if loader.data:
                sender_factory = SenderFactory(tg_client=client)
                service = NotificationService(session=session, sender_factory=sender_factory, source=source)
                for message in loader.data:
                    await service.send_message_to_subcribers(message)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass