import json


def count_esg_ratio(text, kp_dict):
    result = {}
    for p, wl in kp_dict.items():
        tmp = 0
        for i in set(wl):
            tmp += text.count(i)
        result[p] = tmp
    return cal_esg_ratio(result)

def cal_esg_ratio(text):
    count_sum = sum(text.values())
    if  count_sum != 0:
        for key in text.keys():
            text[key] = text[key] / count_sum
    return text
