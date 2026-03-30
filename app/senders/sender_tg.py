from loguru import logger
from app.utils.common_utils import prepare_media_from_urls
from . import Sender
from app.utils.message import Message

class SenderTg(Sender):
    def __init__(self, target, client):
        self.target = target
        self.client = client

    async def send(self, message: Message):
        short_msg = f"{message.text[:30].strip()}..."
        logger.info(f"![TG] Отправляем сообщение в {self.target.channel}: {short_msg}")
        try:
            if message.enclosures:
                prepared_files = await prepare_media_from_urls(message.enclosures)
                await self.client.send_file(self.target.channel, prepared_files, caption=message.text, parse_mode='md')
            else:
                await self.client.send_message(self.target.channel, message.text, parse_mode='md')
        except Exception as e:
            logger.error(f"[TG] Произошла ошибка при отправке сообщения: {e}")     

        logger.info(f"+[TG] Сообщение отправлено в {self.target.channel}: {short_msg}")