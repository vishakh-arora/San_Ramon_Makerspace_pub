import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from aiohttp import web, web_request
import aiohttp_jinja2
from aiohttp_session import get_session, new_session
from init_db import *
from db import *
from google.oauth2 import id_token
from google.auth.transport import requests
from multidict import MultiDict
from sqlalchemy import and_, or_
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import random
import itertools
import re
import math

# temp_storage = {'partner':[None for i in range(3)]}
CLIENT_ID = '745601090768-kosoi5uc466i9ns0unssv5h6v8ilk0a8.apps.googleusercontent.com'

conn = initialize_db()

# (TEST)
# clear existing entries
conn.execute(school.delete())
conn.execute(student.delete())
conn.execute(admin.delete())
conn.execute(preference.delete())
conn.execute(organization.delete())
conn.execute(org_name.delete())

# create hardcoded entries (TEST)
# creating organizations w names
# conn.execute(org_name.insert({
    # 'id': 0,
    # 'hierarchy_1': 'building',
    # 'hierarchy_2': 'floor',
    # 'hierarchy_3': 'level'
# }))
# conn.execute(org_name.insert({
    # 'id': 1,
    # 'hierarchy_1': 'floor',
    # 'hierarchy_2': 'bay',
    # 'hierarchy_3': 'level'
# }))
# creating school
conn.execute(school.insert({
    'id': 0,
    'name': 'Dougherty Valley High School',
    # 'org_id': 0,
    'students_spreadsheet_uploaded': False,
    'lockers_spreadsheet_uploaded': False,
    'preassignments_spreadsheet_uploaded': False
}))
conn.execute(school.insert({
    'id': 1,
    'name': 'California High School',
    # 'org_id': 1,
    'students_spreadsheet_uploaded': False,
    'lockers_spreadsheet_uploaded': False,
    'preassignments_spreadsheet_uploaded': False
}))

# creating student users
# conn.execute(student.insert({
#     'id': 0,
#     'email': 'dh.skumar@students.srvusd.net',
#     'first_name': 'shubham',
#     'last_name': 'kumar',
#     'school_id': 0,
#     'grade': 12
# }))
# conn.execute(student.insert({
#     'id': 1,
#     'email': 'dh.varora@students.srvusd.net',
#     'first_name': 'vishakh',
#     'last_name': 'arora',
#     'school_id': 0,
#     'grade': 12
# }))
# conn.execute(student.insert({
#     'id': 2,
#     'email': 'dh.cnookala@students.srvusd.net',
#     'first_name': 'chaitanya',
#     'last_name': 'nookala',
#     'school_id': 0,
#     'grade': 12
# }))
# conn.execute(student.insert({
#     'id': 3,
#     'email': 'dh.smehrotra@students.srvusd.net',
#     'first_name': 'shlok',
#     'last_name': 'mehrotra',
#     'school_id': 0,
#     'grade': 12
# }))
# conn.execute(student.insert({
#     'id': 4,
#     'email': 'dh.abhakat@students.srvusd.net',
#     'first_name': 'anay',
#     'last_name': 'bhakat',
#     'school_id': 0,
#     'grade': 12
# }))
# conn.execute(student.insert({
#     'id': 5,
#     'email': 'ch.student1@students.srvusd.net',
#     'first_name': 'CalStudent1',
#     'last_name': 'Test',
#     'school_id': 1,
#     'grade': 12
# }))
# conn.execute(student.insert({
#     'id': 6,
#     'email': 'ch.student2@students.srvusd.net',
#     'first_name': 'CalStudent2',
#     'last_name': 'Test',
#     'school_id': 1,
#     'grade': 12
# }))
# creating admin user
conn.execute(admin.insert({
    'id': 0,
    'email':'eliddle@srvusd.net',
    'prefix': 'Mr.',
    'last_name': 'liddle',
    'school_id': 0
}))
# creating organizations
# options = {
#     0: {
#         'building': ['1000', '2000', '3000', '4000'],
#         'floor': ['top', 'bottom'],
#         'level': ['top', 'bottom']
#     },
#     1: {
#         'floor': ['top', 'bottom'],
#         'bay': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'],
#         'level': ['top', 'bottom']
#     }
# }

