from sanic import Sanic, Blueprint
from .tablenamespace import tablenamespace

download = Blueprint.group(tablenamespace, url_prefix="/download")


def init_downloads(app: Sanic) -> Sanic:
    app.blueprint(download)
    return app
