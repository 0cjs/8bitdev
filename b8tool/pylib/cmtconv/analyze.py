def baud_rates(baud):
    res = []
    b = baud
    while b >= 115:
        res.append(int(b))
        b = b / 2
    res = list(reversed(res))
    b = baud * 2
    while b <= 10000:
        res.append(int(b))
        b = b * 2
    return res
