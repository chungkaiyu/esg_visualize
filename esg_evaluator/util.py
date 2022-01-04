import json


def count_esg_ratio(text, kp_dict):
    result = {}
    for p, wl in kp_dict.items():
        tmp = 0
        for i in set(wl):
            tmp += text.count(i)
        result[p] = tmp

    return result
