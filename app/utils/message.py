from dataclasses import dataclass
from typing import Any, List, Optional
from flask_sqlalchemy import model
from loguru import logger
from app.models.sources import source
from app.utils.common_utils import is_valid_content
from app.utils.gen_api_utils import gen_api_send

@dataclass
class Message:
    text: str
    enclosures: List[Any] = None
    id: Optional[int|str] = None

    @classmethod
    async def create(cls, text, enclosures=[], id=None, source=None, gen_api_token=None):
        logger.info(f"!Проверяем сообщение {id}.")

        if source:
            allowed_words = getattr(source.allowed_filter, 'keywords', None)
            forbidden_words = getattr(source.forbidden_filter, 'keywords', None)

            if not is_valid_content(text, allowed_words, forbidden_words):
                logger.info(f"-Сообщение {id} не прошло фильтрацию по разрешающим/запрещающим словам.")
                return None
            
            prompt = getattr(source.ai_prompt, 'prompt', None)
            model = getattr(source.ai_prompt, 'ai_model', None)
            if prompt:
                if not gen_api_token or not model:
                    logger.error(f"Указаны не все данные для обращения к ИИ, сообщение не обработано.")   
                    return None
                
                text = await gen_api_send(text, prompt, gen_api_token, model.value)
                if not text:
                    logger.error(f"-Обратотка текста ИИ не удалась.")    
                    return None
        
        #logger.info(f"+Сообщение создано.")
        return cls(text=text, enclosures=enclosures, id=id) 
    
