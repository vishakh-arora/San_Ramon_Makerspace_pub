import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from aiohttp import web, web_request
from urllib.parse import urlencode
import aiohttp_jinja2
from aiohttp_session import get_session, new_session
from assignment import Lockers, Match
from copy import deepcopy
from cryptography.fernet import Fernet
from init_db import *
from db import *
from google.oauth2 import id_token
from google.auth.transport import requests
from multidict import MultiDict
from sqlalchemy import and_, or_
from datetime import datetime, timezone, timedelta
import pandas as pd
import numpy as np
import random
import itertools
import re
import math
# import pytz

# temp_storage = {'partner':[None for i in range(3)]}
CLIENT_ID = '745601090768-kosoi5uc466i9ns0unssv5h6v8ilk0a8.apps.googleusercontent.com'

conn = initialize_db()

# (TEST)
# clear existing entries
# conn.execute(school.delete())
# conn.execute(student.delete())
# conn.execute(admin.delete())
# conn.execute(preference.delete())
# conn.execute(organization.delete())
# conn.execute(org_name.delete())
# conn.execute(assignment.delete())

# create hardcoded entries (TEST)
# creating school
# conn.execute(school.insert({
#     'id': 0,
#     'name': 'Dougherty Valley High School',
#     # 'org_id': 0,
#     'students_spreadsheet_uploaded': False,
#     'lockers_spreadsheet_uploaded': False,
#     'preassignments_spreadsheet_uploaded': False
# }))
# conn.execute(school.insert({
#     'id': 1,
#     'name': 'California High School',
#     # 'org_id': 1,
#     'students_spreadsheet_uploaded': False,
#     'lockers_spreadsheet_uploaded': False,
#     'preassignments_spreadsheet_uploaded': False
# }))

# creating organizations w names
# conn.execute(org_name.insert({
#     'school_id': 0,
#     'hierarchy_1': 'building',
#     'hierarchy_2': 'floor',
#     'hierarchy_3': 'row'
# }))
# conn.execute(org_name.insert({
#     'school_id': 1,
#     'hierarchy_1': 'floor',
#     'hierarchy_2': 'bay',
#     'hierarchy_3': 'level'
# }))

# creating student users
# conn.execute(student.insert({
#     'id': 0,
#     'email': 'dh.skumar@students.srvusd.net',
#     'first_name': 'shubham',
#     'last_name': 'kumar',
#     'school_id': 0,
#     'grade': 9
# }))
# conn.execute(student.insert({
#      'id': 1,
#      'email': 'dh.varora@students.srvusd.net',
#      'first_name': 'vishakh',
#      'last_name': 'arora',
#      'school_id': 0,
#      'grade': 12
#  }))
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
#     'email': 'ch.skumar@students.srvusd.net',
#     'first_name': 'shubham',
#     'last_name': 'kumar',
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
# conn.execute(admin.insert({
#     'id': 0,
#     'email':'vishakh.arora29@gmail.com',
#     'prefix': 'Mr.',
#     'last_name': 'Arora',
#     'school_id': 0
# }))
#
# conn.execute(admin.insert({
#     'id': 1,
#     'email':'kumar.shubham5504@gmail.com',
#     'prefix': 'Mr.',
#     'last_name': 'Kumar',
#     'school_id': 1
# }))

# creating organizations
options = {
     0: {
         'building': ['1000', '2000', '3000', '4000'],
         'floor': ['top', 'bottom'],
         'row': ['top', 'bottom']
     },
     1: {
         'floor': ['1', '2', '3'],
         'bay': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n'],
         'level': ['top', 'middle', 'bottom']
     }
 }
#
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

wayward_buddies = set()
og_db_request = conn.execute(preference.select()).fetchall()
og_mfs = set()
# print(set([i[1] for i in og_db_request]))
for i in og_db_request:
    st_db_req = conn.execute(student.select().where(student.c.id == i[1])).first()
    # check if student is from DV, is not a freshman and has submitted before separation date
    # print(i[0], datetime(2021, 8, 4, 10, 0, 0, 0, timezone.utc), datetime(2021, 8, 4, 7, 0, 0, 0, timezone.utc) > i[0])
    if st_db_req[4] == 0 and st_db_req[5] != 9 and i[0] < datetime(2021, 8, 4, 16, 30, 0, 0, timezone.utc):
        og_mfs.add(i[1])
    # else:
        # print(i[1])

# print(og_mfs)

PRINT = True
def print_debug(arg='\n'):
    if PRINT:
        print(arg)

