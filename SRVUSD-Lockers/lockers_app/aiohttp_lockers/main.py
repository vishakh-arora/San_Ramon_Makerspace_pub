from aiohttp import web
from settings import config
from routesv2 import setup_routes
import aiohttp_jinja2
import aiohttp_session
import base64
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography.fernet import Fernet
import jinja2
from db import close_pg, init_pg

app = web.Application()
app['config'] = config

# template and static routes
aiohttp_jinja2.setup(app,
    loader=jinja2.FileSystemLoader('templates/'))
app.add_routes([web.static('/static', 'static/')])

# app routes
setup_routes(app)

# client session instantiation
# key = Fernet.generate_key()
fernet_key = Fernet.generate_key()
secret_key = base64.urlsafe_b64decode(fernet_key)
#key = b'1d4URWUAYoJzQlNLynRQcYwel1zAOJDUTGyVbbsdyxU='
#aiohttp_session.setup(app, EncryptedCookieStorage(key.decode()))
aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))

# database stuff
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)

# start
web.run_app(app)
