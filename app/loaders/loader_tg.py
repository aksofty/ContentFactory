from loguru import logger
from app.cruds.source_cruds import get_source
from app.database import AsyncSessionLocal
from app.utils.message import Message
from . import Loader

class LoaderTg(Loader):
    def __init__(self, source_id, client, gen_api_token):
        self.source_id = source_id
        self.gen_api_token = gen_api_token
        self.client = client


    async def load(self):
        async with AsyncSessionLocal() as session:
            source = await get_source(session, self.source_id)
            if not source:
                logger.error(f"Источник не найден #{self.source_id}")
                return
            
            new_posts = []
            logger.info(f"! Загружаем записи из {source.channel}")
            try:
                async for message in self._get_messages(source, limit=30):
                    message_ids = [message.id]
                    message_media = []

                    if message.media:
                        message_media.append(message.media)

                    if message.grouped_id:
                        logger.info(f"[TG] Сообщение №{message.id} - часть группы {message.grouped_id}. Собираю список...")
                        async for g_message in self._get_all_messages_from_group(source, message.id, message.grouped_id):
                            message_ids.append(g_message.id)
                            print(f"{message.id} - {g_message.id}")
                            if g_message.media:
                                message_media.append(g_message.media)

                    msg = await Message.create(message.text, enclosures=message_media, id=max(message_ids))
                    new_posts.append(msg)

            except Exception as e:
                logger.error(f"[TG] Произошла ошибка при загрузке: {e}")  

            #for p in new_posts:
                #print(p)

            self.data = new_posts[:source.limit]
            if self.data:
                logger.info(f"[TG] Новые записи из {source.channel} обработаны")
                await self._update_last_message_id(session, source, self.data[-1].id)
            else:
                logger.info(f"[TG] Новых записей нет в {source.channel}")

 
    async def _get_messages(self, source, limit: int=10):
        """Получает поток сообщений из источника, фильтруя технические и пустые сообщения."""
        min_id = source.last_message_id if source.last_message_id else 0
        smart_limit = limit if min_id>0 else 1
        channel = source.channel

        if min_id > 0:
            messages = self.client.iter_messages(channel, min_id=min_id, limit=smart_limit, reverse=True) 
        else:
            messages = self.client.iter_messages(channel, limit=smart_limit)

        if messages:
            async for message in messages:
                # Пропускаем сервисные сообщения и пустые части альбомов без текста
                if message.id == 1 or (message.grouped_id and not message.text):
                    continue
                yield message


    async def _get_all_messages_from_group(self, source, first_id, group_id, limit: int = 20):  
        """Ищет все сообщения, принадлежащие одной группе (альбому).""" 
        async for message in self.client.iter_messages(source.channel, min_id=first_id-10, limit=limit):
            if message.grouped_id and message.grouped_id == group_id:
                yield message 


    async def _update_last_message_id(self, session, source, last_message_id):
        pass
        try:
            logger.debug(f"Обновление ID последнего сообщения для источника ID {self.source_id}: {last_message_id}")
            source.last_message_id = last_message_id
            await session.commit()
            #await session.refresh(self.source)
            logger.info(f"Успешно обновлен ID последнего сообщения для TG-источника '{source.name}' (ID: {last_message_id})")
            return True

        except Exception as e:
            await session.rollback()
            logger.exception(f"Непредвиденная ошибка при работе с источником ID {self.source_id}: {str(e)}")
        
        return None