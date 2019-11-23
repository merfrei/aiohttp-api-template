import json
import datetime
from aiohttp import web


def parse_datetime(content):
    if isinstance(content, datetime.datetime):
        return content.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(content, datetime.date):
        return content.strftime('%Y-%m-%d')
    return content


def custom_dumps(content):
    return json.dumps(content, default=parse_datetime)


def get_404_response():
    return web.json_response({'message': 'Not found',
                              'data': {},
                              'status': 'unknown'}, status=404)


def get_base_get(DBModel, *where, extra=None):
    async def get_handler(request):
        model_id = request.match_info.get('id')
        model_db = DBModel(request.app)
        total = 1;
        paging_query = []
        if 'offset' in request.query:
            offset = int(request.query['offset'])
            paging_query.append('OFFSET {}'.format(offset))
        if 'limit' in request.query:
            limit = int(request.query['limit'])
            paging_query.append('LIMIT {}'.format(limit))
        where_query = list(where)
        extra_query = []
        if extra is not None:
            extra_query.append(extra)
        extra_query += paging_query
        if model_id is not None:
            model_id = int(model_id)
            where_query += [('id', '=', model_id), ]
            row = await model_db.select_one(*where_query,
                                            extra=' '.join(extra_query))
            result = dict(row) if row is not None else {}
            if not result:
                return get_404_response()
        else:
            rows = await model_db.select(*where_query,
                                         extra=' '.join(extra_query))
            result = [dict(r) for r in rows]
            total_c = await model_db.count(*where_query)
            total = total_c['count']
        return web.json_response({'message': 'All OK',
                                  'data': result,
                                  'total': total,
                                  'status': 'success'}, status=200,
                                 dumps=custom_dumps)
    return get_handler


def get_base_post(DBModel):
    async def post_handler(request):
        model_db = DBModel(request.app)
        params = await request.json()
        if params:
            columns = []
            values = []
            for c, v in params.items():
                columns.append(c)
                values.append(v)
            result = await model_db.insert(','.join(columns), *[tuple(values)])
            return web.json_response({'message': 'All OK',
                                      'data': {'id': result},
                                      'status': 'success'}, status=201,
                                     dumps=custom_dumps)
        return get_404_response()
    return post_handler


def get_base_put(DBModel):
    async def put_handler(request):
        model_id = request.match_info.get('id')
        if model_id is not None:
            model_db = DBModel(request.app)
            params = await request.json()
            if params:
                columns = []
                values = []
                for c, v in params.items():
                    columns.append(c)
                    values.append(v)
                where_query = [('id', '=', int(model_id)), ]
                result = await model_db.update(','.join(columns),
                                               tuple(values),
                                               *where_query)
                return web.json_response({'message': 'All OK',
                                          'data': dict(result),
                                          'status': 'success'}, status=200,
                                         dumps=custom_dumps)
        return get_404_response()
    return put_handler


def get_base_delete(DBModel):
    async def delete_handler(request):
        model_id = request.match_info.get('id')
        if model_id is not None:
            model_db = DBModel(request.app)
            where_query = [('id', '=', int(model_id)), ]
            result = await model_db.delete(*where_query)
            return web.json_response({'message': 'All OK',
                                      'data': dict(result),
                                      'status': 'success'}, status=200,
                                     dumps=custom_dumps)
        return get_404_response()
    return delete_handler
