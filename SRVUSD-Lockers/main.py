from match import Match
from spreadsheet import Spreadsheet
import config

# creating objects
s = Spreadsheet(config.TEST_SPREADSHEET_ID)
m = Match(s)

# testing class structure
partnerships = m.get_partners()
for a, b in partnerships:
    print(m.num2name[a], m.num2name[b])
