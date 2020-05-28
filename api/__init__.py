"""
AIOHTTP API

Init App
"""

import asyncpg
from aiohttp import web
from api.config import get_config
from api.routes import init_routes
from api.auth import apikey_middleware


async def init_app():
    '''Set the config and database pool and init the routes'''
    config = get_config()

    if config['TESTING']:
        app = web.Application()
    else:
        # Auth enabled
        app = web.Application(middlewares=[apikey_middleware])
        app['api_key'] = config['API_KEY']

    # Create a database connection pool
    app['pool'] = await asyncpg.create_pool(config['DATABASE_URI'])

    init_routes(app)

    return app
