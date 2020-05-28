"""
AIOHTTP API - Base Model
"""

from itertools import chain


class DBModel:
    '''DBModel to represent a table in database'''

    tablename = None  # It must not be None

    def __init__(self, app):
        self._app = app
        self.pool = app['pool']

    @staticmethod
    def _insert_values_query_str(columns, *values):
        columns_no = len(columns.split(','))
        first_col_no = 1
        insert_values_list = []
        for _ in values:
            last_col_no = columns_no + first_col_no
            values_query = ', '.join(['${}'.format(c_no) for c_no in
                                      range(first_col_no, last_col_no)])
            insert_values_list.append('({})'.format(values_query))
            first_col_no = last_col_no
        return ', '.join(insert_values_list)

    async def insert(self, columns, *values, return_id=True, on_conflict=None):
        """SQL INSERT Query
        columns: str (ie: name, age)
        *values: tuples (ie: ('Nano', 33))"""
        query = 'INSERT INTO {} ({}) VALUES {}'.format(
            self.tablename, columns, self._insert_values_query_str(columns, *values))
        if on_conflict is not None:
            query += ' ON CONFICT {}'.format(on_conflict)
        if return_id:
            query += ' RETURNING id'
        values_args = list(chain(*values))
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchval(query, *values_args)
                return result

    async def update(self, columns, values, *where):
        """SQL UPDATE Query
        columns: str (ie: name, age)
        values: tuple (ie: ('Emiliano', 33))
        *where: tuples <column, comparator, value> (ie: ('name', '=', 'Nano'))"""
        query_args = list(values)
        query_args += self._where_args(*where)
        update_query_str = ', '.join([
            '{} = ${}'.format(c.strip(), c_no) for c_no, c in
            enumerate(columns.split(','), 1)])
        query = 'UPDATE {} SET {}'.format(self.tablename, update_query_str)
        if where:
            where_query_str = self._where_str(*where, first_arg_no=(len(values) + 1))
            query += ' WHERE {}'.format(where_query_str)
        query += ' RETURNING *'
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(query, *query_args)
                return result

    @staticmethod
    def _where_args(*where):
        query_args = []
        for _1, _2, w_v in where:
            if callable(w_v):
                # Look at the comment in `_where_str` method
                _, qry_args = w_v()
                w_v = qry_args  # This way is more explicit
            if isinstance(w_v, list):
                query_args += w_v
            else:
                query_args.append(w_v)
        return query_args

    @staticmethod
    def _w_v_args(args, arg_no):
        """It'll return the arguments to use in the where query
        ie: [$1, $2, ...]
        Also the current argument position number"""
        w_v_args = []
        for _ in args:
            arg_no += 1
            w_v_args.append('${}'.format(arg_no))
        return w_v_args, arg_no

    def _where_str(self, *where, first_arg_no=1):
        arg_no = first_arg_no - 1
        where_cl = []
        for w_c, w_e, w_v in where:
            if callable(w_v):
                # Used to include subqueries
                # This callback will return a tuple: <qry_str>,<qry_args>
                # All the arguments will be {} so we can use format to insert
                # the correct position number
                qry_str, _ = w_v()
                w_v_args, arg_no = self._w_v_args(w_v, arg_no)
                qry_str = qry_str.format(*w_v_args)
                where_cl.append('{} {} ({})'.format(w_c, w_e, qry_str))
            elif w_e == 'in':
                w_v_args, arg_no = self._w_v_args(w_v, arg_no)
                where_cl.append('{} in ({})'.format(w_c, ','.join(w_v_args)))
            else:
                arg_no += 1
                where_cl.append('{} {} ${}'.format(w_c, w_e, arg_no))
        return ' AND '.join(where_cl)

    def _select_query(self, *where, columns='*', extra=None):
        query = 'SELECT {} FROM {}'.format(columns, self.tablename)
        query_args = []
        if where:
            query_args = self._where_args(*where)
            where_query_str = self._where_str(*where)
            query += ' WHERE {}'.format(where_query_str)
        if extra is not None:
            query += ' {}'.format(extra)
        return query, query_args

    def _select_count_query(self, *where, columns='*', extra=None):
        query = 'SELECT count({}) FROM {}'.format(columns, self.tablename)
        query_args = []
        if where:
            query_args = self._where_args(*where)
            where_query_str = self._where_str(*where)
            query += ' WHERE {}'.format(where_query_str)
        if extra is not None:
            query += ' {}'.format(extra)
        return query, query_args

    async def select(self, *where, columns='*', extra=None):
        """SQL SELECT Query
        *where: tuples <column, comparator, value> (ie: ('age', '>', 15))
        columns: str (ie: name, age)
        extra: str (ie: ORDER BY 1 OFFSET 3 LIMIT 5)"""
        query, query_args = self._select_query(*where, columns=columns, extra=extra)
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetch(query, *query_args)
                return result

    async def count(self, *where, columns='id'):
        '''Return the count for a given query'''
        query, query_args = self._select_count_query(*where, columns=columns)
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(query, *query_args)
                return result

    async def select_one(self, *where, columns='*', extra=None, no_limit=False):
        """SQL SELECT Query (only one row)
        *where: tuples <column, comparator, value> (ie: ('age', '>', 15))
        columns: str (ie: name, age)
        extra: str (ie: ORDER BY 1 OFFSET 3)
        no_limit: do not add LIMIT 1 at the end of the query"""
        query, query_args = self._select_query(*where, columns=columns, extra=extra)
        if not no_limit:
            query += ' LIMIT 1'
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(query, *query_args)
                return result

    async def select_val(self, *where, columns='*', extra=None, no_limit=False):
        """SQL SELECT Query (return a value in the first row)
        *where: tuples <column, comparator, value> (ie: ('age', '>', 15))
        columns: str (ie: name, age)
        extra: str (ie: ORDER BY 1 OFFSET 3 LIMIT 5)
        no_limit: do not add LIMIT 1 at the end of the query"""
        query, query_args = self._select_query(*where, columns=columns, extra=extra)
        if not no_limit:
            query += ' LIMIT 1'
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchval(query, *query_args)
                return result

    async def delete(self, *where):
        """SQL DELETE Query
        *where: tuples <column, comparator, value> (ie: ('name', '=', 'Nano'))"""
        query_args = self._where_args(*where)
        query = 'DELETE FROM {}'.format(self.tablename)
        if where:
            where_query_str = self._where_str(*where)
            query += ' WHERE {}'.format(where_query_str)
        query += ' RETURNING *'
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                result = await connection.fetchrow(query, *query_args)
                return result
