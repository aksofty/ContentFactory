import io
import re
import httpx
from loguru import logger
from wtforms.validators import url
from telethon.tl.types import DocumentAttributeFilename, MessageMediaPhoto


def is_valid_content(
        text: str, allowed_str: str|None, forbidden_str: str|None) -> bool: 
    if not text:
        return False
    
    text_lower = text.lower()
    def prepare_list(s: str|None) -> list[str]:
        if not s:
            return []
        return [w.strip().lower() for w in s.split(',') if w.strip()]

    forbidden = prepare_list(forbidden_str)
    if forbidden:
        if any(word in text_lower for word in forbidden):
            return False
        
    allowed = prepare_list(allowed_str)
    if allowed:
        return any(word in text_lower for word in allowed)

    return True


def is_url(string):
    if not isinstance(string, str):
        return False
    regex = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
    return re.match(regex, string) is not None

async def download_file_by_url(url, max_size_mb=5):
    MAX_SIZE = max_size_mb * 1024 * 1024  
    async with httpx.AsyncClient() as client:
        try:
            head = await client.head(url, follow_redirects=True)
            file_size = int(head.headers.get("Content-Length", 0))

            if file_size > MAX_SIZE:
                logger.error(f"Пропускаем {url}: Слишком большой файл ({file_size / 1024 / 1024:.2f} MB)")
                return None

            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                file = io.BytesIO(response.content)

                clean_name = url.split('/')[-1].split('?')[0] or "image.jpg"
                file.name = clean_name
                return file

        except Exception as e:
            logger.info(f"Ошибка обработки файла {url}: {e}")
    return None

async def download_file_by_tg(media, tg_client, tg_download=True, max_size_mb=5):
    if not media:
        return None
    if not tg_download:
        return media

    filename = "file.bin"
    MAX_SIZE = max_size_mb * 1024 * 1024
    try:
        file_bytes = await tg_client.download_media(media, file=bytes)
        if len(file_bytes) > MAX_SIZE:
            logger.error(f"Пропускаем {media.id}: Слишком большой файл ({len(file_bytes) / 1024 / 1024:.2f} MB)")
            return None
        
        if hasattr(media, 'document'):
        # Ищем атрибут имени в списке атрибутов документа
            for attr in media.document.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    filename = attr.file_name
                    break
                elif isinstance(media, MessageMediaPhoto) or hasattr(media, 'photo'):
                    # У фото нет оригинального имени, задаем стандартное
                    filename = f"photo_{media.id}.jpg"

        file = io.BytesIO(file_bytes)
        file.name = filename
        return file
    except Exception as e:
        logger.info(f"Ошибка обработки файла {media.id}: {e}")
    return None


async def download_file(url, tg_client=None, tg_download=True, max_size_mb=5):
    MAX_SIZE = max_size_mb * 1024 * 1024
    if is_url(url):
        return await download_file_by_url(url, max_size_mb)
    else:
        return await download_file_by_tg(
            url, tg_client, tg_download=tg_download, max_size_mb=max_size_mb)
    return None

async def clear_medias_from_memory(medias):
    for media in medias:
        try:             
            if isinstance(media, io.BytesIO) and not media.closed:
                media.close()
        except Exception as e:
            logger.error(f"Ошибка при закрытии файла {media.name}: {e}")

async def prepare_media(medias, tg_client=None, tg_download=True, max_size_mb=5):
    media_list = []
    for media in medias:
        file = await download_file(
            media, tg_client, tg_download=tg_download, max_size_mb=max_size_mb)
        if file:
            media_list.append(file)

    return media_list


'''async def prepare_media_from_urls(urls, max_size_mb=5):
    # 5mb x 10 (максимальное количество прикрепленных файлов) = 50 mb памяти
    # Переводим МБ в байты
    MAX_SIZE = max_size_mb * 1024 * 1024
    media_list = []
    
    async with httpx.AsyncClient() as client:
        for url in urls:
            if is_url(url):
                try:
                    # 1. Сначала проверяем только заголовок (без скачивания контента)
                    head = await client.head(url, follow_redirects=True)
                    file_size = int(head.headers.get("Content-Length", 0))

                    if file_size > MAX_SIZE:
                        logger.error(f"Пропускаем {url}: Слишком большой файл ({file_size / 1024 / 1024:.2f} MB)")
                        continue

                    # 2. Если размер ок, скачиваем полностью
                    response = await client.get(url, timeout=10.0)
                    if response.status_code == 200:
                        file = io.BytesIO(response.content)
                        
                        # Формируем чистое имя файла (без параметров после ?)
                        clean_name = url.split('/')[-1].split('?')[0] or "image.jpg"
                        file.name = clean_name
                        
                        media_list.append(file)
                except Exception as e:
                    logger.info(f"Ошибка обработки файла {url}: {e}")
            else:
                file_bytes = await client.download_media(message, file=bytes)
                media_list.append(url) # если не ссылка на файл то оставляем как есть (это идентификатор файла)

    return media_list'''

def make_text_message(
        title: str, 
        body: str, 
        tags: list, 
        max_len: int = 1000
    ) -> str:

    tags_str = f"\n{' '.join(tags)}" if tags else ""

    template = f"{title}\n\n{body}{tags_str}"

    # Считаем доступное место для основного текста
    max_body_len = max_len - len(template)
    clean_body = body[:max_body_len] + "..." if len(body) > max_body_len else body
    template = f"{title}\n\n{clean_body}{tags_str}"

    return template

def get_rss_tags(post):
    tags = []
    for tag in getattr(post, 'tags', []):
        clean_tag = re.sub(r'[-\s]+', '', tag.term)
        tags.append(f"#{clean_tag}")
    return tags