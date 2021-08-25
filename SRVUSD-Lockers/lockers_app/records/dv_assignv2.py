from assignment import Lockers, Match
import csv
import itertools
import numpy as np
from tabulate import tabulate
from datetime import datetime

DVHS_ATTRIBUTES = [
    ['4000', '3000', '2000', '1000'],
    ['top', 'bottom'],
    ['top', 'bottom']
]

DVHS_LOCKERS = Lockers(DVHS_ATTRIBUTES)

with open('DVHS_LATE_PREFERENCES.csv', newline='') as csvfile:
    DVHS_PREFS = list(csv.reader(csvfile, delimiter=','))

with open('DVHS_REMAINING_LOCKERS.csv', newline='') as csvfile:
    DVHS_LOCKER_LIST = list(csv.reader(csvfile, delimiter=','))

# with open('DVHSStudentTest.csv', newline='') as csvfile:
#     DVHS_STUDENT_LIST = list(csv.reader(csvfile, delimiter=','))
# 189989@students.srvusd.net
# 212768@students.srvusd.net


DVHS_PREFS = [[i.strip().lower() for i in j] for j in DVHS_PREFS]
# for i in DVHS_PREFS.copy():
#     if i[6] == '189989@students.srvusd.net' or i[6] == '212768@students.srvusd.net':
#         DVHS_PREFS.remove(i)

# sjebm = '2021-07-30 20:11:16.419690+00:00'

# manuals = [
#     [sjebm, '0', '0', '12', 'xie', 'ashlee', '189348@students.srvusd.net', 'xie', 'ashlee', '189348@students.srvusd.net', '1000', 'top', 'top'],
#     [sjebm, '0', '0', '9', 'vicente', 'valdez', '206345@students.srvusd.net', 'subramanian', 'sundar', '206283@students.srvusd.net', '4000', 'top', 'top'],
#     [sjebm, '0', '0', '9', 'lovejoy', 'andrew', '206325@students.srvusd.net', 'mui', 'jude', '206253@students.srvusd.net', '4000', 'top', 'top'],
#     [sjebm, '0', '0', '9', 'horn', 'eliana', '207621@students.srvusd.net', 'chen', 'evey', '207944@students.srvusd.net', '4000', 'bottom', 'bottom'],
#     [sjebm, '0', '0', '10', 'senthilkumar', 'rithika', '202895@students.srvusd.net', 'senthilkumar', 'rithika', '202895@students.srvusd.net', '3000', 'bottom', 'top'],
#     [sjebm, '0', '0', '9', 'pramanik', 'dhriti', '212768@students.srvusd.net', 'patel', 'shreeya', '206655@students.srvusd.net', '4000', 'bottom', 'bottom'],
#     [sjebm, '1', '0', '9', 'pramanik', 'dhriti', '212768@students.srvusd.net', 'miryala', 'adhya', '208313@students.srvusd.net', '4000', 'bottom', 'bottom'],
#     [sjebm, '2', '0', '9', 'pramanik', 'dhriti', '212768@students.srvusd.net', 'shrinithi', 'giridharan', '222621@students.srvusd.net', '4000', 'bottom', 'bottom'],
#     [sjebm, '0', '0', '10', 'bekele', 'nicholas', 'ginamik3@gmail.com', 'bekele', 'nicholas', 'ginamik3@gmail.com', '3000', 'bottom', 'top'],
#     [sjebm, '0', '0', '9', 'shunmuga', 'smrethi', '218463@students.srvusd.net', 'arunsaravanakumar', 'srishreya', '241783@students.srvusd.net', '4000', 'bottom', 'top'],
#     [sjebm, '1', '0', '9', 'shunmuga', 'smrethi', '218463@students.srvusd.net', 'ruys', 'isabelle', '206814@students.srvusd.net', '4000', 'bottom', 'top'],
#     [sjebm, '0', '0', '10', 'kleber', 'sydney', 'moonkleber@gmail.com', 'kleber', 'sydney', 'moonkleber@gmail.com', '3000', 'bottom', 'top'],
#     [sjebm, '0', '0', '9', 'romero', 'cecilia', 'cpjr2006@gmail.com', 'romero', 'cecilia', 'cpjr2006@gmail.com', '4000', 'bottom', 'top']
# ]
#
# for i in manuals:
#     DVHS_PREFS.append(i)

DVHS_PREFS = sorted(DVHS_PREFS, key=lambda x: x[0])
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

class_stats = {
    '9': [0 for i in range(4)], # total number of students assigned, number of individual lockers, number of partner lockers, total students
    '10': [0 for i in range(4)],
    '11': [0 for i in range(4)],
    '12': [0 for i in range(4)]
}

