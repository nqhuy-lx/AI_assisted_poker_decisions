from CheckScore import tinh_diem_tay_bai
from BoBai import BoBai
from Utils import tinh_p_final

class MonteCarloSimulator:
    def __init__(self, so_lan=1000, so_doi_thu=1):
        self.so_lan = so_lan
        self.so_doi_thu = so_doi_thu

    def _to_str(self, card):
        if isinstance(card, str):
            return card
        if hasattr(card, "show"):
            return card.show()
        return str(card)

    def loai_bai_da_biet(self, bo_bai, danh_sach_da_biet):
        ten_la_da_co = set(self._to_str(x) for x in danh_sach_da_biet)
        bo_bai.cards = [la for la in bo_bai.cards if la.show() not in ten_la_da_co]

    def tinh_xac_suat_thang(self, bai_nguoi_choi, bai_chung_da_co=None, so_doi_thu_override=None):
        if bai_chung_da_co is None:
            bai_chung_da_co = []

        old_so_doi = self.so_doi_thu
        if so_doi_thu_override is not None:
            self.so_doi_thu = max(0, int(so_doi_thu_override))

        so_lan_thang = 0
        for _ in range(self.so_lan):
            bo = BoBai()
            bo.xaoBai()

            cac_la_biet = list(bai_nguoi_choi) + list(bai_chung_da_co)
            self.loai_bai_da_biet(bo, cac_la_biet)

            ds_bai_doi_thu = [bo.chiaBai(2) for _ in range(self.so_doi_thu)]

            so_la_con_thieu = 5 - len(bai_chung_da_co)
            bai_chung_da_sim = list(bai_chung_da_co) + bo.chiaBai(so_la_con_thieu)

            all_nguoi = [self._to_str(x) for x in (list(bai_nguoi_choi) + bai_chung_da_sim)]
            diem_nguoi = tinh_diem_tay_bai(all_nguoi)

            thua = False
            for bai_doi_thu in ds_bai_doi_thu:
                all_doi_thu = [self._to_str(x) for x in (bai_doi_thu + bai_chung_da_sim)]
                diem_doi_thu = tinh_diem_tay_bai(all_doi_thu)
                if diem_doi_thu > diem_nguoi:
                    thua = True
                    break
            if not thua:
                so_lan_thang += 1

        if so_doi_thu_override is not None:
            self.so_doi_thu = old_so_doi

        return so_lan_thang / self.so_lan

    def tinh_xac_suat_day_du(self, bai_nguoi_choi, bai_chung_da_co=None, so_active=2):
        if bai_chung_da_co is None:
            bai_chung_da_co = []

        p_raw = self.tinh_xac_suat_thang(bai_nguoi_choi, bai_chung_da_co, so_active - 1)
        baseline = 1 / so_active
        hand_bonus = 0.0
        p_final = tinh_p_final(p_raw, baseline, hand_bonus)
        return {"p_raw": p_raw, "p_final": p_final}

def simulate(hand, board, active_players, runs=2000):
    sim = MonteCarloSimulator(so_lan=runs, so_doi_thu=max(0, active_players - 1))
    return sim.tinh_xac_suat_day_du(hand, board, so_active=active_players)