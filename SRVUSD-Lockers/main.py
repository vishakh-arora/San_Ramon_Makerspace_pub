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

# testing class structure
partnerships = m.get_partners()
for a, b in partnerships:
    print(m.num2name[a], m.num2name[b])
