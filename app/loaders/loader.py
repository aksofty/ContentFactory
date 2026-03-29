from abc import ABC, abstractmethod

class Loader(ABC):
    @abstractmethod
    async def load(self):
        pass