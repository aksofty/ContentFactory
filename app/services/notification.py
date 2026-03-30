from loguru import logger
from app.database import AsyncSessionLocal
from app.cruds.target_cruds import get_target_list
from app.utils.message import Message

class NotificationService:
    def __init__(self, sender_factory, source):
        self.factory = sender_factory
        self.source = source

    #@classmethod
    async def send_message_to_subcribers(self, message: Message):
        logger.info(f"Отправка сообщения всем подписчикам источника #{self.source.id}...")
        async with AsyncSessionLocal() as session:
            targets = await get_target_list(session, source_id=self.source.id, is_active=True)
            for target in targets:
                sender = self.factory.get_sender(target)
                await sender.send(message)