def preview_db():
    # preview tables
    school_request = conn.execute(school.select())
    student_request = conn.execute(student.select())
    admin_request = conn.execute(admin.select())
    preference_request = conn.execute(preference.select())
    organization_request = conn.execute(organization.select())
    org_name_request = conn.execute(org_name.select())
    locker_request = conn.execute(locker.select())
    assignment_request = conn.execute(assignment.select())

    # print()
    # print()
    # print('SCHOOL PREVIEW:', *school_request.fetchall(), sep='\n')
    # print('STUDENT PREVIEW:', *student_request.fetchall(), sep='\n')
    # print('ADMIN PREVIEW:', *admin_request.fetchall(), sep='\n')
    # print('PREFERENCE PREVIEW:', *preference_request.fetchall(), sep='\n')
    # print('ORGANIZATION PREVIEW:', *organization_request.fetchall(), sep='\n')
    # print('ORG_NAME PREVIEW:', *org_name_request.fetchall(), sep='\n')
    # print('LOCKER PREVIEW:', *locker_request.fetchall(), sep='\n')
    # print('ASSIGNMENT PREVIEW:', *assignment_request.fetchall(), sep='\n')
    # print()
    # print()

all_sessions = {}

# caches
student_cache = {0:{9:None, 10:None, 11:None, 12:None}, 1:{9:None, 10:None, 11:None, 12:None}}
locker_cache = {}
# STUDENT CJECHJU
# {
#     0: {
#             9: DVHS Freshmen List,
#             10: DVHS Sophomores List,
#             11: DVHS Juniors List,
#             12: DVHS Seniors List,
#     },
#     1: {
#             9: CHS Freshmen List,
#             10: CHS Sophomores List,
#             11: CHS Juniors List,
#             12: CHS Seniors List,
#     }
# }
# LOCKER CJECHJU
# {
#     0: {
#             'building': [1000, 2000, 3000, 4000],
#             'floor': ['top', 'bottom'],
#             'row': ['top', 'bottom']
#     },
#     1: {
#             'floor': ['top', 'bottom'],
#             'bay': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'],
#             'level': ['top', 'bottom']
#     }
# }

# locker assignment is closed by default, can be opened
open = {0: True, 1:True}

locker_objects = {
    i: Lockers([options[i][j] for j in options[i]])
    for i in options
}

# print(locker_objects[0].d)
# print(locker_objects[1].d)

# print(locker_objects)

def check_login(request):
    # print('ALL SESSIONS')
    # print(all_sessions)
    # getting user session
    sessionid = request.cookies.get('sessionid')
    # print('Cookie Session:', sessionid)
    session = None
    if sessionid == None or sessionid == '':
        # print('\nGETTING PARAMETER\n')
        sessionid = str(request.rel_url.query.get('sessionid')).strip()
        # print(sessionid)
        if sessionid == None:
            sessionid = ''
    if sessionid != None:
        session = all_sessions.get(sessionid)
    # print('Index Session:', session)

    if session == None:
        session = {}

    return session, sessionid

async def index(request):
    # preview_db()

    # creating message dictionary
    messages = {
        'success': [],
        'danger': [],
        'info': []
    }
#        exc = web.HTTPFound(location=request.app.router['index'].url_for())
#        # print('Deleting cookie...')
#        exc.set_cookie('sessionid','')
#        raise exc

    session, sessionid = check_login(request)

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
        response.set_cookie('sessionid', '')
        # rendering for user
        return response

    else:
        return web.HTTPFound(location=request.app.router['dashboard'].url_for())


async def dashboard(request):
    preview_db()

    # creating message dictionary
    messages = {
        'success': [],
        'danger': [],
        'info': []
    }

    session, sessionid = check_login(request)

    if session.get('authorized') == None:
        return web.HTTPFound(location=request.app.router['index'].url_for())

    # user is logged in
    if session.get('authorized'):

        # user is a student
        if session['role'] == 'student':
            # print('\nAUTHORIZED as student\n')
            # preference_request = conn.execute(preference.select())
