from dataclasses import dataclass
from typing import List, Optional
from loguru import logger
from app.utils.gen_api_utils import gen_api_send

@dataclass
class Message:
    text: str
    enclosures: List[str] = None
    id: Optional[int|str] = None

    prompt: Optional[str] = None
    token: Optional[str] = None
    model: Optional[str] = None

    @classmethod
    async def create(cls, text, enclosures=[], id=None, prompt=None, token=None, model=None):
        logger.info(f"!Создаем сообщение.")

        if prompt:
            if not token or not model:
                logger.error(f"Указаны не все данные для обращения к ИИ, сообщение не обработано.")   
                return None
            
            text = await gen_api_send(text, prompt, token, model)
            if not text:
                logger.error(f"-Обратотка текста ИИ не удалась.")    
                return None
        
        logger.info(f"+Сообщение создано.")
        return cls(
            text=text, enclosures=enclosures, id=id, prompt=prompt, token=token, model=model) 
