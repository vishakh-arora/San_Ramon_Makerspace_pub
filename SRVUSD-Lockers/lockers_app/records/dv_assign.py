from assignment import Lockers, Match
import csv
import itertools
import numpy as np
from tabulate import tabulate

DVHS_ATTRIBUTES = [
    ['4000', '3000', '2000', '1000'],
    ['top', 'bottom'],
    ['top', 'bottom']
]

DVHS_LOCKERS = Lockers(DVHS_ATTRIBUTES)

with open('../snapshot_prefs4/dv_preferences.csv', newline='') as csvfile:
    DVHS_PREFS = list(csv.reader(csvfile, delimiter=','))

with open('DVHSLockerTest.csv', newline='') as csvfile:
    DVHS_LOCKER_LIST = list(csv.reader(csvfile, delimiter=','))

# with open('DVHSStudentTest.csv', newline='') as csvfile:
#     DVHS_STUDENT_LIST = list(csv.reader(csvfile, delimiter=','))

DVHS_PREFS = [[i.strip().lower() for i in j] for j in DVHS_PREFS]
DVHS_LOCKER_LIST = [[i.strip().lower() for i in j] for j in DVHS_LOCKER_LIST][1:]
# DVHS_STUDENT_LIST = [[i.strip().lower() for i in j] for j in DVHS_STUDENT_LIST][1:]
DVHS_STUDENT_LIST = list(set([i[6] for i in DVHS_PREFS]))

print('Read all CSVs.')

# print(*DVHS_PREFS[:20], sep='\n')
# print(*DVHS_LOCKER_LIST[:20], sep='\n')

print('Making lockers.')

for locker_number, combination, building, floor, row in DVHS_LOCKER_LIST:
    DVHS_LOCKERS.add_locker([building, floor, row], [locker_number])

print('Finished making lockers.')

# DVHS_PREFS = sorted(DVHS_PREFS, key=lambda x: (x[0], x[3]))
DVHS_ASSIGNMENTS = []

dv_locker_alternatives_12 = list(itertools.product(
    ['1000'],
    ['bottom', 'top'],
    ['top', 'bottom'],
))

dv_locker_alternatives_11 = list(itertools.product(
    ['2000'],
    ['bottom', 'top'],
    ['top', 'bottom'],
))

dv_locker_alternatives_10 = list(itertools.product(
    ['3000'],
    ['bottom', 'top'],
    ['top', 'bottom'],
))

dv_locker_alternatives_9 = list(itertools.product(
    ['4000'],
    ['bottom', 'top'],
    ['top', 'bottom'],
))

alternatives = {
    '9': dv_locker_alternatives_9,
    '10': dv_locker_alternatives_10,
    '11': dv_locker_alternatives_11,
    '12': dv_locker_alternatives_12
}

E2IP = {}
preferences_dict = {}
partnered = set()
partners = set()

for submit_time, partner_rank, school_id, grade, student_last_name, student_first_name, student_email, partner_last_name, partner_first_name, partner_email, building, floor, row in DVHS_PREFS:
    if student_email not in E2IP:
        E2IP[student_email] = [student_last_name, student_first_name, grade, building, floor, row]

# cleaning preferences: removing choices of students who did not fill out the form
for submit_time, partner_rank, school_id, grade, student_last_name, student_first_name, student_email, partner_last_name, partner_first_name, partner_email, building, floor, row in DVHS_PREFS:
    if student_email == partner_email:
        partners.add((student_email, partner_email))
        partnered.add(student_email)
        continue
    else:
        if student_email in preferences_dict:
            if partner_email in DVHS_STUDENT_LIST:
                preferences_dict[student_email][int(partner_rank)] = partner_email
            else:
                preferences_dict[student_email][int(partner_rank)] = None
        else:
            preferences_dict[student_email] = [None, None, None]
            if partner_email in DVHS_STUDENT_LIST:
                preferences_dict[student_email][int(partner_rank)] = partner_email
            else:
                preferences_dict[student_email][int(partner_rank)] = None

# shift over values
for i in preferences_dict:
    shifted = list(filter(lambda x: x is not None, preferences_dict[i]))
    preferences_dict[i] = shifted + [None for i in range(3-len(shifted))]
    # for i in preferences_dict[i]:
    #     if i in partnered:
    #         print('problem')

# make sure post-shift values are accurate
for i in preferences_dict:
    assert(len(preferences_dict[i]) == 3)

# matching (0, 0) people
for i in preferences_dict:
    first_choice = preferences_dict[i][0]
    if first_choice != None and preferences_dict[first_choice][0] == i and i not in partnered and first_choice not in partnered:
        partnered.add(i)
        partnered.add(first_choice)
        if (i, first_choice) not in partners and (first_choice, i) not in partners:
            partners.add((i, first_choice))

# check in
indiv = 0
double = 0
for a, b in partners:
    if a == b:
        indiv += 1
    else:
        double += 1

# removing partnered people from other's preferences and Munkressing them
for i in partnered:
    if i in preferences_dict:
        del preferences_dict[i]

for i in preferences_dict:
    for j in range(3):
        if preferences_dict[i][j] in partnered or preferences_dict[i][j] not in preferences_dict:
            preferences_dict[i][j] = None

# shift over values
for i in preferences_dict:
    shifted = list(filter(lambda x: x is not None, preferences_dict[i]))
    preferences_dict[i] = shifted + [None for i in range(3-len(shifted))]
    # for i in preferences_dict[i]:
    #     if i in partnered:
    #         print('problem')

# make sure post-shift values are accurate
x = 0
for i in preferences_dict:
    assert(len(preferences_dict[i]) == 3)
    if preferences_dict[i][0] == None:
        x  += 1

class_input = {
    '9': [],
    '10': [],
    '11': [],
    '12': []
}
for i in preferences_dict:
    grade = E2IP[i][2]
    reformatted_prefs = [i]+[j if j != None else '' for j in preferences_dict[i]]
    class_input[grade].append(reformatted_prefs)

for grade in class_input:
    dv_matcher = Match(class_input[grade]).get_partners()
    for student, partner in dv_matcher:
        double += 1
        if (student, partner) not in partners and (partner, student) not in partners:
            partnered.add(student)
            partnered.add(partner)
            partners.add((student, partner))

total_partner_stats = {
    '9': 0,
    '10': 0,
    '11': 0,
    '12': 0
}

for a, b in partners:
    assert(E2IP[a][2] == E2IP[b][2])
    total_partner_stats[E2IP[a][2]] += 1

print(tabulate([
    ['Total Individuals: ', indiv],
    ['Total Doubles: ', double],
    ['Total Students Partnered: ', len(partnered)],
    ['Total Students: ', len(DVHS_STUDENT_LIST)],
]))

print(total_partner_stats)

remaining_students = sorted(list(set(DVHS_STUDENT_LIST) - set(partnered)), key=lambda x: E2IP[x][2])
for i in remaining_students:
    print(i, E2IP[i][2])
