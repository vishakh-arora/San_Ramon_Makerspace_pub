import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from aiohttp import web
import aiohttp_jinja2
from aiohttp_session import get_session, new_session
from init_db import *
import db
from google.oauth2 import id_token
from google.auth.transport import requests
from multidict import MultiDict
import pandas as pd
import numpy as np
import random

# temp_storage = {'partner':[None for i in range(3)]}
CLIENT_ID = '745601090768-kosoi5uc466i9ns0unssv5h6v8ilk0a8.apps.googleusercontent.com'

conn = initialize_db()

# create hardcoded entries (TEST)
# creating school
# access(
#     conn,
#     'school',
#     'insert',
#     {
#         'id': 0,
#         'name': 'Dougherty Valley High School'
#     }
# )
# # creating student user
# access(
#     conn,
#     'student',
#     'insert',
#     {
#         'id': 0,
#         'email': 'dh.skumar@students.srvusd.net',
#         'first_name': 'shubham',
#         'last_name': 'kumar',
#         'school_id': 0,
#         'grade': 12
#     }
# )
# # creating admin user
# access(
#     conn,
#     'admin',
#     'insert',
#     {
#         'id': 0,
#         'email': 'eliddle@srvusd.net',
#         'prefix': 'Mr.',
#         'last_name': 'liddle',
#         'school_id': 0
#     }
# )

async def index(request):
    # creating message dictionary
    messages = {'success':[], 'danger':[], 'info':[]}

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
        if session.get('role') == 'student':
            # populate these with values from database if they exist
            # EXAMPLES:
            student_list = [
                'oren (dh.oren@students.srvusd.net)',
                'kjev (dh.kjev@students.srvusd.net)',
                'veggu (dh.veggu@students.srvusd.net)',
                'shubhert (dh.shubhert@students.srvusd.net)'
            ]
            organization_fields = {
                'building': ['1000', '2000', '3000', '4000'],
                'floor': ['top', 'bottom'],
                'row': ['top', 'bottom']
            }
            # creating context
            ctx_students = {
                'student_list': student_list,
                'organization_fields': organization_fields,
                'partner_preferences': [None for i in range(3)], # temp_storage['partner'], (TEST)
                'locker_preferences':[None for i in range(3)], # ex: [building, floor, row]
                'locker_options':{}, # ex: ['building':[1000, 2000, 3000, 4000], 'floor':[1, 2], 'row':[1, 2]]
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
                # message to reload
                messages['success'].append('Recorded Preferences Successfully.')
                # creating response
                response = aiohttp_jinja2.render_template(
                    'student.html',
                    request,
                    ctx_students
                )
                return response


        # user is an administrator
        if session.get('role') == 'admin':
            # creating context
            # populate these with values from database if they exist
            fields = ['students', 'lockers', 'preassignments']
            ctx_admin = {
                'fields': fields,
                'sheets':{
                    i:{
                        'filename':None,
                        'data':None,
                        'error':None
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
                message['success'].append('Recorded Sheets Successfully.')
                # creating response
                response = aiohttp_jinja2.render_template(
                    'admin.html',
                    request,
                    ctx_admin
                )
                return response

async def login(request):
    # creating message dictionary
    messages = {'success':[], 'danger':[], 'info':[]}

    # loading post request data
    data = await request.post()

    # test: from form fields on home page
    # email = data['email']

    # final: OAuth2 flow when it's figured out
    token = data['idtoken']
    idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
    print('USER INFO:', idinfo)

    # id_info attributes required to authorize a user
    domain = idinfo.get('hd')
    email = idinfo.get('email')

    # user is not a member of the district
    if domain == None or 'srvusd' not in domain:
        return web.HTTPFound(location=request.app.router['index'].url_for())

    # authorizing the user email exists in database (given by admin sheet)
    # conn.Query('student')
    # conn.Query('admin')
    # If the user is found, create session, set authorized to true, and redirect
    # If not, send back to home page

    # if user already has a session
    session = await get_session(request)
    if session.get('authorized'):
        print('User is already authorized')
        print('Session Exists:', session)
        # return to / page, correct view will be rendered based on user's role
        return web.HTTPFound(location=request.app.router['index'].url_for())

    # if user doesn't have a session
    if session.get('authorized') == None:
        print('User does not have a session')
        print('Creating Session...')
        # transferring info from id_info into session
        session = await new_session(request)
        session['authorized'] = True
        session['first_name'] = idinfo.get('given_name')
        session['last_name'] = idinfo.get('family_name')
        session['email'] = email
        session['role'] = 'student'
        print('Session Created:', session)
        # return to / page, correct view will be rendered based on user's role
        return web.HTTPFound(location=request.app.router['index'].url_for())

async def logout(request):
    # creating message dictionary
    messages = {'success':[], 'danger':[], 'info':[]}

    # getting user session
    session = await get_session(request)

    # log out successful
    if session.get('authorized'):
        messages['success'].append('Logged Out Successfully.')

    # invalidating session
    session.invalidate()

    # return to / page, correct view will be rendered based
    # return web.HTTPFound(location=request.app.router['index'].url_for())
    # creating context
    ctx_logout = {
        'session': session,
        'messages': messages
    }
    # creating response
    response = aiohttp_jinja2.render_template(
        'index.html',
        request,
        ctx_logout
    )
    # rendering for user
    return response
