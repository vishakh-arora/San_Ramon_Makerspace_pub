from assignment import Lockers

dv = Lockers([
    ['1000', '2000', '3000', '4000'],
    ['top', 'bottom'],
    ['top', 'bottom']
])

for i in range(1000, 5000, 1000):
    dv.add_locker([str(i), 'top', 'top'], [i for i in range(i, i+10, 2)])
    dv.add_locker([str(i), 'top', 'bottom'], [i for i in range(i+10, i+20, 2)])
    dv.add_locker([str(i), 'bottom', 'top'], [i for i in range(i+20, i+30, 2)])
    dv.add_locker([str(i), 'bottom', 'bottom'], [i for i in range(i+30, i+40, 2)])

alternates = [
    ['1000', 'bottom', 'top'],
    ['1000', 'bottom', 'bottom'],
    ['1000', 'top', 'top'],
    ['1000', 'top', 'bottom']
]   

current = ['1000', 'bottom', 'bottom']
k = 0

for i in range(30):
    x = dv.get_locker(current)
    if x != None:
        print(x, current)
    else:
        next_idx = (alternates.index(current) + 1) % 4
        current = alternates[next_idx]
        # a locker location is emptied
        k += 1
    if k == len(alternates):
        print('all lockers assigned')
        break
