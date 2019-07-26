from aiohttp import web


async def get_403_response():
    return web.json_response({'message': 'forbidden',
                              'data': {},
                              'status': 'forbidden'}, status=403)


@web.middleware
async def apikey_middleware(request, handler):
    api_key = request.query.get('api_key', None)
    if api_key is None or api_key != request.app['api_key']:
        return await get_403_response()
    return await handler(request)
