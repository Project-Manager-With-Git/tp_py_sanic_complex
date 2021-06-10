from sanic import Blueprint
from .example_tables import example_tables

tablenamespace = Blueprint("tables", url_prefix="/table", version="1_0_0")

tablenamespace.get("/<date:ymd>")(example_tables)