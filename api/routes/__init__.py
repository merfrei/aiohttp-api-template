"""
API: init routes
"""

from api.routes.foo import init_foo_routes


def init_routes(app):
    '''Init some routes for the App'''
    init_foo_routes(app)
