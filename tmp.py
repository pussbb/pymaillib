
from pymaillib.imap.dovecot_utils import parse_date

print(parse_date("2006-05-09T18:04:12+05:30"))
print(parse_date("1990-12-31T15:59:60-08:00"))

raise SystemExit
