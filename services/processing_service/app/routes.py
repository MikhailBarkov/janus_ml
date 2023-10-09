from view import index, processing


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_post('/processing', processing)
