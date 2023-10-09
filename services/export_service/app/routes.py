from view import index, export


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_post('/export', export)
