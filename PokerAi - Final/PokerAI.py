import time

from MonteCarloSimulator import MonteCarloSimulator
from CheckScore import parse_card


class PokerAI:
    def __init__(self, so_doi_thu=1, so_lan=1000):
        self.simulator = MonteCarloSimulator(so_doi_thu=so_doi_thu, so_lan=so_lan)

        self.min_equity_thresholds = {
            "preflop": 0.15,
            "flop": 0.25,
            "turn": 0.35,
            "river": 0.45
        }

        self.raise_thresholds = {
            "preflop": 0.45,
            "flop": 0.55,
            "turn": 0.60,
            "river": 0.65
        }

    def danh_gia_bai_tay(self, bai_tay):
        la1, la2 = bai_tay
        r1, s1 = parse_card(la1)
        r2, s2 = parse_card(la2)

        rank_order = "23456789TJQKA"
        if r1 == "10": r1 = "T"
        if r2 == "10": r2 = "T"

        if r1 not in rank_order or r2 not in rank_order:
            return 0.0

        idx1, idx2 = rank_order.index(r1), rank_order.index(r2)
        gap = abs(idx1 - idx2)

        bonus = 0.0
        if r1 == r2:
            if r1 in "AKQJ":
                bonus = 0.20
            elif r1 in "T9":
                bonus = 0.15
            else:
                bonus = 0.10
        elif s1 == s2 and gap <= 4:
            bonus = 0.10
        elif r1 in "AKQJ" and r2 in "AKQJ":
            bonus = 0.12
        elif gap <= 2:
            bonus = 0.05

        return bonus

    def tinh_xac_suat_dieu_chinh(self, bai_nguoi_choi, bai_chung_da_co, so_active):
        p_raw = self.simulator.tinh_xac_suat_thang(
            bai_nguoi_choi, bai_chung_da_co, so_doi_thu_override=so_active - 1
        )
        baseline = 1 / so_active
        hand_bonus = self.danh_gia_bai_tay(bai_nguoi_choi)

        p_final = (p_raw + baseline) / 2
        p_final += hand_bonus

        return min(p_final, 1.0), p_raw

    def ra_quyet_dinh(self, bai_nguoi_choi, bai_chung_da_co, so_active, vong="postflop", decision=""):
        p_final, p_raw = self.tinh_xac_suat_dieu_chinh(
            bai_nguoi_choi, bai_chung_da_co, so_active
        )

        call_threshold = self.min_equity_thresholds.get(vong, 0.3)
        raise_threshold = self.raise_thresholds.get(vong, 0.6)
        decision = ""

        if p_final < call_threshold:
            decision = f"Gợi ý: p_raw={p_raw*100:.2f}% | p_final={p_final*100:.2f}% => Bỏ bài"
            return "bo", decision

        if p_final >= raise_threshold:
            decision = f"Gợi ý: p_raw={p_raw*100:.2f}% | p_final={p_final*100:.2f}% => Tố"
            return "to", decision
        
        decision = f"Gợi ý: p_raw={p_raw*100:.2f}% | p_final={p_final*100:.2f}% => Theo"
        return "theo", decision
