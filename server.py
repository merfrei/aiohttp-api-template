import asyncio
import argparse
from aiohttp import web
from api import init_app


parser = argparse.ArgumentParser(description="Codescrap API: aiohttp server")
parser.add_argument('--path')
parser.add_argument('--port')


def run_server():
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())

    args = parser.parse_args()

    web.run_app(app, path=args.path, port=args.port)


if __name__ == '__main__':
    run_server()
