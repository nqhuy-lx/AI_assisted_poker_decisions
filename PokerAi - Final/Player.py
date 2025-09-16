class Player:
    def __init__(self, ten, is_bot=False):
        self.ten = ten
        self.is_bot = is_bot      
        self.bai_tren_tay = []   
        self.bo_bai = False    

    def phat_bai(self, bai):
        self.bai_tren_tay = bai

    def bo(self):
        self.bo_bai = True

    def is_active(self):
        return not self.bo_bai

    def hien_thi_bai(self):
        return ', '.join([c.show() for c in self.bai_tren_tay])
