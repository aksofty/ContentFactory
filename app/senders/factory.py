from . import SenderTg

class SenderFactory:
    def __init__(self, tg_client):
        self.tg_client = tg_client
        
    def get_sender(self, target):
        if target.type == 'tg':
            return SenderTg(target, self.tg_client)
        
        raise ValueError(f"Неизвестный тип: {target.type}")