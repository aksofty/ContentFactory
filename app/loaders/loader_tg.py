from loguru import logger
from . import Loader

class LoaderTg(Loader):
    def __init__(self, source, session, client, gen_api_token):
        self.source = source
        self.session = session
        self.client = client
        self.gen_api_token = gen_api_token

    async def load(self):
        logger.info(f"! Загружаем записи из {self.source.channel}")
        try:
            pass
        except Exception as e:
            logger.error(f"[TG] Произошла ошибка при загрузке: {e}")     

        logger.info(f"[TG] Записи загружены из {self.source.channel}")