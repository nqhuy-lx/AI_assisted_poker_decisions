from itertools import combinations
thu_tu = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7,
              '8':8, '9':9, '10':10, 'J':11, 'Q':12, 'K':13, 'A':14}
def tinh_so(rank):    
    return thu_tu[rank]

def parse_card(card_str):
    if not card_str:
        raise ValueError("Card string rỗng!")

    card_str = card_str.strip().replace(" ", "_")

    if "_" not in card_str:
        raise ValueError(f"Card string không hợp lệ: {card_str}")

    parts = card_str.split("_")
    if len(parts) != 2:
        raise ValueError(f"Không tìm thấy rank/suit trong {card_str}")

    rank, suit = parts[0], parts[1]
    return rank, suit


def is_sanh(cards):
    danh_sach_so = sorted(set([tinh_so(parse_card(c)[0]) for c in cards]))
    for i in range(len(danh_sach_so) - 4):
        if danh_sach_so[i+4] - danh_sach_so[i] == 4:
            return True
    if set([14,2,3,4,5]).issubset(danh_sach_so):
        return True
    return False

def is_dong_chat(cards):
    suits = [parse_card(c)[1] for c in cards]
    for s in set(suits):
        if suits.count(s) >= 5:
            return True
    return False

def tinh_diem_tay_bai(bo_5_to_7_la):
    ket_qua_max = (1, [])
    for to_hop in combinations(bo_5_to_7_la, 5):
        so_dem, chat_dem, danh_sach_so = {}, {}, []
        for c in to_hop:
            r, s = parse_card(c)
            so = tinh_so(r)
            danh_sach_so.append(so)
            so_dem[so] = so_dem.get(so, 0) + 1
            chat_dem[s] = chat_dem.get(s, 0) + 1

        so_sap_xep = sorted(so_dem.items(), key=lambda x: (-x[1], -x[0]))
        so_rank = [item[0] for item in so_sap_xep]

        la_sanh = is_sanh(to_hop)
        la_dong_chat = is_dong_chat(to_hop)

        if la_sanh and la_dong_chat:
            diem = 10 if set([10,11,12,13,14]).issubset(set(danh_sach_so)) else 9
        elif so_sap_xep[0][1] == 4: diem = 8
        elif so_sap_xep[0][1] == 3 and so_sap_xep[1][1] == 2: diem = 7
        elif la_dong_chat: diem = 6
        elif la_sanh: diem = 5
        elif so_sap_xep[0][1] == 3: diem = 4
        elif so_sap_xep[0][1] == 2 and so_sap_xep[1][1] == 2: diem = 3
        elif so_sap_xep[0][1] == 2: diem = 2
        else: diem = 1

        ket_qua_max = max(ket_qua_max, (diem, so_rank))
    return ket_qua_max