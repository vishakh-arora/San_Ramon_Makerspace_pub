from aiohttp import web
from viewsv2 import *

def setup_routes(app):
    # index
    app.router.add_get('/', index, name='index')
    app.router.add_post('/', index, name='index')

    # authentication
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/logout', logout, name='logout')