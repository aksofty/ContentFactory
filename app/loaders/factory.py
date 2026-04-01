from . import LoaderTg, LoaderRss

class LoaderFactory:
    def __init__(self, app_config):
        self.tg_client = app_config.client
        self.gen_api_token = app_config.gen_api_token
        
    def get_loader(self, source):
        if source.type == 'tg':
            return LoaderTg(source.id, self.tg_client, self.gen_api_token)
        elif source.type == 'rss':
            return LoaderRss(source.id, self.gen_api_token)
        
        raise ValueError(f"Неизвестный тип: {source.type}")