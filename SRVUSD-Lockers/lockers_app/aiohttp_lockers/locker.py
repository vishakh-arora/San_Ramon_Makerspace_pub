# Work with Python 3.6
import numpy as np
import pandas as pd

locker_building = {
    "4":"4000",
    "3":"3000",
    "2":"2000",
    "1":"1000"
}

locker_floor = {
    "2":"top",
    "1":"bottom"
}

locker_row = {
    "T":"top",
    "B":"bottom"
}

locker_T_B = {}
locker_sheet = []

broken_locks = [3063,3217,3234,3357,3092,4122,4220,4527,4659,4665,4247, 4025,4029,4146,4169,4171,4174,4198,4219,4229,4265,4285,4291,4305,4309,4317,4527]


def make_lockers(start, end):
    lockers = []
    for i in range(start,end,2):
        if (i not in broken_locks):
            lockers.append(str(i))
    return lockers

def append_lockers(top_bottom, start, end):
    lockers = []
    if (top_bottom == "T"):
        lockers = make_lockers(start+1, end+1)
    else:
        lockers = make_lockers(start, end+1)
    return lockers

def create_lockers():
    #fill locker dictionary

    for i in locker_building.keys():
        for j in locker_floor.keys():
            locker_T_B[i+j+"T"] = None
            locker_T_B[i+j+"B"] = None
    for i in locker_T_B:
        lockers = []
        #triple_lockers = []
        lockers.append(0)
        if (i[0] == "3"):
            if (i[1] == "1"):
                lockers = append_lockers(i[2],3001,3400)
            elif (i[1] == "2"):
                lockers = append_lockers(i[2],3501,3730)
        elif (i[0] == "2"):
            if (i[1] == "1"):
                lockers = append_lockers(i[2],2001,2358)
            elif (i[1] == "2"):
                lockers = append_lockers(i[2],2501,2716)
        elif (i[0] == "1"):
            if (i[1] == "1"):
                lockers = append_lockers(i[2],1001,1406)
            elif (i[1] == "2"):
                lockers = append_lockers(i[2],1501,1730)
        elif (i[0] == "4"):
            if (i[1] == "1"):
                lockers = append_lockers(i[2],4001,4335)
            elif (i[1] == "2"):
                lockers = append_lockers(i[2],4501,4678)

        locker_T_B[i] = lockers
create_lockers()
#print(locker_T_B)

for i in locker_T_B:
    for j in locker_T_B[i]:
        bldg = locker_building[i[0]]
        floor = locker_floor[i[1]]
        row = locker_row[i[2]]
        locker_sheet.append([j,"10,20,30",bldg,floor,row])
#print(locker_sheet)

locker_df = pd.DataFrame(np.asarray(locker_sheet),
                         columns=['locker number', 'locker combination', 'building', 'floor', 'row'])
#print(locker_df.head)

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('test_sheets/DVHS_lockers.xlsx', engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object.
locker_df.to_excel(writer, sheet_name='lockers', index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.save()
print("successfully saved lockers")
