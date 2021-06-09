from sanic import Sanic, Blueprint
from .usernamespace import usernamespace

api = Blueprint.group(usernamespace, url_prefix="/api")


def init_api(app: Sanic) -> Sanic:
    app.blueprint(api)
    return app