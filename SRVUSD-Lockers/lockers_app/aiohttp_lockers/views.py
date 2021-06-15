from aiohttp import web
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from init_db import *
import aiohttp_jinja2
import aiohttp_session
import db
import asyncio
from google.oauth2 import id_token
from google.auth.transport import requests
from multidict import MultiDict
import pandas as pd
import numpy as np

CLIENT_ID = '745601090768-kosoi5uc466i9ns0unssv5h6v8ilk0a8.apps.googleusercontent.com'

conn = initialize_db()

# bruh idek what this does
def require_login(f):
    f.__require_login__ = True
    return f

@aiohttp_jinja2.template('index.html')
async def index(request):
    # async with request.app['db'].acquire() as conn:
    #     cursor = await conn.execute(db.question.select())
    #     records = await cursor.fetchall()
    #     questions = [dict(q) for q in records]
        # return web.Response(text=str(questions))
    return {}

@aiohttp_jinja2.template('student.html')
async def student(request):
    if request.method == 'GET':
        # render with filled preferences from database
        return {}
    data = await request.post()
    # preference1, preference2, preference3, building, floor, row
    # check if the preferences are valid and are in the database
    return {}

@aiohttp_jinja2.template('admin.html')
async def admin(request):
    # initializing render variables
    fields = ['students', 'lockers', 'preassign']
    sheets = {i:{
        'error':None,
        'filename':None,
        'data':None,
        # 'df':None
    }
    for i in fields}

    # if response is GET, pull render variables from database
    if request.method == 'GET':
        # add database data retrieval code here and update
        # if a spreadsheet hasn't been successfully uploaded, add in a default error message.
        return {'sheets': sheets}

    # if response is POST, verify submission
    data = await request.post()
    print('RAW RESPONSE:', data, '\n')
    print('KEYS', data.keys(), '\n')

    for sheet_id in fields:
        # empty submission and not existing in database
        if type(data[sheet_id]) == bytearray:
            # add check to see if the spreadsheet already exists in database
            sheets[sheet_id]['error'] = f'Missing {sheet_id.capitalize()} Spreadsheet.'
            continue
        else:
            try:
                sheet = data[sheet_id]

                # filename contains the name of the file in string format.
                sheets[sheet_id]['filename'] = sheet.filename

                # input_file contains the actual file data which needs to be
                # stored somewhere.
                sheets[sheet_id]['data'] = sheet.file
                df = pd.read_excel(sheet.file, engine="openpyxl").to_numpy()

                # length validation

                # print()
                # print(df.columns)
                # sheets[sheet_id]['df'] = df

            except Exception as e:
                print('EXCEPTIONS:', e)

    print('FINAL DICT', sheets)
    return {'sheets':sheets}

    # print(sheets)
    # return web.Response(body=sheets['students'][2],
    #                     headers=MultiDict({'CONTENT-DISPOSITION': 'inline'}))


# @asyncio.coroutine
async def tokensignin(request):
    data = await request.post()
    token = data['idtoken']
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        print(idinfo)

        # If auth request is from a G Suite domain:
        domain = idinfo.get('hd')
        #print(idinfo['hd'])
        if domain != None:
        # ****Change validation to db lookup****
            if 'srvusd' not in domain:
                raise ValueError('Wrong hosted domain.')
        else:
            raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']

        # if user's email is identified as an admin in database, direct to admin page
        location = request.app.router['admin'].url_for()

        # otherwise, take them to student page
        # location = request.app.router['student'].url_for()

        raise web.HTTPFound(location=location)
    except ValueError:
        # Invalid token
        pass

@aiohttp_jinja2.template('login_test.html')
async def login_test(request):
    if request.method == 'GET':
        session = await aiohttp_session.get_session(request)
        if 'username' in session:
            return {'username':session['username']}
        return {'username':None}
    data = await request.post()
    session = await aiohttp_session.new_session(request)
    session['username'] = data['username']
    return {'username':session['username']}

@aiohttp_jinja2.template('login_test.html')
async def logout_test(request):
    session = await aiohttp_session.get_session(request)
    session['username'] = None;
    return {'username': session['username']}
