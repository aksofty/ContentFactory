from . import SenderTg, SenderVK

class SenderFactory:
    def __init__(self, tg_client, vk_token):
        self.tg_client = tg_client
        self.vk_token = vk_token

    def get_sender(self, target):
        if target.type == 'tg':
            return SenderTg(target.id, self.tg_client)
        if target.type == 'vk':
            return SenderVK(target.id, self.vk_token)
        
        raise ValueError(f"Неизвестный тип: {target.type}")