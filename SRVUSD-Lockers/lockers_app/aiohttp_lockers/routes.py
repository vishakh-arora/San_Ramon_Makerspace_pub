from aiohttp import web
from views import *

def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/student', student, name='student')
    app.router.add_get('/admin', admin, name='admin')
    app.router.add_get('/dashboard', dashboard, name='dashboard')
    app.router.add_post('/tokensignin', tokensignin, name='tokensignin')
