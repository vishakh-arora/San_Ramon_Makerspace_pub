from aiohttp import web
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from init_db import *
import aiohttp_jinja2
import db
import asyncio
from google.oauth2 import id_token
from google.auth.transport import requests
from multidict import MultiDict
import pandas as pd

CLIENT_ID = '745601090768-kosoi5uc466i9ns0unssv5h6v8ilk0a8.apps.googleusercontent.com'

conn = initialize_db()

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
    return {}

@aiohttp_jinja2.template('admin.html')
async def admin(request):
    return {}

@asyncio.coroutine
def tokensignin(request):
    data = yield from request.post()
    token = data['idtoken']
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        print(idinfo)

        # If auth request is from a G Suite domain:
        domain = idinfo.get('hd')
        #print(idinfo['hd'])
        if domain != None:
        #****Change validation to db lookup****
            if 'srvusd' not in domain:
                raise ValueError('Wrong hosted domain.')
        else:
            raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        location = request.app.router['admin'].url_for()
        raise web.HTTPFound(location=location)
    except ValueError:
        # Invalid token
        pass

def store_sheets(request):
    sheets = {'students':[],
              'lockers':[],
              'preassign':[]}
    data = yield from request.post()

    print(data)

    for sheet_id in sheets:
        try:
            sheet = data[sheet_id]
            # filename contains the name of the file in string format.
            sheets[sheet_id].append(sheet.filename)

            # input_file contains the actual file data which needs to be
            # stored somewhere.
            sheets[sheet_id].append(sheet.file)
            df = pd.read_excel(sheet.file, engine="openpyxl")
            #*** add sheet validation here ***
            # print()
            # print(df.head())
            sheets[sheet_id].append(df)
        except Exception as e:
            print(e)

    # print(sheets)
    return web.Response(body=sheets['students'][2],
                        headers=MultiDict({'CONTENT-DISPOSITION': 'inline'}))
