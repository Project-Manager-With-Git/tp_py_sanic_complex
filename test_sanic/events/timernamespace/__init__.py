from sanic import Blueprint
from .listsource import ListSource
from .source import Source

timernamespace = Blueprint("timer", url_prefix="/timer", version="1_0_0")
timernamespace.add_route(ListSource.as_view(), "/")
timernamespace.add_route(Source.as_view(), "/<channelid:string>", strict_slashes=True)
