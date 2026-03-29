import asyncio
import json
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from loguru import logger
ALLOWED_PATHS = ("/upload/", "/uploads/", "/media/", "/images/article/")

async def parse_article(url: str):
    empty_result = {"text": "", "enclosures": []} 
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content_area = soup.find('article') or soup.find('main') or soup.body
        
        paragraphs = content_area.find_all('p')
        text_content = "\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        images = content_area.find_all('img')
        enclosures = []
        for img in images:
            src = img.get('src')
            if src:
                if any(path in src for path in ALLOWED_PATHS):
                    enclosures.append(urljoin(url, src))
        
        # Формируем итоговый словарь
        result_data = {
            "text": text_content,
            "enclosures": list(set(enclosures))  # Убираем дубликаты ссылок
        }
        
        # Возвращаем JSON-строку
        return json.dumps(result_data, ensure_ascii=False, indent=4)
    
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error(f"Ошибка при запросе {url}: {e}")
        return json.dumps(empty_result, ensure_ascii=False, indent=4)

