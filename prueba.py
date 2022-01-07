import datetime
from werkzeug.security import generate_password_hash, check_password_hash

print(generate_password_hash("25222333"))
print(datetime.datetime.now()-datetime.datetime(2021,6,16,22,30))
print(datetime.datetime.now().date()==datetime.date(2021,6,19))
print(datetime.datetime.now().toordinal())
print(datetime.datetime.now().isocalendar())
print(datetime.datetime.now().isoformat())
s='2020-11-15'
s=list(map(int,s.split('-')))
print(datetime.date(s[0],s[1],s[2]))
