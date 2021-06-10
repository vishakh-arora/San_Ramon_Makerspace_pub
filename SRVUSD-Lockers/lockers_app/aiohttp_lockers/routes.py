from aiohttp import web
from views import index, student, admin

def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/student', student, name='student')
    app.router.add_get('/admin', admin, name='admin')
