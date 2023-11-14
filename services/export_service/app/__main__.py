import argparse

from aiohttp import web

from routes import setup_routes


parser = argparse.ArgumentParser(description="aiohttp server")
parser.add_argument('--port')

app = web.Application()
setup_routes(app)

args = parser.parse_args()

web.run_app(app, port=args.port)
