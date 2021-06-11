from sanic import Sanic, Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, text
from sanic_openapi import doc
from .usernamespace import usernamespace

api = Blueprint.group(usernamespace, url_prefix="/api")


def init_api(app: Sanic) -> Sanic:
    app.get("/ping")(ping)
    app.blueprint(api)
    return app


@doc.summary("ping接口用于健康检查")
async def ping(request: Request) -> HTTPResponse:
    return text("pong")