#            # print()
#            # print('PREFERENCE PREVIEW:', *preference_request.fetchall(), sep='\n')
#            # print()
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

            # cache students if not already
            if student_cache[session['school_id']][session['grade']] != None:
                student_options = student_cache[session['school_id']][session['grade']]
                # print(f'PULLED STUDENT DATA FROM CACHE')
            else:
                # querying database for student options (grade & school must be the same)
                # exclude the logged in student from the list
                student_db_request = conn.execute(
                    student.select().
                        where(
                            and_(
                            # student.c.id != session['id'],
                            student.c.grade == session['grade'],
                            student.c.school_id == session['school_id']
                            )
                        )
                    )

                # create dict to be passed into jinja prepopulated with student ids and info
                # i[0] is id, i[2] is first name, i[3] is last name and i[1] is email
                student_options = {
                    i[0]: f'{i[2].capitalize()} {i[3].capitalize()} ({i[1]})'
                    for i in student_db_request if i[0] not in og_mfs
                }
                student_cache[session['school_id']][session['grade']] = student_options.copy()

            # querying database for existing student preferences
            # sort preferences by partner rank (least to greatest)

            preference_request = conn.execute(preference.select())
            # print('PREFERENCE PREVIEW:', *preference_request.fetchall(), sep='\n')

            preference_db_request = conn.execute(
                preference.select().
                    where(preference.c.student_id == session['id'])
                ).fetchall()

            if len(preference_db_request) != 0:
                messages['success'].append('Preferences saved successfully.')

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
            # hierarchy_db_request = conn.execute(
            # organization.select().
            #     where(organization.c.school_id == session['school_id'])
            # ).fetchall()
            #
            # hierarchy_db_request = [list(filter(None, i[2:])) for i in hierarchy_db_request]

            # print()
            # print(*hierarchy_db_request, sep='\n')
            # print()

            # hierarchy_options = [set() for i in range(len(hierarchies))]

            # for i in hierarchy_db_request: # (1000, top, top)
            #     for j in range(len(i)):
            #         hierarchy_options[j].add(i[j])

            # print()
            # print(*hierarchy_options, sep='\n')
            # print()

            # hierarchy_options = [sorted(list(i)) for i in hierarchy_options]

            # locker_options = {
            #     i: j
            #     for i, j in zip(hierarchies, hierarchy_options)
            # }

            locker_options = deepcopy(options[session['school_id']])

            # Dougherty Valley High School
            # Seniors 1000
            # Juniors 2000
            # Sophomores 3000
            # Freshmen 4000 (with partners)
            # No need to ask for building information
            if session['school_id'] == 0:
                del locker_options['building']

            # California High School
            # Seniors First Floor
            # Juniors First & Second Floor
            # Sophomores Second Floor
            # Freshmen Third Floor
            # Only need to offer floor option to juniors
            if session['school_id'] == 1:
                if session['grade'] == 9:
                    del locker_options['floor']
                if session['grade'] == 10:
                    del locker_options['floor']
                if session['grade'] == 11:
                    locker_options['floor'] = ['1', '2']
                if session['grade'] == 12:
                    del locker_options['floor']
                    locker_options['bay'].remove('n')

            # print()
            # print(options)
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
                'open': (open[session['school_id']] and session['id'] not in og_mfs),
                'chosen': not (session['id'] in wayward_buddies),
                'student_partnerships': True,
                'student_options': student_options,
                'partner_preferences': partner_preferences, # temp_storage['partner'], (TEST)
                'locker_preferences': locker_preferences, # ex: {'building':1000, 'floor':1, 'row':1}
                'locker_options': locker_options, # ex: {'building':[1000, 2000, 3000, 4000], 'floor':[1, 2], 'row':[1, 2]}
                'session': session,
                'messages': messages,
                'issues': [None, None, None]
            }

            if session['school_id'] == 1 or session['id'] in og_mfs:
                ctx_students['student_partnerships'] = False

            # print(ctx_students)
            # get request
            if request.method == 'GET':
                # creating response
                response = aiohttp_jinja2.render_template(
                    'student.html',
                    request,
                    ctx_students
                )
                response.set_cookie('sessionid', sessionid)
                # rendering for user
                # print(request.method)
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
                if ctx_students['student_partnerships']:
                    user_form_response = [
                        data['preference1'],
                        data['preference2'],
                        data['preference3']
                    ]
                    data_proc = list(filter(lambda x: x!='none', user_form_response))

                    # print('USER RESPONSE', data_proc)

                    if len(set(data_proc)) != len(data_proc):
                        messages['success'] = []
                        messages['danger'].append('Please choose different people for each preference.')
                        # prefilling fields
                        # ctx_students['locker_preferences'] = {
                        #     i: data[i]
                        #     for i in hierarchies
                        # }
                        ctx_students['locker_preferences'] = {}
                        for i in hierarchies:
                            try:
                                ctx_students['locker_preferences'][i] = data[i]
                            except:
                                pass
                        # print(user_form_response)
                        # ctx_students['partner_preferences'] = [int(i) for i in user_form_response]
                        ctx_students['partner_preferences'] = []
                        for i in user_form_response:
                            if i != 'none':
                                ctx_students['partner_preferences'].append(int(i))
                            else:
                                ctx_students['partner_preferences'].append(i)
                        # print(ctx_students['partner_preferences'])
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
                        response.set_cookie('sessionid', sessionid)
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

                # Dougherty Valley High School
                # Seniors 1000
                # Juniors 2000
                # Sophomores 3000
                # Freshmen 4000 (with partners)
                # No need to ask for building information
                if session['school_id'] == 0:
                    # Populating building
                    if session['grade'] == 9:
                        criteria_hierarchy_query[0][1] = '4000'
                    if session['grade'] == 10:
                        criteria_hierarchy_query[0][1] = '3000'
                    if session['grade'] == 11:
                        criteria_hierarchy_query[0][1] = '2000'
                    if session['grade'] == 12:
                        criteria_hierarchy_query[0][1] = '1000'
                    # Populating other fields
                    for i in range(len(hierarchies)-1):
                        criteria_hierarchy_query[i+1][1] = data[hierarchies[i+1]]

                # California High School
                # Seniors First Floor
                # Juniors First & Second Floor
                # Sophomores Second Floor
                # Freshmen Third Floor
                # Only need to offer floor option to juniors
                if session['school_id'] == 1:
                    if session['grade'] == 9:
                        criteria_hierarchy_query[0][1] = '3'
                    if session['grade'] == 10:
                        criteria_hierarchy_query[0][1] = '2'
                    if session['grade'] == 11:
                        criteria_hierarchy_query[0][1] = data['floor']
                    if session['grade'] == 12:
                        criteria_hierarchy_query[0][1] = '1'
                    # Populating other fields
                    for i in range(len(hierarchies)-1):
                        criteria_hierarchy_query[i+1][1] = data[hierarchies[i+1]]

                criteria_hierarchy_query = [i[0] == i[1] for i in criteria_hierarchy_query]

                locker_db_request = conn.execute(
                    organization.select().
                        where(
                            and_(*criteria_hierarchy_query)
                        )
                    ).first()

                locker_preference_id = locker_db_request[0]

                if ctx_students['student_partnerships']:
                    # TEMPORARY
                    # NEED TO FIGURE OUT UPSERTS
                    # FIGURED IT OUT OREN
                    if data['preference1'] != 'none':
                        if session['id'] in wayward_buddies:
                            wayward_buddies.remove(session['id'])
                        criteria_preference1_upsert = [
                            preference.c.student_id == session['id'],
                            or_(
                                preference.c.partner_id == data['preference1'],
                                preference.c.partner_rank == 0
                            )
                        ]
                        upsert(conn, preference, criteria_preference1_upsert, {
                            'submit_time': datetime.now(timezone.utc),
                            'student_id': session['id'],
                            'partner_id': data['preference1'],
                            'partner_rank': 0,
                            'locker_pref': locker_preference_id,
                        })
                    else:
                        wayward_buddies.add(session['id'])
                        criteria_preference1_upsert_n = [
                            preference.c.student_id == session['id'],
                            preference.c.partner_rank == 0
                        ]
                        dup = list(student_options.keys())
                        # print(partner_preferences)
                        for i in partner_preferences:
                            if i in dup:
                                dup.remove(i)
                        if data['preference2'] != 'none':
                            dup.remove(data['preference2'])
                        if data['preference3'] != 'none':
                            dup.remove(data['preference3'])
                        upsert(conn, preference, criteria_preference1_upsert_n, {
                            'submit_time': datetime.now(timezone.utc),
                            'student_id': session['id'],
                            'partner_id': random.choice(dup),
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
                else:
                    upsert(conn, preference, [preference.c.student_id == session['id']], {
                        'submit_time': datetime.now(timezone.utc),
                        'student_id': session['id'],
                        'partner_id': session['id'],
                        'partner_rank': 0,
                        'locker_pref': locker_preference_id,
                    })


                # # message to reload
                # messages['success'].append('Saved successfully. Reload to view preferences.')
                # # creating response
                # response = aiohttp_jinja2.render_template(
                #     'student.html',
                #     request,
                #     ctx_students
                # )
                # return response
                return web.HTTPFound(location=request.app.router['dashboard'].url_for())


        # user is an administrator
        if session['role'] == 'admin':
            # creating context
            # populate these with values from database if they exist
            fields = ['students', 'lockers', 'preassignments']

            ctx_admin = {
                'open': open[session['school_id']],
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
                response.set_cookie('sessionid', sessionid)
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
                                #     # print(i)
                                # print('\n\n')

                                for last_name, first_name, grade, email in sheet_data:
                                    criteria = [student.c.email == email]
                                    upsert(conn, student, criteria, {
                                        'email': str(email.strip().lower()),
                                        'first_name': str(first_name.strip().lower()),
                                        'last_name': str(last_name.strip().lower()),
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
                                        if type(row[1]) != str or len(row[1].split(',')) != 3 or len(row[1]) != 8:
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
                                    organization_values = i[2:]
                                    for j in range(num_hierarchies):
                                        # if type(locker[j]) == str:
                                            # locker[j].lower()
                                        locker_options[j].add(str(organization_values[j]).strip().lower())
                                    # print([str(i).strip().lower() for i in organization_values])
                                    locker_objects[session['school_id']].add_locker([str(i).strip().lower() for i in organization_values], [str(i[0])])

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
                                    hierarchy_name_upsert[i][1] = sheet_columns[i+2].strip().lower()

                                organization_name_values = {
                                    i[0]: i[1]
                                    for i in hierarchy_name_upsert
                                }
                                upsert(conn, org_name, [org_name.c.school_id == session['school_id']], organization_name_values)

                                hierarchy_query = [
                                    [organization.c.hierarchy_1, None],
                                    [organization.c.hierarchy_2, None],
                                    [organization.c.hierarchy_3, None],
                                    [organization.c.hierarchy_4, None],
                                    [organization.c.hierarchy_5, None],
                                    [organization.c.school_id, session['school_id']]
                                ]
                                # preview_db()
                                # add in the lockers
                                # GODDA DO THIS ONE STILL G
                                for i in sheet_data:
                                    locker_number = i[0]
                                    locker_combination = i[1]
                                    organization_values = i[2:]
                                    for i in range(len(organization_values)):
                                        hierarchy_query[i][1] = str(organization_values[i]).strip().lower()
                                    org_id = conn.execute(organization.select().where(and_(*[i[0] == i[1] for i in hierarchy_query]))).first()[0]
                                    locker_criteria = [
                                        [locker.c.number, 'number', str(locker_number)],
                                        [locker.c.school_id, 'school_id', session['school_id']],
                                        [locker.c.combination, 'combination', str(locker_combination)],
                                        [locker.c.organization, 'organization', org_id]
                                    ]
                                    upsert(conn, locker, [i[0]==i[2] for i in locker_criteria], {i[1]:i[2] for i in locker_criteria})

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
                    return web.HTTPFound(location=request.app.router['dashboard'].url_for())
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
                    response.set_cookie('sessionid', sessionid)
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
    # print()
    # print(request.remote)
    # print(request.headers)
    # print()
    # test: from form fields on home page (TEST)
    if data.get('idtoken') == None:
        email = data['email']
    else:
        # final: OAuth2 flow when it's figured out
        token = data['idtoken']
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        # print('USER INFO:', idinfo)

        # id_info attributes required to authorize a user
        email = idinfo.get('email')

    # print('EMAIL: ', email)

    # authorizing the user email exists in database (given by admin sheet)
    # querying email and recording response
    student_db_request = conn.execute(student.select().
        where(student.c.email == email)).first()
    admin_db_request = conn.execute(admin.select().
        where(admin.c.email == email)).first()

    # user is a student
    if student_db_request != None:
        # print('IDENTIFIED AS STUDENT')
        role = 'student'
        kv = zip(student.columns.keys(), student_db_request)
    # user is an admin
    elif admin_db_request != None:
        # print('IDENTIFIED AS ADMIN')
        role = 'admin'
        kv = zip(admin.columns.keys(), admin_db_request)
    # user is not found
    else:
        # return to / page, correct view will be rendered based on user's role and login status
        # print('\nNO ROLE FOUND\n')
        raise web.HTTPUnauthorized()
        # return web.HTTPFound(location=request.app.router['index'].url_for())

    # new session
    #session = await new_session(request)
    sessionid = request.cookies['sessionid']
    # print('Checking Session...' + sessionid)
    if sessionid == '' or sessionid == None:
        sessionid = Fernet.generate_key().decode()
        all_sessions[sessionid] = {}
    session = all_sessions.get(sessionid)

    # user info
    session['authorized'] = True
    session['role'] = role

    # loading db info into session
    for key, value in kv:
        session[key] = value

    # print('Session Created:', session)
    # print(all_sessions[sessionid])

    # return to / page, correct view will be rendered based on user's role and login status
    location = str(request.app.router['dashboard'].url_for())+ '?' + urlencode({'sessionid': sessionid})
    # print(location)
    exc = web.HTTPFound(location=location)

    # print(sessionid)
#    exc.set_cookie('sessionid', sessionid)
    raise exc
#    return web.Response()

async def logout(request):
    # creating message dictionary
    messages = {
        'success': [],
        'danger': [],
        'info': []
    }

    # getting user session
#    session = await get_session(request)
    sessionid = request.cookies['sessionid']
    session = all_sessions.get(sessionid)

    # log out successful
    if session != None and session.get('authorized'):
        messages['success'].append('Logged out successfully.')

    # invalidating session
    try:
        del all_sessions[sessionid]
    except:
        pass

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

# TEST
async def simulate_preferences(request):
    session, sessionid = check_login(request)

    if session.get('authorized') and session['role'] == 'admin':
        if session['school_id'] == 0:
            student_db_request = conn.execute(student.select().where(and_(student.c.school_id == 0))).fetchall()
            for id, email, first_name, last_name, school_id, grade in student_db_request:
                if school_id == 0:
                    # if grade == 9:
                        # criteria = [organization.c.hierarchy_1 == '1000', organization.c.hierarchy_2 == 'a', organization.c.hierarchy_3 == 'top']
                        # continue
                    if grade == 10:
                        criteria = [organization.c.hierarchy_1 == '3000', organization.c.hierarchy_2 == 'bottom', organization.c.hierarchy_3 == 'top']
                    if grade == 11:
                        criteria = [organization.c.hierarchy_1 == '2000', organization.c.hierarchy_2 == 'bottom', organization.c.hierarchy_3 == 'top']
                    if grade == 12:
                        criteria = [organization.c.hierarchy_1 == '1000', organization.c.hierarchy_2 == 'bottom', organization.c.hierarchy_3 == 'top']
                if grade != 9:
                    organization_db_request = conn.execute(organization.select().where(and_(*criteria))).first()
                    locker_preference_id = organization_db_request[0]
                    upsert(conn, preference, [preference.c.student_id == id], {
                        'submit_time': datetime.now(timezone.utc),
                        'student_id': id,
                        'partner_id': id,
                        'partner_rank': 0,
                        'locker_pref': locker_preference_id,
                    })

        if session['school_id'] == 1:
            student_db_request = conn.execute(student.select().where(and_(student.c.school_id == 1))).fetchall()
            for id, email, first_name, last_name, school_id, grade in student_db_request:
                if school_id == 1:
                    if grade == 9:
                        criteria = [organization.c.hierarchy_1 == '3', organization.c.hierarchy_2 == 'a', organization.c.hierarchy_3 == 'top']
                    if grade == 10:
                        criteria = [organization.c.hierarchy_1 == '2', organization.c.hierarchy_2 == 'a', organization.c.hierarchy_3 == 'top']
                    if grade == 11:
                        criteria = [organization.c.hierarchy_1 == '2', organization.c.hierarchy_2 == 'a', organization.c.hierarchy_3 == 'top']
                    if grade == 12:
                        criteria = [organization.c.hierarchy_1 == '1', organization.c.hierarchy_2 == 'a', organization.c.hierarchy_3 == 'top']
                organization_db_request = conn.execute(organization.select().where(and_(*criteria))).first()
                locker_preference_id = organization_db_request[0]
                upsert(conn, preference, [preference.c.student_id == id], {
                    'submit_time': datetime.now(timezone.utc),
                    'student_id': id,
                    'partner_id': id,
                    'partner_rank': 0,
                    'locker_pref': locker_preference_id,
                })
        return web.HTTPFound(location=request.app.router['dashboard'].url_for())

    else:
        return web.HTTPFound(location=request.app.router['index'].url_for())

async def assign(request):
    session, sessionid = check_login(request)

    # user is logged in
    if session.get('authorized') and session['role'] == 'admin':
        # print('ASSIGNMENT CALLED')

        student_db_request = conn.execute(student.select()).fetchall()
        # print(len(student_db_request))

        partner_preference_dict = {}
        locker_preference_dict = []
        added_students = set()

        for i in student_db_request:
            preference_db_request = conn.execute(preference.select().where(preference.c.student_id == i[0])).fetchall()

            # ya no ill do it rn :keki:
            # address DVHS freshmen later, they need to be partnered first
            # if i[4] == 0 and i[5] == 9:
            #     print(preference_db_request)
            #     print('freshi man guy')
            #     continue

            # assign lockers for DV students who did not fill out the form
            # cal high people who don't sign up don't get lockers
            if i[4] == 0 and (preference_db_request == None or len(preference_db_request) == 0):
                # preference_db_request.append()
                # print('person didnt select')
                if i[5] == 9:
                    # criteria = [organization.c.hierarchy_1 == '3000', organization.c.hierarchy_2 == 'top', organization.c.hierarchy_3 == 'bottom']
                    # preference_id = conn.execute(organization.select().where(and_(*criteria))).first()[0]
                    partner_preference_dict[i[0]] = ['', '', '']
                    continue
                if i[5] == 10:
                    criteria = [organization.c.hierarchy_1 == '3000', organization.c.hierarchy_2 == 'top', organization.c.hierarchy_3 == 'bottom']
                if i[5] == 11:
                    criteria = [organization.c.hierarchy_1 == '2000', organization.c.hierarchy_2 == 'top', organization.c.hierarchy_3 == 'bottom']
                if i[5] == 12:
                    criteria = [organization.c.hierarchy_1 == '1000', organization.c.hierarchy_2 == 'top', organization.c.hierarchy_3 == 'bottom']
                preference_id = conn.execute(organization.select().where(and_(*criteria))).first()[0]
                locker_preference_dict.append([i[0], i[4], datetime.now(timezone.utc), i[5], preference_id])
                continue

            # print('lens', preference_db_request, len(preference_db_request))

            for submit_time, student_id, partner_id, partner_rank, locker_pref in preference_db_request:

                if student_id != partner_id:
                    try:
                        partner_preference_dict[student_id][partner_rank] = partner_id
                    except:
                        partner_preference_dict[student_id] = ['', '', '']
                        partner_preference_dict[student_id][partner_rank] = partner_id
                    continue
                # if student_id != partner_id:
                    # print('SLIGHT PRAULEM STUDENT IS NOT EQUAL TO PARTNER FOR AN INDIVIDUAL LOCKER :WRONGTENSE')
                    # continue

                student_db_request = conn.execute(student.select().where(student.c.id == student_id)).first()
                grade = student_db_request[5]
                school_id = student_db_request[4]

                if student_id not in added_students:
                    locker_preference_dict.append([student_id, school_id, submit_time, grade, locker_pref])
                    added_students.add(student_id)
                # else:
                    # print('bruh how lmfao')

        dv_freshmen_partnerships = Match([
            [k, v[0], v[1], v[2]]
            for k, v in partner_preference_dict.items()
        ]).get_partners()

        # print(dv_freshmen_partnerships)

        # sort by grade then submit time
        locker_preference_dict = sorted(locker_preference_dict, key=lambda x: (-(11-x[3])**2, x[2]))
        # print(*locker_preference_dict, sep='\n')

        # dictionary {school_id: {id: [attributes]}}

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

        chs_locker_alternatives_12 = list(itertools.product(
            ['1'],
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm'],
            ['top', 'middle', 'bottom']
        ))

        chs_locker_alternatives_11 = list(itertools.product(
            ['1', '2'],
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n'],
            ['top', 'middle', 'bottom']
        ))

        chs_locker_alternatives_11.remove(('1', 'n', 'top'))
        chs_locker_alternatives_11.remove(('1', 'n', 'middle'))
        chs_locker_alternatives_11.remove(('1', 'n', 'bottom'))

        chs_locker_alternatives_10 = list(itertools.product(
            ['2'],
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n'],
            ['top', 'middle', 'bottom']
        ))

        chs_locker_alternatives_9 = list(itertools.product(
            ['3'],
            ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n'],
            ['top', 'middle', 'bottom']
        ))

        alternatives = {
            0: {
                9: dv_locker_alternatives_9,
                10: dv_locker_alternatives_10,
                11: dv_locker_alternatives_11,
                12: dv_locker_alternatives_12
            },
            1: {
                9: chs_locker_alternatives_9,
                10: chs_locker_alternatives_10,
                11: chs_locker_alternatives_11,
                12: chs_locker_alternatives_12
            },
        }

        # out_ctr = 0
        # assigned_ctr = 0
        for student_id, school_id, submit_time, grade, locker_preference_id in locker_preference_dict:

            # db requests
            # student_db_request = conn.execute(student.select().where(student.c.id == student_id)).first()
            organization_db_request = conn.execute(organization.select().where(organization.c.id == locker_preference_id)).first()

            # find grade and school
            # grade = student_db_request[5]
            # school_id = student_db_request[4]

            # freshmen at DV will be assigned after partnerships are finalized
            if school_id == 0 and grade == 9:
                # print('auschwetz')
                continue

            out_of_lockers = False

            # list of alternatives for the specific grade & school
            alt = alternatives[school_id][grade]
            current = tuple(filter(None, organization_db_request[2:]))
            current_idx = alt.index(current)
            track = current_idx

            # look for available locker closest to preference
            new_lock = locker_objects[school_id].get_locker(current)
            # print(locker_objects[school_id].d)
            # print(current)
            while new_lock == None:
                current_idx = (current_idx + 1) % len(alt)
                current = alt[current_idx]
                new_lock = locker_objects[school_id].get_locker(current)
                if current_idx == track:
                    out_of_lockers = True
                    break

            # if no lockers are available from the possible options
            if out_of_lockers:
                print(f'OUT OF LOCKERS FOR GRADE {grade} AT SCHOOL {school_id}.')
                # out_ctr += 1
                continue
            else:
                # print(student_id, new_lock, current)
                # assigned_ctr += 1
                locker_db_request = conn.execute(locker.select().where(and_(locker.c.school_id == school_id, locker.c.number == str(new_lock)))).first()
                upsert(conn, assignment, [assignment.c.student_id == student_id], {
                    'student_id': student_id,
                    'partner_id': student_id,
                    'status': 'MATCH',
                    'locker_id': locker_db_request[0]
                })

        # print(f'\n\n\n\nSTATS:')
        # print(out_ctr, assigned_ctr)
        # print(locker_objects[session['school_id']].d)
        # print('\n\n\n\n')

        for a, b in dv_freshmen_partnerships:
            preference_id_a = conn.execute(preference.select().where(and_(preference.c.student_id == a))).first()
            preference_id_b = conn.execute(preference.select().where(and_(preference.c.student_id == b))).first()

            locker_preference_id = None

            if preference_id_a == None and preference_id_b == None:
                criteria = [organization.c.hierarchy_1 == '4000', organization.c.hierarchy_2 == 'top', organization.c.hierarchy_3 == 'bottom']
                locker_preference_id = conn.execute(organization.select().where(and_(*criteria))).first()[0]
            elif preference_id_a != None:
                locker_preference_id = preference_id_a[4]
            elif preference_id_b != None:
                locker_preference_id = preference_id_b[4]

            organization_db_request = conn.execute(organization.select().where(organization.c.id == locker_preference_id)).first()

            out_of_lockers = False

            # list of alternatives for the specific grade & school
            alt = alternatives[0][9]
            current = tuple(filter(None, organization_db_request[2:]))
            current_idx = alt.index(current)
            track = current_idx

            # look for available locker closest to preference
            new_lock = locker_objects[0].get_locker(current)

            while new_lock == None:
                current_idx = (current_idx + 1) % len(alt)
                current = alt[current_idx]
                new_lock = locker_objects[0].get_locker(current)
                if current_idx == track:
                    out_of_lockers = True
                    break

            if out_of_lockers:
                print(f'OUT OF LOCKERS FOR GRADE 9 AT SCHOOL 0.')
                continue

            else:
                locker_db_request = conn.execute(locker.select().where(and_(locker.c.school_id == 0, locker.c.number == str(new_lock)))).first()
                upsert(conn, assignment, [assignment.c.student_id == a], {
                    'student_id': a,
                    'partner_id': b,
                    'status': 'MATCH',
                    'locker_id': locker_db_request[0]
                })
                upsert(conn, assignment, [assignment.c.student_id == b], {
                    'student_id': b,
                    'partner_id': a,
                    'status': 'MATCH',
                    'locker_id': locker_db_request[0]
                })


        return web.HTTPFound(location=request.app.router['dashboard'].url_for())

    # user can't access this page
    else:
        return web.HTTPFound(location=request.app.router['index'].url_for())

async def export_preferences_to_spreadsheet(request):
    session, sessionid = check_login(request)

    # user is logged in as admin
    if session.get('authorized') and session['role'] == 'admin':
        preference_db_request = conn.execute(preference.select()).fetchall()
        dv_arr = []
        ch_arr = []

        for submit_time, student_id, partner_id, partner_rank, locker_preference_id in preference_db_request:
            student_db_request = conn.execute(student.select().where(student.c.id == student_id)).first()
            partner_db_request = conn.execute(student.select().where(student.c.id == partner_id)).first()
            organization_db_request = conn.execute(organization.select().where(organization.c.id == locker_preference_id)).first()
            subarr = [
                submit_time,
                partner_rank,
                student_db_request[4], # school
                student_db_request[5], # grade
                student_db_request[3], # last name
                student_db_request[2], # first name
                student_db_request[1], # email
                partner_db_request[3], # last name
                partner_db_request[2], # first name
                partner_db_request[1], # email
                organization_db_request[2],
                organization_db_request[3],
                organization_db_request[4],
            ]
            if student_db_request[4] == 0:
                dv_arr.append(subarr)
            if student_db_request[4] == 1:
                ch_arr.append(subarr)

        np.savetxt('test_sheets/ch_preferences.csv', np.array(ch_arr), delimiter=', ', fmt='%s')
        np.savetxt('test_sheets/dv_preferences.csv', np.array(dv_arr), delimiter=', ', fmt='%s')
        return web.HTTPFound(location=request.app.router['index'].url_for())

    # user not allowed
    else:
        return web.HTTPFound(location=request.app.router['index'].url_for())

async def export_assignments_to_spreadsheet(request):
    session, sessionid = check_login(request)

    # user is logged in as admin
    if session.get('authorized') and session['role'] == 'admin':
        assignment_db_request = conn.execute(assignment.select()).fetchall()
        dv_arr = []
        ch_arr = []

        for student_id, partner_id, status, locker_id in assignment_db_request:
            student_db_request = conn.execute(student.select().where(student.c.id == student_id)).first()
            partner_db_request = conn.execute(student.select().where(student.c.id == partner_id)).first()
            locker_db_request = conn.execute(locker.select().where(locker.c.id == locker_id)).first()
            subarr = [
                student_db_request[4], # school
                student_db_request[5], # grade
                student_db_request[3], # last name
                student_db_request[2], # first name
                student_db_request[1], # email
                partner_db_request[3], # last name
                partner_db_request[2], # first name
                partner_db_request[1], # email
                locker_db_request[1]
            ]
            if student_db_request[4] == 0:
                dv_arr.append(subarr)
            if student_db_request[4] == 1:
                ch_arr.append(subarr)

        np.savetxt('test_sheets/ch_assignments.csv', np.array(ch_arr), delimiter=', ', fmt='%s')
        np.savetxt('test_sheets/dv_assignments.csv', np.array(dv_arr), delimiter=', ', fmt='%s')
        return web.HTTPFound(location=request.app.router['index'].url_for())

    # user not allowed
    else:
        return web.HTTPFound(location=request.app.router['index'].url_for())

async def open_form(request):
    session, sessionid = check_login(request)

    # user is logged in as admin
    if session.get('authorized') and session['role'] == 'admin':
        open[session['school_id']] = True

    return web.HTTPFound(location=request.app.router['index'].url_for())

async def close_form(request):
    session, sessionid = check_login(request)

    # user is logged in as admin
    if session.get('authorized') and session['role'] == 'admin':
        open[session['school_id']] = False

    return web.HTTPFound(location=request.app.router['index'].url_for())
