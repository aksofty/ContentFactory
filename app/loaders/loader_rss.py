from itertools import dropwhile
import json
import feedparser
from loguru import logger
from app.cruds.source_cruds import get_source
from app.database import AsyncSessionLocal
from app.utils.common_utils import get_rss_tags, make_text_message
from app.utils.parse_utils import parse_article
from app.utils.message import Message
from . import Loader

class LoaderRss(Loader):

    def __init__(self, source_id, gen_api_token):
        self.source_id = source_id
        self.gen_api_token = gen_api_token

    async def load(self):
        async with AsyncSessionLocal() as session:
            source = await get_source(session, self.source_id)
            if not source:
                logger.error(f"Источник не найден #{self.source_id}")
                return

            new_posts = []
            async for post in self._get_new_rss_posts(source):
                processed_msg = await self._process_single_post(session, source, post)
                if processed_msg:
                    new_posts.append(processed_msg)

            self.data = new_posts
            self._log_summary(source.url)


    async def _process_single_post(self, session, source, post):
        try:
            await self._update_last_post_url(session, source, post.link)
            
            body, enclosures = await self._get_post_content(source, post)
            if not body and source.parse_link:
                return None

            return await self._create_message_object(source, post, body, enclosures)

        except Exception as e:
            logger.error(f"[RSS] Ошибка при обработке поста {post.link}: {e}", exc_info=True)
            return None


    async def _get_post_content(self, source, post):
        """Определяет, откуда брать контент: из RSS или через парсинг ссылки."""
        if not source.parse_link:
            enclosures = [e.href for e in getattr(post, "enclosures", [])]
            return post.description, enclosures

        # Парсинг детальной страницы
        try:
            raw_article = await parse_article(post.link)
            article = json.loads(raw_article)
            
            if not article.get("text"):
                logger.warning(f"[RSS] Не удалось извлечь текст из статьи: {post.link}")
                return None, []
                
            return article["text"], article.get("enclosures", [])
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"[RSS] Ошибка парсинга JSON для {post.link}: {e}")
            return None, []
        

    async def _create_message_object(self, source, post, body, enclosures):
        if source.ai_prompt:
            return await Message.create(
                body, 
                enclosures=enclosures, 
                id=post.link, 
                prompt=source.ai_prompt.prompt, 
                model=source.ai_prompt.ai_model.value, 
                token=self.gen_api_token
            )
        
        tags = get_rss_tags(post)
        text = make_text_message(post.title, body, tags)
        return await Message.create(text, enclosures=enclosures, id=post.link)


    def _log_summary(self, url):
        if self.data:
            logger.info(f"[RSS] Обработано новых записей: {len(self.data)} из {url}")
        else:
            logger.info(f"[RSS] Новых записей нет в {url}")


    async def _update_last_post_url(self, session, source, last_post_link):
        try:
            logger.debug(f"Обновление URL последнего поста для источника ID {self.source_id}: {last_post_link}")   
            source.last_post_url = last_post_link
            await session.commit()
            #await self.session.refresh(self.source)

        except Exception as e:
            await session.rollback()
            logger.exception(f"Непредвиденная ошибка при работе с источником ID {self.source_id}: {str(e)}")


    async def _get_new_rss_posts(self, source):

        feed = feedparser.parse(source.url)
    
        if feed.bozo:
            logger.error(f"[RSS] Ошибка обработки {source.url}: {feed.bozo_exception}")
        else:
            logger.info(f"[RSS]{source.url}]:  Ищу новые записи...")
            entries = list(reversed(feed.entries)) if source.reverse else feed.entries
            if source.last_post_url:
                entries = list(dropwhile(lambda e: e.link != source.last_post_url, entries))
                if entries: entries.pop(0)

            for count, entry in enumerate(entries):
                if count >= source.limit:
                    break
                yield entry
      