for submit_time, partner_rank, school_id, grade, student_last_name, student_first_name, student_email, partner_last_name, partner_first_name, partner_email, building, floor, row in DVHS_PREFS:
    if student_email not in E2IP:
        class_stats[grade][3] += 1
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
# for i in preferences_dict:
    # shifted = list(filter(lambda x: x is not None, preferences_dict[i]))
    # preferences_dict[i] = shifted + [None for i in range(3-len(shifted))]
    # for i in preferences_dict[i]:
    #     if i in partnered:
    #         print('problem')

# make sure post-shift values are accurate
# for i in preferences_dict:
    # assert(len(preferences_dict[i]) == 3)

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

for i in class_input:
    class_partners = Match(class_input[i]).get_partners()
    for a, b in class_partners:
        partnered.add(a)
        partnered.add(b)
        if (a, b) not in partners and (b, a) not in partners:
            partners.add((a, b))
    print(f'Finished Grade {i}.')

# print(*partners, sep='\n')
remaining_students = sorted(list(set(DVHS_STUDENT_LIST) - set(partnered)), key=lambda x: E2IP[x][2])
while remaining_students:
    if len(remaining_students) > 1 and E2IP[remaining_students[0]][2] == E2IP[remaining_students[1]][2]:
        partnered.add(remaining_students[0])
        partnered.add(remaining_students[1])
        partners.add((remaining_students[0], remaining_students[1]))
        remaining_students.pop(0)
        remaining_students.pop(0)
    else:
        partnered.add(remaining_students[0])
        partners.add((remaining_students[0], remaining_students[0]))
        remaining_students.pop(0)
    # print(remaining_students)
    # print()

x = set()
# checking if grades are the same and partnerships are bipartite
for a, b in partners:
    if a in x:
        print('wrong')
    if b in x:
        print('wrong')
    x.add(a)
    x.add(b)
    if a and b in E2IP:
        assert(E2IP[a][2] == E2IP[b][2])
    else:
        print(a, b)
    grade = E2IP[a][2]
    if a == b:
        class_stats[grade][0] += 1
        class_stats[grade][1] += 1
    else:
        class_stats[grade][0] += 2
        class_stats[grade][2] += 1

print(*class_stats.items(), sep='\n')
print(len(partnered))
print(len(DVHS_STUDENT_LIST))

for student_email, partner_email in partners:
    student_last_name, student_first_name, grade, building, floor, level = E2IP[student_email]
    partner_last_name, partner_first_name, grade, _, _, _ = E2IP[partner_email]

    alt = alternatives[grade]
    current = (building, floor, level)
    current_idx = alt.index(current)
    track = current_idx

    new_lock = DVHS_LOCKERS.get_locker(current)

    out_of_lockers = False

    while new_lock == None:
        current_idx = (current_idx + 1) % len(alt)
        current = alt[current_idx]
        new_lock = DVHS_LOCKERS.get_locker(current)
        if current_idx == track:
            out_of_lockers = True
            break

    if out_of_lockers:
        print(f'OUT OF LOCKERS AT DV HIGH FOR GRADE {grade}')

    else:
        DVHS_ASSIGNMENTS.append([
            0,
            grade,
            student_last_name,
            student_first_name,
            student_email,
            partner_last_name,
            partner_first_name,
            partner_email,
            new_lock
        ])
        if student_email != partner_email:
            DVHS_ASSIGNMENTS.append([
                0,
                grade,
                partner_last_name,
                partner_first_name,
                partner_email,
                student_last_name,
                student_first_name,
                student_email,
                new_lock
            ])

# DVHS_ASSIGNMENTS.append([
#     0,
#     '9',
#     'Negrete-Lopez',
#     'Hezekiah',
#     '189989@students.srvusd.net',
#     'Negrete-Lopez',
#     'Hezekiah',
#     '189989@students.srvusd.net',
#     '4330'
# ])

for _, grade, _, _, _, _, _, _, new_lock in DVHS_ASSIGNMENTS:
    if grade == '9':
        assert(new_lock[0] == '4')
    if grade == '10':
        assert(new_lock[0] == '3')
    if grade == '11':
        assert(new_lock[0] == '2')
    if grade == '12':
        assert(new_lock[0] == '1')

appearances = {i:0 for i in DVHS_STUDENT_LIST}
appearances['189989@students.srvusd.net'] = 0
for _, _, _, _, a, _, _, b, _ in DVHS_ASSIGNMENTS:
    appearances[a] += 1
    appearances[b] += 1

for i in appearances:
    try:
        assert(appearances[i] == 2)
    except AssertionError:
        print(i)

print(DVHS_LOCKERS.d)

np.savetxt('dv_late_assignment.csv', np.array(DVHS_ASSIGNMENTS), delimiter=',', fmt='%s')
