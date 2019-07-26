from api.handlers.base import get_base_get
from api.handlers.base import get_base_post
from api.handlers.base import get_base_put
from api.handlers.base import get_base_delete
from api.model.foo import FooDB


async def get_handler(request):
    where_query = []
    if 'column' in request.query:
        where_query.append(
            ('column', 'ilike', '%{}%'.format(request.query['column'])))
    result = await get_base_get(FooDB, *where_query,
                                extra='ORDER BY column asc')(request)
    return result


async def post_handler(request):
    result = await get_base_post(FooDB)(request)
    return result


async def put_handler(request):
    result = await get_base_put(FooDB)(request)
    return result


async def delete_handler(request):
    result = await get_base_delete(FooDB)(request)
    return result
