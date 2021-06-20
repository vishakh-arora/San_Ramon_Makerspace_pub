import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import get_session, new_session
from init_db import *
from db import *
from google.oauth2 import id_token
from google.auth.transport import requests
from multidict import MultiDict
from sqlalchemy import and_
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import random
import itertools

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
conn.execute(org_name.insert({
    'id': 0,
    'hierarchy_1': 'building',
    'hierarchy_2': 'floor',
    'hierarchy_3': 'level'
}))
conn.execute(org_name.insert({
    'id': 1,
    'hierarchy_1': 'floor',
    'hierarchy_2': 'bay',
    'hierarchy_3': 'level'
}))
# creating school
conn.execute(school.insert({
    'id': 0,
    'name': 'Dougherty Valley High School',
    'org_id': 0
}))
conn.execute(school.insert({
    'id': 1,
    'name': 'California High School',
    'org_id': 1
}))

# creating student users
conn.execute(student.insert({
    'id': 0,
    'email': 'dh.skumar@students.srvusd.net',
    'first_name': 'shubham',
    'last_name': 'kumar',
    'school_id': 0,
    'grade': 12
}))
conn.execute(student.insert({
    'id': 1,
    'email': 'dh.varora@students.srvusd.net',
    'first_name': 'vishakh',
    'last_name': 'arora',
    'school_id': 0,
    'grade': 12
}))
conn.execute(student.insert({
    'id': 2,
    'email': 'dh.cnookala@students.srvusd.net',
    'first_name': 'chaitanya',
    'last_name': 'nookala',
    'school_id': 0,
    'grade': 12
}))
conn.execute(student.insert({
    'id': 3,
    'email': 'ch.somefool@students.srvusd.net',
    'first_name': 'some',
    'last_name': 'fool',
    'school_id': 1,
    'grade': 12
}))
# creating admin user
conn.execute(admin.insert({
    'id': 0,
    'email':'eliddle@srvusd.net',
    'prefix': 'Mr.',
    'last_name': 'liddle',
    'school_id': 0
}))
# creating organizations
options = {
    0: {
        'building': ['1000', '2000', '3000', '4000'],
        'floor': ['top', 'bottom'],
        'level': ['top', 'bottom']
    },
    1: {
        'floor': ['top', 'bottom'],
        'bay': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M'],
        'level': ['top', 'bottom']
    }
}

x = 0
for i in options: #(0, 1)
    prod = list(itertools.product(*[j for j in list(options[i].values())]))
    for a, b, c in prod:
        conn.execute(organization.insert({
            'id': x,
            'school_id': i,
            'hierarchy_1': a,
            'hierarchy_2': b,
            'hierarchy_3': c
        }))
        x += 1

# preview tables
school_request = conn.execute(school.select())
student_request = conn.execute(student.select())
admin_request = conn.execute(admin.select())
preference_request = conn.execute(preference.select())
organization_request = conn.execute(organization.select())
org_name_request = conn.execute(org_name.select())

print('SCHOOL PREVIEW:', *school_request.fetchall(), sep='\n')
print('STUDENT PREVIEW:', *student_request.fetchall(), sep='\n')
print('ADMIN PREVIEW:', *admin_request.fetchall(), sep='\n')
print('PREFERENCE PREVIEW:', *preference_request.fetchall(), sep='\n')
print('ORGANIZATION PREVIEW:', *organization_request.fetchall(), sep='\n')
print('ORG_NAME PREVIEW:', *org_name_request.fetchall(), sep='\n')

async def index(request):
    # creating message dictionary
    messages = {
        'success': [],
        'danger': [],
        'info': []
    }

    # getting user session
    session = await get_session(request)
    print('Index Session:', session)

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

            # preference_request = conn.execute(preference.select())
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
                partner_preferences[i[3]] = f'{s[2].capitalize()} {s[3].capitalize()} ({s[1]})'


            # querying database for locker options
            # finding org_id for school
            school_db_request = conn.execute(
            school.select().
                where(school.c.id == session['school_id'])
            ).first(),

            org_id = school_db_request[0][2]
            # org_id = 0

            # finding hierarchy names for user's school
            hierarchies = list(filter(None, conn.execute(
            org_name.select().
                where(org_name.c.id == org_id)
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
                'messages': messages
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

                # TEMPORARY
                # NEED TO FIGURE OUT A WAY TO DEAL WITH VARIABLE HIERARCHIES
                locker_db_request = conn.execute(
                    organization.select().
                        where(
                            and_(
                                organization.c.hierarchy_1 == data['building'],
                                organization.c.hierarchy_2 == data['floor'],
                                organization.c.hierarchy_3 == data['level']
                            )
                        )
                    ).first()

                locker_preference_id = locker_db_request[0]

                # TEMPORARY
                # NEED TO FIGURE OUT UPSERTS

                conn.execute(preference.insert({
                    'submit_time': datetime.now(timezone.utc),
                    'student_id': session['id'],
                    'partner_id': data['preference1'],
                    'partner_rank': 0,
                    'locker_pref': locker_preference_id,
                }))

                # preference_request = conn.execute(preference.select())

                if data['preference2'] != 'none':
                    conn.execute(preference.insert({
                        'submit_time': datetime.now(timezone.utc),
                        'student_id': session['id'],
                        'partner_id': data['preference2'],
                        'partner_rank': 1,
                        'locker_pref': locker_preference_id,
                    }))

                if data['preference3'] != 'none':
                    conn.execute(preference.insert({
                        'submit_time': datetime.now(timezone.utc),
                        'student_id': session['id'],
                        'partner_id': data['preference3'],
                        'partner_rank': 2,
                        'locker_pref': locker_preference_id,
                    }))

                # message to reload
                messages['success'].append('Saved successfully. Reload to view preferences.')
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
                        'filename': None,
                        'data': None,
                        'error': None
                    }
                    for i in fields
                },
                'session': session,
                'messages': messages
            }

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
                # save data into database
                # message to reload
                messages['success'].append('Saved sheets successfully. Reload to view sheets.')
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
    print('Creating Session...')
    session = await new_session(request)

    # user info
    session['authorized'] = True
    session['role'] = role

    # loading db info into session
    for key, value in kv:
        session[key] = value

    print('Session Created:', session)

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
