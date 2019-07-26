from api.routes.foo import init_foo_routes


def init_routes(app):
    init_foo_routes(app)
