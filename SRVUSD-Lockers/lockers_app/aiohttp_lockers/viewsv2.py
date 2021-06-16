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

CLIENT_ID = '745601090768-kosoi5uc466i9ns0unssv5h6v8ilk0a8.apps.googleusercontent.com'

conn = initialize_db()

async def index(request):
    messages = []
    # getting user session
    session = await get_session(request)

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
                'test_dict': {'water':'tastes good'},
                'student_list': student_list,
                'organization_fields': organization_fields,
                'partner_preferences':['', '', ''],
                'locker_preferences':['', '', ''], # ex: [building, floor, row]
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
                # message to reload
                messages.append('Reload the page to view updated preferences.')
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
                messages.append('Reload the page to view updated preferences.')
                # creating response
                response = aiohttp_jinja2.render_template(
                    'admin.html',
                    request,
                    ctx_admin
                )
                return response

async def login(request):
    # loading post request data
    data = await request.post()

    # validate the user email exists in database (given by admin sheet)
    # creating new user session
    session = await new_session(request)
    # final: OAuth2 flow when it's figured out

    # test: from form fields on home page
    session['authorized'] = True
    session['name'] = data['name']
    session['role'] = data['role']

    # return to / page, correct view will be rendered based on user's role
    return web.HTTPFound(location=request.app.router['index'].url_for())

async def logout(request):
    # getting user session
    session = await get_session(request)

    # invalidating session
    session.invalidate()

    # return to / page, correct view will be rendered based on user's role
    return web.HTTPFound(location=request.app.router['index'].url_for())
