from aiohttp import web
from viewsv2 import *

def setup_routes(app):
    # index
    app.router.add_get('/', index, name='index')
    # app.router.add_post('/', index, name='index')

    # dashboard student & admin
    app.router.add_get('/dashboard', dashboard, name='dashboard')
    app.router.add_post('/dashboard', dashboard, name='dashboard')

    # authentication
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/logout', logout, name='logout')

    # assignment
    app.router.add_get('/assign', assign, name='assign')

    # assignment
    app.router.add_get('/simulate_preferences', simulate_preferences, name='simulate_preferences')
