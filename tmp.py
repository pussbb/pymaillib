"""
from pymaillib.imap.dovecot_utils import parse_date

print(parse_date("2006-05-09T18:04:12+05:30"))
print(parse_date("1990-12-31T15:59:60-08:00"))

raise SystemExit

"""


def build_numeric_sequence(data: list):
    prev = 0
    start = None
    res = []
    for item in filter(None, sorted(data)):
        if prev+1 == item:
            if not start:
                start = prev
                if res and res[-1] == prev:
                    res.pop()
        else:
            if start:
                res.append('{}:{}'.format(start, prev))
                start = None
            res.append(item)
        prev = item
    return ','.join([str(item) for item in res])


res = build_numeric_sequence([0, 1, 2, 3, 4, 5, 6, 56, 64, 44, 45, 46])
print(res)
