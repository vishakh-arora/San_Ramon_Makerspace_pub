from aiohttp import web
from views import *

def setup_routes(app):
    # index
    app.router.add_get('/', index, name='index')

    # student page
    app.router.add_get('/student', student, name='student')
    app.router.add_post('/student', student, name='student')

    # admin page
    app.router.add_get('/admin', admin, name='admin')
    app.router.add_post('/admin', admin, name='admin')

    # authentication
    app.router.add_get('/login', login, name='login')
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/logout', logout, name='logout')

    # login tests
    # app.router.add_get('/login_test', login_test, name='login_test')
    # app.router.add_post('/login_test', login_test, name='login_test')
    # app.router.add_get('/logout_test', logout_test, name='logout_test')

    # app.router.add_post('/store_sheets', store_sheets, name='store_sheets')
