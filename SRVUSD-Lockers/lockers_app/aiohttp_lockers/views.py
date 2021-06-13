from aiohttp import web
import aiohttp_jinja2
import db, asyncio
from google.oauth2 import id_token
from google.auth.transport import requests

CLIENT_ID = '745601090768-kosoi5uc466i9ns0unssv5h6v8ilk0a8.apps.googleusercontent.com'

async def dashboard(request):
    location = request.app.router['admin'].url_for()
    raise web.HTTPFound(location=location)

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
