from sanic import Blueprint
from .listsource import ListSource
from .source import Source

usernamespace = Blueprint("user", url_prefix="/user", version="1_0_0")
usernamespace.add_route(ListSource.as_view(), "/")
usernamespace.add_route(Source.as_view(), "/<uid:int>")