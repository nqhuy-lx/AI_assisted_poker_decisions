from BoBai import BoBai
from PokerAI import PokerAI
from Player import Player


class VanBai:
    def __init__(self, so_doi_thu=2, so_lan_mo_phong=2000, web_mode=False):
        self.so_doi_thu = so_doi_thu
        self.so_lan_mo_phong = so_lan_mo_phong
        self.web_mode = web_mode
        self.bo = BoBai()
        self.bo.xaoBai()
        self.bai_chung = []

        self.nguoi_choi = Player("Bạn", is_bot=False)
        if not web_mode:
            self.nguoi_choi.phat_bai(self.bo.chiaBai(2))

        self.ds_doi_thu = []
        for i in range(self.so_doi_thu):
            bot = Player(f"Đối thủ {i+1}", is_bot=True)
            if not web_mode:
                bot.phat_bai(self.bo.chiaBai(2))
            self.ds_doi_thu.append(bot)

        self.ai = PokerAI(so_doi_thu=self.so_doi_thu, so_lan=self.so_lan_mo_phong)

    def cap_nhat_bai_nguoi_choi(self, bai_tay):
        class S:
            def __init__(self, s): self._s = s
            def show(self): return self._s
        self.nguoi_choi.phat_bai([S(x) if isinstance(x, str) else x for x in bai_tay])

    def cap_nhat_so_doi_thu(self, so_moi):
        self.so_doi_thu -= so_moi
        if len(self.ds_doi_thu) > self.so_doi_thu:
            self.ds_doi_thu = self.ds_doi_thu[:self.so_doi_thu]
        self.ai.simulator.so_doi_thu = max(0, self.so_doi_thu)

    def hien_thi_bai(self, bai):
        return ', '.join([card.show() for card in bai])

    def so_active_players(self):
        active = 0
        if not self.nguoi_choi.bo_bai:
            active += 1
        active += sum(1 for bot in self.ds_doi_thu if not bot.bo_bai)
        return active

    def in_bang_ti_le(self, ten_vong):
        print(f"\n=== Bảng tỉ lệ thắng ({ten_vong}) ===")
        active_players = [p for p in [self.nguoi_choi] + self.ds_doi_thu if not p.bo_bai]
        so_active = self.so_active_players()

        for p in active_players:
            p_final, p_raw = self.ai.tinh_xac_suat_dieu_chinh(
                [c.show() for c in p.bai_tren_tay],
                [c.show() for c in self.bai_chung],
                so_active
            )
            print(f"{p.ten}: p_raw={p_raw*100:.2f}% | p_final={p_final*100:.2f}%")

    def so_doi_thu_con_lai(self,doi_thu=None):
        doi_thu = self.so_doi_thu
        return doi_thu
