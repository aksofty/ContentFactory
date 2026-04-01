from loguru import logger
from app.cruds.source_cruds import get_source
from app.cruds.target_cruds import get_target
from app.database import AsyncSessionLocal
from app.utils import message
from app.utils.common_utils import clear_medias_from_memory, prepare_media
from app.utils.message import Message
from . import Sender

class SenderTg(Sender):
    def __init__(self, target_id, client):
        self.target_id = target_id
        self.client = client

    async def send(self, message: Message):
        short_msg = f"{message.text[:30].strip()}..."
        
        async with AsyncSessionLocal() as session:
            target = await get_target(session, self.target_id)
            if not target:
                logger.error(f"Target не найден #{self.target_id}")
                return
            
        try:
            logger.info(f"![TG] Отправляем сообщение в {target.channel}:{short_msg}")

            send_params = {
                'entity': target.channel,
                'parse_mode': 'md',
                'link_preview': False
            }

            message.enclosures = [] if target.skip_media else message.enclosures

            if message.enclosures:
                prepared_files = await prepare_media(message.enclosures, tg_download=False)
                await self.client.send_file(**send_params, file=prepared_files, caption=message.text)
                await clear_medias_from_memory(prepared_files)
            else:
                await self.client.send_message(**send_params, message=message.text)
            
            logger.info(f"+[TG] Сообщение отправлено в {target.channel}:{short_msg}")

        except Exception as e:
            logger.error(f"-[TG] Произошла ошибка при отправке сообщения: {e}")    