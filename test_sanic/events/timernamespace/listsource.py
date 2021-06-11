import uuid
import asyncio
from pyloggerhelper import log
from sanic.response import json, HTTPResponse
from sanic.request import Request
from sanic.views import HTTPMethodView
from sanic_openapi import doc
from sserender import SSE
from test_sanic.aredis_proxy import redis
from ...decorators.checkjsonschema import checkjsonschema
from .schema import post_query_schema


class ListSource(HTTPMethodView):

    @doc.summary("监听指定计时器")
    @doc.tag("event")
    @doc.produces(
        doc.String(description="sse消息"),
        description="监听流",
        content_type="text/event-stream;charset=UTF-8")
    async def get(self, request: Request) -> HTTPResponse:
        response = await request.respond(
            content_type="text/event-stream;charset=UTF-8",
            headers={
                "Connection": "keep-alive",
                "Transfer-Encoding": "chunked",
                "Cache-Control": "no-cache"
            }
        )
        p = redis.pubsub()
        await p.subscribe('timer::golbal')
        log.info("subscribe ok")
        while True:
            message = await p.get_message(ignore_subscribe_messages=True, timeout=0.01)
            if message is not None:
                log.info("get msg", msg=message)
                sse = SSE.from_content(message["data"])
                if sse.comment and sse.comment.strip() == "END":
                    # await response.send(message["data"])
                    await response.send("", True)
                    break
                else:
                    await response.send(message["data"])
        return response

    @staticmethod
    @doc.summary("创建一个倒计时")
    @doc.tag("event")
    @doc.consumes(doc.JsonBody({
        "seconds": doc.Integer("倒计时信息.")
    }), location="body")
    @doc.produces({
        "channelid": str
    }, description="频道id", content_type="application/json")
    @checkjsonschema(post_query_schema)
    async def post(request: Request) -> HTTPResponse:
        query_json = request.json
        seconds = query_json.get("seconds")
        channelid = str(uuid.uuid4())

        async def countdown_maker(seconds: int, channelid: str) -> None:
            await redis.sadd("timer::channels", channelid)
            eid = 0
            try:
                for i in range(seconds, 0, -1):
                    msg = SSE(event="countdown", ID=str(eid), data=str(i)).render()
                    async with await redis.pipeline() as pipe:
                        await pipe.publish(f'timer::{channelid}', msg)
                        await pipe.publish('timer::golbal', msg)
                        await pipe.execute()
                    # log.info("send msg ok", msg=msg)
                    eid += 1
                    await asyncio.sleep(1)
            finally:
                msg = SSE(event="countdown", ID=str(seconds), data="0").render()
                async with await redis.pipeline() as pipe:
                    await pipe.publish(f'timer::{channelid}', msg)
                    await pipe.publish('timer::golbal', msg)
                    await pipe.execute()
                endmsg = SSE(comment="END").render()
                await redis.publish(f'timer::{channelid}', endmsg)
                await redis.srem("timer::channels", channelid)
                log.info("send close ok", msg=endmsg)
                await asyncio.sleep(1)

        request.app.add_task(countdown_maker(seconds, channelid))
        return json({"channelid": channelid})
