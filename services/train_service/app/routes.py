from view import index, modeltraining


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_post('/modeltraining', modeltraining)
