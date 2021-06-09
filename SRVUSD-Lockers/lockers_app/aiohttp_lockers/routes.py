from views import index, student

def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/student', student)
