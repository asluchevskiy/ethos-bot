import aiohttp
import asyncio
import aioredis
from aiohttp import web
from json import dumps
from datetime import date, datetime
from parsers import parse_rigstat_online
from settings import *


loop = asyncio.get_event_loop()
routes = web.RouteTableDef()


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError('Type %s not serializable' % type(obj))


def formatted_dumps(data):
    return dumps(data, indent=4 if DEBUG else None, default=json_serial, sort_keys=True)


@routes.get('/api/{name}/')
async def api_handler(request):
    name = request.match_info.get('name')
    cached_html = await app.redis.get('cache:%s' % name)
    if cached_html and not request.query.get('force'):
        return web.json_response(parse_rigstat_online(cached_html), dumps=formatted_dumps)
    async with app.session.get(RIGSTAT_ONLINE_URL % name) as response:
        html = await response.text()
        await app.redis.setex('cache:%s' % name, CACHE_PERIOD, html)
        return web.json_response(parse_rigstat_online(html), dumps=formatted_dumps)


async def prepare_app():

    async def close_session(app):
        await app.session.close()

    async def close_redis(app):
        app.redis.close()

    api = web.Application()
    api.redis = await aioredis.create_redis((REDIS_HOST, REDIS_PORT), db=REDIS_DB)
    api.session = aiohttp.ClientSession(loop=loop)
    api.add_routes(routes)
    api.on_shutdown.append(close_session)
    api.on_shutdown.append(close_redis)
    return api


app = loop.run_until_complete(prepare_app())
web.run_app(app)
