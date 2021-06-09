from aiohttp import web
from settings import config
from routes import setup_routes, student
import aiohttp_jinja2
import jinja2
from db import close_pg, init_pg

app = web.Application()
app['config'] = config
aiohttp_jinja2.setup(app,
    loader=jinja2.FileSystemLoader('aiohttp_lockers/templates'))
setup_routes(app)
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)
web.run_app(app)
