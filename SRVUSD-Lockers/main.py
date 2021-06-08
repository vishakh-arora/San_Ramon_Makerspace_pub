from match import Match
from spreadsheet import Spreadsheet
from assignment import Lockers
import config

dv_attributes = [
    ['1000', '2000', '3000', '4000'],
    ['1', '2'],
    ['T', 'B']
]

# creating objects
s = Spreadsheet(config.TEST_SPREADSHEET_ID)
m = Match(s)
l = Lockers(s, dv_attributes)

# testing match class structure
partnerships = m.get_partners()
for a, b in partnerships:
    print(m.num2name[a], m.num2name[b])

# testing locker pointer handling
l.add_locker(['1000', '1', 'T'], '1103')
l.add_locker(['3000', '2', 'B'], '2205')
print(l.d)

print(l.get_locker(['1000', '2', 'T']))
