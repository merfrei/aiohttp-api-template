"""
AIOHTTP Auth

API Key authentication method
"""

from aiohttp import web


async def get_403_response():
    '''A Unauthorized 403 reponse'''
    return web.json_response({'message': 'forbidden',
                              'data': {},
                              'status': 'forbidden'}, status=403)


@web.middleware
async def apikey_middleware(request, handler):
    '''AIOHTTP Middleware to use an API Key as authentication method'''
    api_key = request.query.get('api_key', None)
    if api_key is None or api_key != request.app['api_key']:
        return await get_403_response()
    return await handler(request)
