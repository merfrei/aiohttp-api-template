"""
API Base Handler creators
"""

import json
import datetime

from pydantic import ValidationError

from aiohttp import web


def parse_datetime(content):
    '''Parse a datetime parameter
    I recommend to set the str format in a config file'''
    if isinstance(content, datetime.datetime):
        return content.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(content, datetime.date):
        return content.strftime('%Y-%m-%d')
    return content


def custom_dumps(content):
    '''Custom dumps function for parsing datetime parameters'''
    return json.dumps(content, default=parse_datetime)


def get_404_response():
    '''Default 404 response'''
    return web.json_response({'message': 'Not found',
                              'data': {},
                              'status': 'unknown'}, status=404)

def get_422_response(details):
    '''Default validation error response'''
    return web.json_response({'message': 'Validation Errors',
                              'data': {'details': details},
                              'status': 'error'}, status=422)


def validate_params(params, schema):
    '''Given a pydantic model it will validate the body params'''
    try:
        schema_inst = schema(**params)
    except ValidationError as errors:
        return errors, params
    ret_params = {sch_k: sch_v for sch_k, sch_v in schema_inst.dict().items()
                  if sch_v is not None}
    return None, ret_params


def convert_dict_list_to_str(content):
    '''If the content is a dict or list it will be converted to a JSON string'''
    if isinstance(content, (list, dict)):
        return json.dumps(content)
    return content


def get_base_get(db_model_cls, *where, extra=None):
    '''Get a base GET handler'''
    async def get_handler(request):
        model_id = request.match_info.get('id')
        model_db = db_model_cls(request.app)
        total = 1
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


def get_base_post(db_model_cls, schema=None):
    '''Get a base POST handler'''
    async def post_handler(request):
        model_db = db_model_cls(request.app)
        params = await request.json()
        if not params:
            return get_404_response()
        if schema is not None:
            errors, params = validate_params(params, schema)
            if errors is not None:
                return get_422_response(errors.json())
        columns = []
        values = []
        for col, val in params.items():
            columns.append(col)
            values.append(convert_dict_list_to_str(val))
        result = await model_db.insert(','.join(columns), *[tuple(values)])
        return web.json_response({'message': 'All OK',
                                  'data': {'id': result},
                                  'status': 'success'}, status=201,
                                 dumps=custom_dumps)
    return post_handler


def get_base_put(db_model_cls, schema=None):
    '''Get a base PUT handler'''
    async def put_handler(request):
        model_id = request.match_info.get('id')
        if model_id is not None:
            model_db = db_model_cls(request.app)
            params = await request.json()
            if not params:
                return get_404_response()
            if schema is not None:
                errors, params = validate_params(params, schema)
                if errors is not None:
                    return get_422_response(errors.json())
            columns = []
            values = []
            for col, val in params.items():
                columns.append(col)
                values.append(convert_dict_list_to_str(val))
            where_query = [('id', '=', int(model_id)), ]
            result = await model_db.update(','.join(columns),
                                           tuple(values),
                                           *where_query)
            return web.json_response({'message': 'All OK',
                                      'data': dict(result),
                                      'status': 'success'}, status=200,
                                     dumps=custom_dumps)
    return put_handler


def get_base_delete(db_model_cls):
    '''Get a base DELETE handler'''
    async def delete_handler(request):
        model_id = request.match_info.get('id')
        if model_id is not None:
            model_db = db_model_cls(request.app)
            where_query = [('id', '=', int(model_id)), ]
            result = await model_db.delete(*where_query)
            return web.json_response({'message': 'All OK',
                                      'data': dict(result),
                                      'status': 'success'}, status=200,
                                     dumps=custom_dumps)
        return get_404_response()
    return delete_handler
