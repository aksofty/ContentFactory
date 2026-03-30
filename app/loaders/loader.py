from abc import ABC, abstractmethod

class Loader(ABC):
    data: list = []
    
    @abstractmethod
    async def load(self):
        pass