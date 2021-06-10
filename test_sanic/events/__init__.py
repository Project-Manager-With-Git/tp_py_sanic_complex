from sanic import Sanic, Blueprint
from .timernamespace import timernamespace

events = Blueprint.group(timernamespace, url_prefix="/event")

def init_events(app: Sanic) -> Sanic:
    app.blueprint(events)
    return app
