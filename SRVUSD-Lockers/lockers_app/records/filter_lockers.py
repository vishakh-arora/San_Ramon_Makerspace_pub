import csv
import numpy as np

with open('CHSLockerTest.csv', newline='') as csvfile:
    ALL_LOCKERS = list(csv.reader(csvfile, delimiter=','))

with open('chsAssignment.csv', newline='') as csvfile:
    LOCKERS_NOW = list(csv.reader(csvfile, delimiter=','))

with open('chsLateAssignment.csv', newline='') as csvfile:
    LOCKERS_LATE = list(csv.reader(csvfile, delimiter=','))

ALL_LOCKERS_T = set({i[0] for i in ALL_LOCKERS})
ALL_OCCUPIED_LOCKERS = set()

for i in LOCKERS_NOW:
    assigned = i[-2]
    new = i[-1]
    ALL_OCCUPIED_LOCKERS.add(assigned)
    if new != '':
        ALL_OCCUPIED_LOCKERS.add(new)

for i in LOCKERS_LATE:
    assigned = i[-2]
    new = i[-1]
    ALL_OCCUPIED_LOCKERS.add(assigned)
    if new != '':
        ALL_OCCUPIED_LOCKERS.add(new)

UNOCCUPIED = ALL_LOCKERS_T - ALL_OCCUPIED_LOCKERS

final = []
for i in ALL_LOCKERS:
    if i[0] in UNOCCUPIED:
        final.append(i)

# print(*PREFS[:5], sep='\n')
# print(*ALL_LOCKERS[:5], sep='\n')
# print(*USED_LOCKERS[:5], sep='\n')

# USED_LOCKERS = set({i[4] if i[5] == '' else i[5] for i in USED_LOCKERS})
# NEW_LOCKERS = [i for i in ALL_LOCKERS if i[0] not in USED_LOCKERS]
# NEW_PREFS = [i for i in PREFS if i[0] > '2021-08-13 0:0:0.0+00:00']

# np.savetxt('CHS_REMAINING_LOCKERS.csv', np.array(NEW_LOCKERS), delimiter=',', fmt='%s')
np.savetxt('unoccupied_lockers_chs_8_25.csv', np.array(final), delimiter=',', fmt='%s')
