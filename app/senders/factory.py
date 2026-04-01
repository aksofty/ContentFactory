from . import SenderTg, SenderVK

class SenderFactory:
    def __init__(self, app_config):
        self.tg_client = app_config.client
        self.vk_token = app_config.vk_token
       
    def get_sender(self, target):
        if target.type == 'tg':
            return SenderTg(target.id, self.tg_client)
        if target.type == 'vk':
            return SenderVK(target.id, self.vk_token, self.tg_client)
        
        raise ValueError(f"Неизвестный тип: {target.type}")