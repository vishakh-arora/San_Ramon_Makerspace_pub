from assignment import Lockers, Match
import csv
import itertools
import numpy as np

CHS_ATTRIBUTES = [
    ['1', '2', '3'],
    ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n'],
    ['top', 'middle', 'bottom']
]

CHS_LOCKERS = Lockers(CHS_ATTRIBUTES)

with open('CHS_LATE_PREFERENCES.csv', newline='') as csvfile:
    CHS_PREFS = list(csv.reader(csvfile, delimiter=','))

with open('CHS_REMAINING_LOCKERS.csv', newline='') as csvfile:
    CHS_LOCKER_LIST = list(csv.reader(csvfile, delimiter=','))

CHS_PREFS = [[i.strip().lower() for i in j] for j in CHS_PREFS]
# CHS_LOCKER_LIST = [[i.strip().lower() for i in j] for j in CHS_LOCKER_LIST][1:]
CHS_LOCKER_LIST = [[i.strip().lower() for i in j] for j in CHS_LOCKER_LIST]

# print(*CHS_PREFS[:20], sep='\n')
# print(*CHS_LOCKER_LIST[:20], sep='\n')

for locker_number, _, _, _, floor, bay, level in CHS_LOCKER_LIST:
    CHS_LOCKERS.add_locker([floor, bay, level], [locker_number])

CHS_PREFS = sorted(CHS_PREFS, key=lambda x: (x[0], x[3]))
CHS_ASSIGNMENTS = []

chs_locker_alternatives_12 = list(itertools.product(
    ['1'],
    ['top', 'middle', 'bottom'],
    ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm']
))

chs_locker_alternatives_12 = [(a, c, b) for a, b, c in chs_locker_alternatives_12]

chs_locker_alternatives_11 = list(itertools.product(
    ['1', '2'],
    ['top', 'middle', 'bottom'],
    ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n'],
))

chs_locker_alternatives_11 = [(a, c, b) for a, b, c in chs_locker_alternatives_11]

chs_locker_alternatives_11.remove(('1', 'n', 'top'))
chs_locker_alternatives_11.remove(('1', 'n', 'middle'))
chs_locker_alternatives_11.remove(('1', 'n', 'bottom'))

chs_locker_alternatives_10 = list(itertools.product(
    ['2'],
    ['top', 'middle', 'bottom'],
    ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']
))

chs_locker_alternatives_10 = [(a, c, b) for a, b, c in chs_locker_alternatives_10]

chs_locker_alternatives_9 = list(itertools.product(
    ['3'],
    ['top', 'middle', 'bottom'],
    ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']
))

chs_locker_alternatives_9 = [(a, c, b) for a, b, c in chs_locker_alternatives_9]

alternatives = {
    '9': chs_locker_alternatives_9,
    '10': chs_locker_alternatives_10,
    '11': chs_locker_alternatives_11,
    '12': chs_locker_alternatives_12
}

not_choice = 0
choice = 0

for submit_time, partner_rank, school_id, grade, student_last_name, student_first_name, student_email, partner_last_name, partner_first_name, partner_email, floor, bay, level in CHS_PREFS:
    alt = alternatives[grade]
    current = (floor, bay, level)
    current_idx = alt.index(current)
    track = current_idx

    new_lock = CHS_LOCKERS.get_locker(current)

    out_of_lockers = False

    if new_lock == None:
        not_choice += 1
    else:
        choice += 1

    while new_lock == None:
        current_idx = (current_idx + 1) % len(alt)
        current = alt[current_idx]
        new_lock = CHS_LOCKERS.get_locker(current)
        if current_idx == track:
            out_of_lockers = True
            break

    if out_of_lockers:
        print(f'OUT OF LOCKERS AT CAL HIGH FOR GRADE {grade}')

    else:
        CHS_ASSIGNMENTS.append([
            school_id,
            grade,
            student_last_name,
            student_first_name,
            student_email,
            partner_last_name,
            partner_first_name,
            partner_email,
            new_lock
        ])

for school_id, grade, student_last_name, student_first_name, student_email, partner_last_name, partner_first_name, partner_email, new_lock in CHS_ASSIGNMENTS:
    try:
        if grade == '9':
            assert(new_lock[0] == '3')
        if grade == '10':
            assert(new_lock[0] == '2')
        if grade == '11':
            assert(new_lock[0] == '1' or new_lock[0] == '2')
        if grade == '12':
            assert(new_lock[0] == '1')
    except:
        print(student_first_name, grade, new_lock)

np.savetxt('ch_late_assignment.csv', np.array(CHS_ASSIGNMENTS), delimiter=',', fmt='%s')
print(CHS_LOCKERS.d)

# print(f'{not_choice} STUDENTS DID NOT RECEIVE THEIR TOP CHOICE LOCKER.')
# print(f'{choice} STUDENTS RECEIVED THEIR TOP CHOICE LOCKER')
# print(f'{(choice/(not_choice+choice))*100}% SUCCESS RATE')
# print(f'{not_choice+choice} TOTAL STUDENTS')
# print(f'{len(CHS_PREFS)} TOTAL PREFERENCES (CHECK)')
