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

def step3_compare(text, key_phrase, opt):
    key_phrase = list(key_phrase.values())
    key_phrase = key_phrase[0] + key_phrase[1] + key_phrase[2] + ['Applied Materials']
    key_phrase = sorted(key_phrase, key = lambda x : len(x), reverse = True)
    res = list()
    if opt == 'word':
        idx = 0
        text = text.split()
        while idx < len(text):
            tmp = text[idx]
            start_num = idx
            while idx + 1 < len(text) and (tmp + ' ' + text[idx+ 1]).lower() in key_phrase:
                idx += 1
                tmp +=  ' ' + text[idx]
            if tmp not in key_phrase: 
                tmp = text[start_num]
                idx = start_num + 1
            else: idx += 1
            res.append(tmp)
    else:
        text = text.replace('. ', '.#')
        text = text.split('#')
        res = text
    return res