# x = 0
# for i in options: #(0, 1)
#     prod = list(itertools.product(*[j for j in list(options[i].values())]))
#     for a, b, c in prod:
#         conn.execute(organization.insert({
#             'id': x,
#             'school_id': i,
#             'hierarchy_1': a,
#             'hierarchy_2': b,
#             'hierarchy_3': c
#         }))
#         x += 1

def preview_db():
    # preview tables
    school_request = conn.execute(school.select())
    student_request = conn.execute(student.select())
    admin_request = conn.execute(admin.select())
    preference_request = conn.execute(preference.select())
    organization_request = conn.execute(organization.select())
    org_name_request = conn.execute(org_name.select())

    print()
    print()
    print('SCHOOL PREVIEW:', *school_request.fetchall(), sep='\n')
    print('STUDENT PREVIEW:', *student_request.fetchall(), sep='\n')
    print('ADMIN PREVIEW:', *admin_request.fetchall(), sep='\n')
    print('PREFERENCE PREVIEW:', *preference_request.fetchall(), sep='\n')
    print('ORGANIZATION PREVIEW:', *organization_request.fetchall(), sep='\n')
    print('ORG_NAME PREVIEW:', *org_name_request.fetchall(), sep='\n')
    print()
    print()

async def index(request):
    preview_db()

    # creating message dictionary
    messages = {
        'success': [],
        'danger': [],
        'info': []
    }

    # getting user session
    session = await get_session(request)
    # print('Index Session:', session)

    # user is not logged in
    if session.get('authorized') == None:
        # creating context
        ctx_index = {
            'session': session,
            'messages': messages
        }
        # creating response
        response = aiohttp_jinja2.render_template(
            'index.html',
            request,
            ctx_index
        )
        # rendering for user
        return response

    # user is logged in
    if session.get('authorized'):

        # user is a student
        if session['role'] == 'student':
            preference_request = conn.execute(preference.select())
            # print()
            # print('PREFERENCE PREVIEW:', *preference_request.fetchall(), sep='\n')
            # print()
            # populate these with values from database if they exist
            # EXAMPLES:
            # student_list = [
            #     'oren (dh.oren@students.srvusd.net)',
            #     'kjev (dh.kjev@students.srvusd.net)',
            #     'veggu (dh.veggu@students.srvusd.net)',
            #     'shubhert (dh.shubhert@students.srvusd.net)'
            # ]
            # organization_fields = {
            #     'building': ['1000', '2000', '3000', '4000'],
            #     'floor': ['top', 'bottom'],
            #     'row': ['top', 'bottom']
            # }

            # querying database for student options (grade & school must be the same)
            # exclude the logged in student from the list
            student_db_request = conn.execute(
                student.select().
                    where(
                        and_(
                        student.c.id != session['id'],
                        student.c.grade == session['grade'],
                        student.c.school_id == session['school_id']
                        )
                    )
                )

            # create dict to be passed into jinja prepopulated with student ids and info
            # i[0] is id, i[2] is first name, i[3] is last name and i[1] is email
            student_options = {
                i[0]: f'{i[2].capitalize()} {i[3].capitalize()} ({i[1]})'
                for i in student_db_request
            }

            # querying database for existing student preferences
            # sort preferences by partner rank (least to greatest)

            preference_request = conn.execute(preference.select())
            # print('PREFERENCE PREVIEW:', *preference_request.fetchall(), sep='\n')

            preference_db_request = conn.execute(
                preference.select().
                    where(preference.c.student_id == session['id'])
                ).fetchall()

            latest_preference_db_request = sorted(preference_db_request, key=lambda i: i[3])

            # create list to be passed into jinja prepopulated with student name and email
            partner_preferences = [None, None, None]
            for i in latest_preference_db_request:
                s = conn.execute(
                    student.select().
                        where(student.c.id == i[2])
                ).first()
                partner_preferences[i[3]] = s[0]

            # querying database for locker options
            # ya buddy this one changed slihjtly oren
            # finding org_id for school
            # school_db_request = conn.execute(
            # school.select().
            #     where(school.c.id == session['school_id'])
            # ).first()

            # org_id = school_db_request[0][2]
            # org_id = 0

            # finding hierarchy names for user's school
            hierarchies = list(filter(None, conn.execute(
            org_name.select().
                where(org_name.c.school_id == session['school_id'])
            ).first()[1:]))

            # finding options for each hierarchy at the user's school
            hierarchy_db_request = conn.execute(
            organization.select().
                where(organization.c.school_id == session['school_id'])
            ).fetchall()

            hierarchy_db_request = [list(filter(None, i[2:])) for i in hierarchy_db_request]

            # print()
            # print(*hierarchy_db_request, sep='\n')
            # print()

            hierarchy_options = [set() for i in range(len(hierarchies))]

            for i in hierarchy_db_request: # (1000, top, top)
                for j in range(len(i)):
                    hierarchy_options[j].add(i[j])

            # print()
            # print(*hierarchy_options, sep='\n')
            # print()

            hierarchy_options = [sorted(list(i)) for i in hierarchy_options]

            locker_options = {
                i: j
                for i, j in zip(hierarchies, hierarchy_options)
            }

            # print()
            # print(locker_options)
            # print()

            # querying database for locker preferences
            # finding org_id for school
            if len(latest_preference_db_request) != 0:
                locker_preference_id = latest_preference_db_request[0][-1]
                locker_db_request = conn.execute(
                    organization.select().
                        where(organization.c.id == locker_preference_id)
                    ).first()
                lp = filter(None, locker_db_request[2:])
            else:
                lp = [None, None, None]
            locker_preferences = {
                i: j
                for i, j in zip(hierarchies, lp)
            }

            # creating context
            ctx_students = {
                'student_options': student_options,
                'partner_preferences': partner_preferences, # temp_storage['partner'], (TEST)
                'locker_preferences': locker_preferences, # ex: {'building':1000, 'floor':1, 'row':1}
                'locker_options': locker_options, # ex: {'building':[1000, 2000, 3000, 4000], 'floor':[1, 2], 'row':[1, 2]}
                'session': session,
                'messages': messages,
                'issues': [None, None, None]
            }

            # get request
            if request.method == 'GET':
                # creating response
                response = aiohttp_jinja2.render_template(
                    'student.html',
                    request,
                    ctx_students
                )
                # rendering for user
                return response

            # post request
            if request.method == 'POST':
                # loading post request data
                data = await request.post()

                # save data into database
                # EXAMPLE: (TEST)
                # temp_storage['partner'][0] = data['preference1']
                # temp_storage['partner'][1] = data['preference2']
                # temp_storage['partner'][2] = data['preference3']

                # invalid input: same choices for mulitple fields
                user_form_response = [
                    data['preference1'],
                    data['preference2'],
                    data['preference3']
                ]
                data_proc = list(filter(lambda x: x!='none', user_form_response))

                # print('USER RESPONSE', data_proc)

                if len(set(data_proc)) != len(data_proc):
                    messages['danger'].append('Please choose different people for each preference.')
                    # prefilling fields
                    ctx_students['locker_preferences'] = {
                        i: data[i]
                        for i in hierarchies
                    }
                    ctx_students['partner_preferences'] = [int(i) for i in user_form_response]
                    # checking for duplicate names
                    for i in range(3):
                        for j in range(i, 3):
                            if i == j:
                                continue
                            if user_form_response[i] == user_form_response[j]:
                                ctx_students['issues'][i] = True
                                ctx_students['issues'][j] = True
                    response = aiohttp_jinja2.render_template(
                        'student.html',
                        request,
                        ctx_students
                    )
                    # rendering for user
                    return response

                # TEMPORARY
                # MAN I DID ET DUMD
                # NEED TO FIGURE OUT A WAY TO DEAL WITH VARIABLE HIERARCHIES
                # hierarchies: names of the hierarchies (building, floor, level etc.)

                criteria_hierarchy_query = [
                    [organization.c.hierarchy_1, None],
                    [organization.c.hierarchy_2, None],
                    [organization.c.hierarchy_3, None],
                    [organization.c.hierarchy_4, None],
                    [organization.c.hierarchy_5, None],
                    [organization.c.school_id, session['school_id']]
                ]

                for i in range(len(hierarchies)):
                    criteria_hierarchy_query[i][1] = data[hierarchies[i]]

                criteria_hierarchy_query = [i[0] == i[1] for i in criteria_hierarchy_query]

                locker_db_request = conn.execute(
                    organization.select().
                        where(
                            and_(*criteria_hierarchy_query)
                        )
                    ).first()

                locker_preference_id = locker_db_request[0]

                criteria_preference1_upsert = [
                    preference.c.student_id == session['id'],
                    or_(
                        preference.c.partner_id == data['preference1'],
                        preference.c.partner_rank == 0
                    )
                ]

                # TEMPORARY
                # NEED TO FIGURE OUT UPSERTS
                # FIGURED IT OUT OREN
                upsert(conn, preference, criteria_preference1_upsert, {
                    'submit_time': datetime.now(timezone.utc),
                    'student_id': session['id'],
                    'partner_id': data['preference1'],
                    'partner_rank': 0,
                    'locker_pref': locker_preference_id,
                })

                # preference_request = conn.execute(preference.select())

                if data['preference2'] != 'none':
                    criteria_preference2_upsert = [
                        preference.c.student_id == session['id'],
                        or_(
                            preference.c.partner_id == data['preference2'],
                            preference.c.partner_rank == 1
                        )
                    ]
                    upsert(conn, preference, criteria_preference2_upsert, {
                        'submit_time': datetime.now(timezone.utc),
                        'student_id': session['id'],
                        'partner_id': data['preference2'],
                        'partner_rank': 1,
                        'locker_pref': locker_preference_id,
                    })
                else:
                    conn.execute(
                        preference.delete().where(
                            and_(
                                preference.c.student_id == session['id'],
                                preference.c.partner_rank == 1
                            )
                        )
                    )

                if data['preference3'] != 'none':
                    criteria_preference3_upsert = [
                        preference.c.student_id == session['id'],
                        or_(
                            preference.c.partner_id == data['preference3'],
                            preference.c.partner_rank == 2
                        )
                    ]
                    upsert(conn, preference, criteria_preference3_upsert, {
                        'submit_time': datetime.now(timezone.utc),
                        'student_id': session['id'],
                        'partner_id': data['preference3'],
                        'partner_rank': 2,
                        'locker_pref': locker_preference_id,
                    })
                else:
                    conn.execute(
                        preference.delete().where(
                            and_(
                                preference.c.student_id == session['id'],
                                preference.c.partner_rank == 2
                            )
                        )
                    )

                # message to reload
                # messages['success'].append('Saved successfully. Reload to view preferences.')
                # creating response
                # response = aiohttp_jinja2.render_template(
                #     'student.html',
                #     request,
                #     ctx_students
                # )
                return web.HTTPFound(location=request.app.router['index'].url_for())


        # user is an administrator
        if session['role'] == 'admin':
            # creating context
            # populate these with values from database if they exist
            fields = ['students', 'lockers', 'preassignments']

            ctx_admin = {
                'fields': fields,
                'sheets':{
                    i:{
                        'saved': False,
                        'filename': None,
                        'data': None,
                        'messages': []
                    }
                    for i in fields
                },
                'session': session,
                'messages': messages
            }

            # check to see if sheets have been uploaded
            school_db_request = conn.execute(
                school.select().where(
                    school.c.id == session['school_id']
                )
            ).first()[2:]

            # print(school_db_request)

            for i in range(3):
                if not school_db_request[i]:
                    ctx_admin['sheets'][fields[i]]['messages'].append(f'Missing {fields[i].capitalize()} Spreadsheet.')
                else:
                    ctx_admin['sheets'][fields[i]]['saved'] = True
                    # ctx_admin['sheets'][fields[i]]['messages'].append(f'Accepted {fields[i].capitalize()} Spreadsheet.')
                    ctx_admin['sheets'][fields[i]]['filename'] = school_db_request[i+3]

            # get request
            if request.method == 'GET':
                # creating response
                response = aiohttp_jinja2.render_template(
                    'admin.html',
                     request,
                     ctx_admin
                )
                # rendering for user
                return response

            # post request
            if request.method == 'POST':
                # loading post request data
                data = await request.post()

                # validate data
                # validation variables
                preassignments_is_valid = True
                lockers_is_valid = True
                students_is_valid = True

                # validation loop
                for field in fields:
                    response_sheet = data.get(field)

                    # print()
                    # print('RESPONSE SHEET: \n', response_sheet, type(response_sheet))
                    # print()

                    # if the submission is a valid file
                    if type(response_sheet) == web_request.FileField:
                        # get file name and file info to extract from
                        sheet_filename = response_sheet.filename
                        sheet_file = response_sheet.file

                        # open file for validation
                        df = pd.read_excel(sheet_file, engine='openpyxl')
                        sheet_columns = list(df.columns)
                        sheet_data = df.to_numpy()

                        # debug
                        # print()
                        # print('2D ARRAY SHEET DATA: \n', sheet_data)
                        # print()
                        #
                        # print()
                        # print('SHEET COLUMNS:', sheet_columns)
                        # print()

                        # validation for students spreadsheet
                        if field == 'students':
                            # reset on resubmission
                            # ctx_admin['sheets'][field]['saved'] = False
                            ctx_admin['sheets'][field]['messages'] = [f'Errors found in {sheet_filename} {field} spreadsheet.']

                            # conn.execute(
                            #     school.update().where(and_(
                            #         school.c.id == session['school_id']
                            #         )
                            #     ).values(
                            #         students_spreadsheet_uploaded = False,
                            #         students_spreadsheet_filename = None
                            #     )
                            # )
                            # try validation
                            try:
                                # wrong number of columns
                                if len(sheet_columns) != 4:
                                    students_is_valid = False
                                    ctx_admin['sheets'][field]['messages'].append(f'Incorrect number of columns. Expected 4, received {len(sheet_columns)}.')
                                else:
                                    for i in range(len(sheet_data)):
                                        row = sheet_data[i]
                                        # check for valid emails
                                        if not re.match('[^@]+@[^@]+\.[^@]+', row[3]):
                                            students_is_valid = False
                                            ctx_admin['sheets'][field]['messages'].append(f'Invalid e-mail in row {i+1}, received {row[3]}.')
                                            break
                                        # check for numerical grade values
                                        if not type(row[2]) == int:
                                            students_is_valid = False
                                            ctx_admin['sheets'][field]['messages'].append(f'Invalid grade value in row {i+1}, received {row[2]}.')
                                            break
                                        blank = False
                                        # check for any blank values
                                        for j in range(len(row)):
                                            if type(row[j]) == float:
                                                students_is_valid = False
                                                ctx_admin['sheets'][field]['messages'].append(f'Blank entry in row {i+1}, column {j+1}.')
                                                blank = True
                                                break
                                        if blank:
                                            break
                            # problem with spreadsheet, but not identified
                            except:
                                students_is_valid = False
                                ctx_admin['sheets'][field]['messages'].append(f'Please follow template carefully. Submission not recognized.')
                            if students_is_valid:
                                ctx_admin['sheets'][field]['messages'] = []
                                conn.execute(
                                    school.update().where(and_(
                                        school.c.id == session['school_id']
                                        )
                                    ).values(
                                        students_spreadsheet_uploaded = True,
                                        students_spreadsheet_filename = sheet_filename
                                    )
                                )
                                # print('\n STUDENT SHEET DATA \n')
                                # for i in sheet_data:
                                #     print(i)
                                # print('\n\n')

                                for last_name, first_name, grade, email in sheet_data:
                                    criteria = [student.c.email == email]
                                    upsert(conn, student, criteria, {
                                        'email': email,
                                        'first_name': first_name,
                                        'last_name': last_name,
                                        'school_id': session['school_id'],
                                        'grade': grade
                                    })

                                # print('INSERTED STUDENT DATA: \n')
                                # student_request = conn.execute(student.select())
                                # print('STUDENT PREVIEW:', *student_request.fetchall(), sep='\n')
                                # print()


                        # validation for lockers spreadsheet
                        if field == 'lockers':
                            # reset on resubmission
                            # ctx_admin['sheets'][field]['saved'] = False
                            ctx_admin['sheets'][field]['messages'] = [f'Errors found in {sheet_filename} {field} spreadsheet.']
                            # conn.execute(
                            #     school.update().where(and_(
                            #         school.c.id == session['school_id']
                            #         )
                            #     ).values(
                            #         lockers_spreadsheet_uploaded = False,
                            #         lockers_spreadsheet_filename = None
                            #     )
                            # )
                            # try validation
                            try:
                                # too many hierarchy values
                                if len(sheet_columns)-2 > 5 or len(sheet_columns) < 2:
                                    lockers_is_valid = False
                                    ctx_admin['sheets'][field]['messages'].append(f'Incorrect number of location attribute values. Expected between 2 and 5, received {len(sheet_columns)}.')
                                else:
                                    for i in range(len(sheet_data)):
                                        row = sheet_data[i]
                                        # check if locker number is numeric
                                        if not type(row[0]) == int:
                                            lockers_is_valid = False
                                            ctx_admin['sheets'][field]['messages'].append(f'Invalid locker number value in row {i+1}, received {row[0]}.')
                                            break
                                        # check if locker combo has three values
                                        if type(row[1]) != str or len(row[1].split(',')) != 3:
                                            lockers_is_valid = False
                                            ctx_admin['sheets'][field]['messages'].append(f'Invalid locker combination value in row {i+1}. Should be formatted \'#,#,#\', received {row[1]}.')
                                            break
                                        blank = False
                                        # check for any blank values
                                        for j in range(len(row)):
                                            if type(row[j]) == float:
                                                lockers_is_valid = False
                                                ctx_admin['sheets'][field]['messages'].append(f'Blank entry in row {i+1}, column {j+1}.')
                                                blank = True
                                                break
                                        if blank:
                                            break
                            # problem with spreadsheet, but not identified
                            except:
                                students_is_valid = False
                                ctx_admin['sheets'][field]['messages'].append(f'Please follow template carefully. Submission not recognized.')
                            if lockers_is_valid:
                                # validated frontend and database
                                ctx_admin['sheets'][field]['messages'] = []
                                conn.execute(
                                    school.update().where(and_(
                                        school.c.id == session['school_id']
                                        )
                                    ).values(
                                        lockers_spreadsheet_uploaded = True,
                                        lockers_spreadsheet_filename = sheet_filename
                                    )
                                )

                                # input data storage
                                num_hierarchies = sheet_data.shape[1]-2
                                locker_options = [set() for i in range(num_hierarchies)]

                                # create organization data for db
                                for i in sheet_data:
                                    locker = i[2:]
                                    for j in range(num_hierarchies):
                                        # if type(locker[j]) == str:
                                            # locker[j].lower()
                                        locker_options[j].add(str(locker[j]).lower())

                                organization_options = itertools.product(*locker_options)

                                # add in organizations into db
                                criteria_hierarchy_upsert = [
                                    [organization.c.hierarchy_1, 'hierarchy_1', None],
                                    [organization.c.hierarchy_2, 'hierarchy_2', None],
                                    [organization.c.hierarchy_3, 'hierarchy_3', None],
                                    [organization.c.hierarchy_4, 'hierarchy_4', None],
                                    [organization.c.hierarchy_5, 'hierarchy_5', None],
                                    [organization.c.school_id, 'school_id', session['school_id']]
                                ]

                                for i in organization_options:
                                    for j in range(num_hierarchies):
                                        criteria_hierarchy_upsert[j][2] = i[j]
                                    temp_criteria_hierarchy_upsert = [i[0] == i[2] for i in criteria_hierarchy_upsert]
                                    organization_values = {
                                        i[1]: i[2]
                                        for i in criteria_hierarchy_upsert
                                    }
                                    organization_values['school_id'] = session['school_id']
                                    upsert(conn, organization, temp_criteria_hierarchy_upsert, organization_values)

                                # add in organization names into db
                                hierarchy_name_upsert = [
                                    ['hierarchy_1', None],
                                    ['hierarchy_2', None],
                                    ['hierarchy_3', None],
                                    ['hierarchy_4', None],
                                    ['hierarchy_5', None],
                                    ['school_id', session['school_id']]
                                ]

                                for i in range(num_hierarchies):
                                    hierarchy_name_upsert[i][1] = sheet_columns[i+2].lower()

                                organization_name_values = {
                                    i[0]: i[1]
                                    for i in hierarchy_name_upsert
                                }
                                upsert(conn, org_name, [org_name.c.school_id == session['school_id']], organization_name_values)

                                # add in the lockers
                                # GODDA DO THIS ONE STILL G


                        # validation for preassignments spreadsheet
                        if field == 'preassignments':
                            # reset on resubmission
                            # ctx_admin['sheets'][field]['saved'] = False
                            ctx_admin['sheets'][field]['messages'] = [f'Errors found in {sheet_filename} {field} spreadsheet.']
                            # conn.execute(
                            #     school.update().where(and_(
                            #         school.c.id == session['school_id']
                            #         )
                            #     ).values(
                            #         preassignments_spreadsheet_uploaded = False,
                            #         preassignments_spreadsheet_filename = None
                            #     )
                            # )
                            try:
                                if len(sheet_columns) != 3:
                                    preassignments_is_valid = False
                                    ctx_admin['sheets'][field]['messages'].append(f'Incorrect number of columns. Expected 4, received {len(sheet_columns)}.')
                                else:
                                    for i in range(len(sheet_data)):
                                        row = sheet_data[i]
                                        if not (re.match('[^@]+@[^@]+\.[^@]+', row[0]) or re.match('[^@]+@[^@]+\.[^@]+', row[1])):
                                            preassignments_is_valid = False
                                            ctx_admin['sheets'][field]['messages'].append(f'Invalid e-mail in row {i+1}, received {row[0]}.')
                                            break
                                        # check if locker number is numeric
                                        if not type(row[2]) == int:
                                            preassignments_is_valid = False
                                            ctx_admin['sheets'][field]['messages'].append(f'Invalid locker number value in row {i+1}, received {row[2]}.')
                                            break
                                        blank = False
                                        # check for any blank values
                                        for j in range(len(row)):
                                            if type(row[j]) == float:
                                                preassignments_is_valid = False
                                                ctx_admin['sheets'][field]['messages'].append(f'Blank entry in row {i+1}, column {j+1}.')
                                                blank = True
                                                break
                                        if blank:
                                            break
                            # problem with spreadsheet, but not identified
                            except:
                                students_is_valid = False
                                ctx_admin['sheets'][field]['messages'].append(f'Please follow template carefully. Submission not recognized.')
                            if preassignments_is_valid:
                                try:
                                    ctx_admin['sheets'][field]['messages'] = []
                                    conn.execute(
                                        school.update().where(and_(
                                            school.c.id == session['school_id']
                                            )
                                        ).values(
                                            preassignments_spreadsheet_uploaded = True,
                                            preassignments_spreadsheet_filename = sheet_filename
                                        )
                                    )
                                    for student_email_1, student_email_2, locker_number in sheet_data:
                                        student_id_1 = conn.execute(
                                            student.select().where(student.c.email == student_email_1)
                                            ).first()[0]
                                        student_id_2 = conn.execute(
                                            student.select().where(student.c.email == student_email_2)
                                            ).first()[0]
                                        criteria_preassignment = [
                                            or_(
                                                assignment.c.student_id == student_id_1,
                                                assignment.c.partner_id == student_id_1
                                            ),
                                            or_(
                                                assignment.c.student_id == student_id_2,
                                                assignment.c.partner_id == student_id_2
                                            )
                                        ]
                                        # DO LOCKER GUYS FIRST SO ID CAN BE FOUND :QJJ:
                                        upsert(conn, assignment, criteria_preassignment, {
                                            'student_id': student_id_1,
                                            'partner_id': student_id_2,
                                            'status': 'MATCH',
                                            'locker_id': 0
                                        })
                                except Exception as e:
                                    # print(e)
                                    preassignments_is_valid = False
                                    ctx_admin['sheets'][field]['messages'].append('Please upload students & lockers spreadsheets first. Student(s)/Locker not found.')

                # reload if everything looks right
                if students_is_valid and lockers_is_valid and preassignments_is_valid:
                    # redirect
                    return web.HTTPFound(location=request.app.router['index'].url_for())
                # return messages if there are errors
                else:
                    # message to reload
                    # messages['success'].append('Saved sheets successfully. Reload to view sheets.')
                    # creating response
                    response = aiohttp_jinja2.render_template(
                        'admin.html',
                        request,
                        ctx_admin
                    )
                    return response

