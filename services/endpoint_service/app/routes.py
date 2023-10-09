from view import (
    index,
    create_endpoint,
    call_endpoint
)


def setup_routes(app):
    app.router.add_post('/', index)
    app.router.add_post('/create_endpoint', create_endpoint)
    app.router.add_post('/call', call_endpoint)
