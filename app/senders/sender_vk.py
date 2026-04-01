from aiovk import TokenSession, API
import httpx
from loguru import logger
from app.cruds.target_cruds import get_target
from app.database import AsyncSessionLocal
from app.utils.common_utils import clear_medias_from_memory, prepare_media
from app.utils.message import Message
from . import Sender

class SenderVK(Sender):
    def __init__(self, target_id, token, tg_client=None):
        self.target_id = target_id
        self.token = token
        self.tg_client = tg_client

    async def send(self, message: Message):
        short_msg = f"{message.text[:30].strip()}..."
        
        async with AsyncSessionLocal() as session:
            target = await get_target(session, self.target_id)
            if not target:
                logger.error(f"Target не найден #{self.target_id}")
                return

        try:
            logger.info(f"![VK] Отправляем сообщение в :{short_msg}")
            prepared_files = await prepare_media(
                message.enclosures, tg_download=True, tg_client=self.tg_client)
            await self._upload_and_send_files_httpx(message, target, files=prepared_files)
            await clear_medias_from_memory(prepared_files)
            logger.info(f"+[VK] Сообщение успешно отправлено: {short_msg}")

        except Exception as e:
            logger.error(f"-[VK] Произошла ошибка при отправке сообщения: {e}") 


    async def _upload_and_send_files_httpx(self, message, target, files=[]):
        token = self.token
        group_id = target.channel

        async with TokenSession(access_token=token) as session:
            vk_api = API(session)

            # отправляем простое текстовое сообщение, если нет файлов или если нужно пропустить медиа
            if target.skip_media or not files:
                await vk_api.wall.post(
                    owner_id=group_id,
                    random_id=0,
                    message=message.text
                )
                return

            # --- ЛОГИКА ДЛЯ ОТПРАВКИ С ФАЙЛАМИ ЧЕРЕЗ HTTPX ---
            attachments = []
            async with httpx.AsyncClient(timeout=15.0) as http_client:
                for file_obj in files:
                    try:
                        filename = getattr(file_obj, 'name', 'file_without_name.jpg').lower()
                        
                        file_content = file_obj.getvalue()
                        if not file_content:
                            continue

                        # --- ЛОГИКА ДЛЯ ФОТО ---
                        if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            upload_server = await vk_api.photos.getWallUploadServer(group_id=abs(int(group_id)))
                            resp = await http_client.post(upload_server['upload_url'], files={'photo': (file_obj.name, file_obj.getvalue())})
                            
                            upload_data = resp.json()
                            saved_photos = await vk_api.photos.saveWallPhoto(
                                group_id=group_id,
                                server=upload_data['server'],
                                photo=upload_data['photo'],
                                hash=upload_data['hash']
                            )
                            photo = saved_photos[0]
                            attachments.append(f"photo{photo['owner_id']}_{photo['id']}")

                        # --- ЛОГИКА ДЛЯ ВИДЕО ---
                        elif filename.endswith(('.mp4', '.mov', '.avi')):
                            video_res = await vk_api.video.save(
                                name=file_obj.name,
                                group_id=abs(int(group_id)),
                                wallpost=1 
                            )
                            upload_url = video_res['upload_url']
                            await http_client.post(upload_url, files={'video_file': (file_obj.name, file_obj.getvalue())})
                            attachments.append(f"video{video_res['owner_id']}_{video_res['video_id']}")

                    except Exception as e:
                        logger.error(f"Не удалось отправить файл {getattr(file_obj, 'name', 'unknown')}: {e}")

            # если есть прикрепленные файлы, отправляем сообщение с ними
            if attachments:
                await vk_api.wall.post(
                    owner_id=group_id,
                    from_group=1,
                    message=message.text,
                    attachments=",".join(attachments)
                )
            