from itertools import dropwhile
import feedparser
from loguru import logger

async def get_new_rss_posts(source):

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