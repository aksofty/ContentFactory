from aiovk import TokenSession, API
from anyio import sleep
from loguru import logger
from app.cruds.source_cruds import get_source
from app.cruds.target_cruds import get_target
from app.database import AsyncSessionLocal
from app.utils.common_utils import prepare_media_from_urls
from app.utils.message import Message
from . import Sender

class SenderVK(Sender):
    def __init__(self, target_id, token):
        self.target_id = target_id
        self.token = token

    async def send(self, message: Message):
        short_msg = f"{message.text[:30].strip()}..."
        
        async with AsyncSessionLocal() as session:
            target = await get_target(session, self.target_id)
            if not target:
                logger.error(f"Target не найден #{self.target_id}")
                return

        try:
            logger.info(f"![TG] Отправляем сообщение в :{short_msg}")
            await self._post_async(message, target)

        except Exception as e:
            logger.error(f"-[TG] Произошла ошибка при отправке сообщения: {e}") 


    async def _post_async(self, message, target):
        token = self.token
        group_id = target.channel
        
        async with TokenSession(access_token=token) as session:
            api = API(session)
            try:
                await api.wall.post(
                    owner_id=group_id,
                    from_group=1,
                    message=message.text,
                    attachments=message.enclosures
                )
                print("Готово!")
            except Exception as e:
                print(f"Ошибка: {e}")