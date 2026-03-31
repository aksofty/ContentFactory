import io
import re
import httpx
from loguru import logger

def is_valid_content(
        text: str, allowed_str: str|None, forbidden_str: str|None) -> bool: 
    if not text:
        return False
    
    print(allowed_str)
    
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
    print(allowed)
    if allowed:
        return any(word in text_lower for word in allowed)

    return True


def is_url(string):
    if not isinstance(string, str):
        return False
    regex = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
    return re.match(regex, string) is not None


async def prepare_media_from_urls(urls, max_size_mb=5):
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
                media_list.append(url) # если не ссылка на файл то оставляем как есть (это идентификатор файла)

    return media_list

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