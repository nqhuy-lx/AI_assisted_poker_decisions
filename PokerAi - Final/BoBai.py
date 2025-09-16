import random


class LaBai:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    
    def show(self):
        return f"{self.rank} {self.suit}"



class BoBai:
    def __init__(self):
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['Bich', 'Co', 'Ro', 'Chuon']
        self.cards = []
        for rank in ranks:
            for suit in suits:
                bai = LaBai(rank, suit)
                self.cards.append(bai)

    def xaoBai(self):
        random.shuffle(self.cards)

    def chiaBai(self, so_luong):
        baiChia = []
        for i in range(so_luong):
            if len(self.cards) > 0:
                bai = self.cards.pop(0)
                baiChia.append(bai)
            else:
                print("Không đủ bài để chia.")
                break
        return baiChia