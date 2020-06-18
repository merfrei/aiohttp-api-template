"""
API authentication
"""

from aiohttp import web


async def get_403_response():
    '''GET 403 Unauthorized response'''
    return web.json_response({'message': 'forbidden',
                              'data': {},
                              'status': 'forbidden'}, status=403)


@web.middleware
async def apikey_middleware(request, handler):
    '''API api-key authentication aiohttp middleware'''
    api_key = request.query.get('api_key', None)
    api_key_method = '{}_api_key'.format(request.method.lower())
    app_api_key = request.app.get(api_key_method, request.app['api_key'])
    if api_key is None or api_key != app_api_key:
        return await get_403_response()
    return await handler(request)
