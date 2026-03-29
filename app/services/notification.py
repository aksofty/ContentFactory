from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from app.models.targets.target import Target
from app.cruds.target_cruds import get_target_list
from app.utils.message import Message

class NotificationService:
    def __init__(self, session, sender_factory, source):
        self.session = session
        self.factory = sender_factory
        self.source = source

    async def send_message_to_subcribers(self, message: Message):
        logger.info(f"Отправка сообщения всем подписчикам источника #{self.source.id}...")

        targets = await get_target_list(
            self.session, source_id=self.source.id, is_active=True)

        for target in targets:
            sender = self.factory.get_sender(target)
            await sender.send(message)

