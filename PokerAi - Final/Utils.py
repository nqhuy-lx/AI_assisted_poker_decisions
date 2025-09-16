def tinh_p_final(p_raw, baseline, hand_bonus):
    p_final = (p_raw + baseline) / 2
    p_final += hand_bonus
    return min(p_final, 1.0)
