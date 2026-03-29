from abc import ABC, abstractmethod
from app.utils.message import Message


class Sender(ABC):
    @abstractmethod
    async def send(self, message: Message):
        pass