from aiohttp import web
import aiohttp_jinja2
import db

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