async def login(request):
    # creating message dictionary
    messages = {
        'success': [],
        'danger': [],
        'info': []
    }

    # loading post request data
    data = await request.post()

    # test: from form fields on home page (TEST)
    email = data['email']

    # final: OAuth2 flow when it's figured out
    # token = data['idtoken']
    # idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
    # print('USER INFO:', idinfo)
    #
    # # id_info attributes required to authorize a user
    # email = idinfo.get('email')

    # authorizing the user email exists in database (given by admin sheet)
    # querying email and recording response
    student_db_request = conn.execute(student.select().
        where(student.c.email == email)).first()
    admin_db_request = conn.execute(admin.select().
        where(admin.c.email == email)).first()

    # user is a student
    if student_db_request != None:
        role = 'student'
        kv = zip(student.columns.keys(), student_db_request)
    # user is an admin
    elif admin_db_request != None:
        role = 'admin'
        kv = zip(admin.columns.keys(), admin_db_request)
    # user is not found
    else:
        # return to / page, correct view will be rendered based on user's role and login status
        return web.HTTPFound(location=request.app.router['index'].url_for())

    # new session
    # print('Creating Session...')
    session = await new_session(request)

    # user info
    session['authorized'] = True
    session['role'] = role

    # loading db info into session
    for key, value in kv:
        session[key] = value

    # print('Session Created:', session)

    # return to / page, correct view will be rendered based on user's role and login status
    return web.HTTPFound(location=request.app.router['index'].url_for())

async def logout(request):
    # creating message dictionary
    messages = {
        'success': [],
        'danger': [],
        'info': []
    }

    # getting user session
    session = await get_session(request)

    # log out successful
    if session.get('authorized'):
        messages['success'].append('Logged out successfully.')

    # invalidating session
    session.invalidate()

    # return to / page, correct view will be rendered based
    return web.HTTPFound(location=request.app.router['index'].url_for())
    # # creating context
    # ctx_logout = {
    #     'session': session,
    #     'messages': messages
    # }
    # # creating response
    # response = aiohttp_jinja2.render_template(
    #     'index.html',
    #     request,
    #     ctx_logout
    # )
    # # rendering for user
    # return response
