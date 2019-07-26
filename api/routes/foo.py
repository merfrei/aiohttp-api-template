from api.handlers.foo import get_handler
from api.handlers.foo import post_handler
from api.handlers.foo import put_handler
from api.handlers.foo import delete_handler


def init_foo_routes(app):
    app.router.add_route('GET', '/foo/{id:\d+}', get_handler)
    app.router.add_route('GET', '/foo', get_handler)
    app.router.add_route('POST', '/foo', post_handler)
    app.router.add_route('PUT', '/foo/{id:\d+}', put_handler)
    app.router.add_route('DELETE', '/foo/{id:\d+}', delete_handler)
