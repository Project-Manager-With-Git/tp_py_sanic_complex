from asyncio import AbstractEventLoopPolicy
from sanic import Sanic
from pyloggerhelper import log
import tortoise
from tortoise.contrib.sanic import register_tortoise
from .usermodel import User


def init_models(app: Sanic, *, db_url: str = "sqlite://:memory:", generate_schemas: bool = True, log_level="DEBUG") -> Sanic:
    tortoise.logger.setLevel(log_level)
    register_tortoise(
        app, db_url=db_url, modules={"models": ["test_sanic.models"]}, generate_schemas=generate_schemas
    )

    @app.listener("after_server_start")
    async def _(app: Sanic, loop: AbstractEventLoopPolicy) -> None:
        await User.init_Table()

    log.info("add user init_table to app")
    return app
