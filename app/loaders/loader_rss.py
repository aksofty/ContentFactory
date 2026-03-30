import json
from typing import Optional
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from app.utils.common_utils import get_rss_tags, make_text_message
from app.utils.parse_utils import parse_article
from app.utils.rss_utils import get_new_rss_posts
from app.utils.message import Message
from . import Loader

class LoaderRss(Loader):
    data: Optional[list] = []


    def __init__(self, source, session, gen_api_token):
        self.source = source
        self.session = session
        self.gen_api_token = gen_api_token


    async def load(self):
        new_posts = []
        async for post in get_new_rss_posts(self.source):
            try:
                body = ""
                enclosures = []
                # Обновляем последний урл в БД
                await self.update_last_post_url(post.link)

                if self.source.parse_link:
                    # Парсим детальную страницу статьи
                    aticle = json.loads(await parse_article(post.link))
                    if aticle["text"]:
                        body = aticle["text"]
                        enclosures = aticle["enclosures"]
                    else:
                        logger.error(f"[RSS] Не удалось распарсить статью") 
                        continue  
                else:
                    # Берем текст из из description
                    body = post.description
                    enclosures = [e.href for e in getattr(post, "enclosures", [])]

                msg = None
                if self.source.ai_prompt:
                    msg = await Message.create(body, enclosures=enclosures, id=post.link, prompt=self.source.ai_prompt.prompt, 
                                               model=self.source.ai_prompt.ai_model.value, token=self.gen_api_token)    
                else:
                    tags = get_rss_tags(post)
                    text = make_text_message(post.title, body, tags)
                    msg = await Message.create(text, enclosures=enclosures, id=post.link)

                if msg:
                    new_posts.append(msg)

            except Exception as e:
                logger.error(f"[RSS] Произошла ошибка при загрузке: {e}") 
                continue   

        self.data = new_posts
        if self.data:
            logger.info(f"[RSS] Новые записи из {self.source.url} обработаны")
        else:
            logger.info(f"[RSS] Новых записей нет в {self.source.url}")


    async def update_last_post_url(self, last_post_link):
        try:
            logger.debug(f"Обновление URL последнего поста для источника ID {self.source.id}: {last_post_link}")
            self.source.last_post_url = last_post_link
            await self.session.commit()
            await self.session.refresh(self.source)
            logger.info(f"Успешно обновлен URL последнего поста для RSS-источника '{self.source.name}' (ID: {last_post_link})")
            return True

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка SQLAlchemy при обновлении RSS-источника ID {self.source.id}: {str(e)}")

        except Exception as e:
            await self.session.rollback()
            logger.exception(f"Непредвиденная ошибка при работе с источником ID {self.source.id}: {str(e)}")
        
        return None