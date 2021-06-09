from aiohttp import web
import aiohttp_jinja2

@aiohttp_jinja2.template('nav_base.html')
async def index(request):
  # return web.Response(text='Hello Aiohttp!')
  return {}
