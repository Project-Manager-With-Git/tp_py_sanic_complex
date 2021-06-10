from typing import Union
from sanic.views import HTTPMethodView
from sanic.request import Request
from sanic.response import json, stream, StreamingHTTPResponse, HTTPResponse
from sanic_openapi import doc
from sserender import SSE
from pyloggerhelper import log
from test_sanic.aredis_proxy import redis


class Source(HTTPMethodView):

    @doc.summary("监听指定channelid的计时器")
    @doc.tag("event")
    # @doc.consumes(doc.String(name="channelid", description="channel的唯一id.", required=True), location="uri")
    @doc.produces(doc.String(description="sse消息"), description="监听流", content_type="text/event-stream;charset=UTF-8")
    async def get(self, request: Request, channelid: str) -> Union[StreamingHTTPResponse, HTTPResponse]:
        ok = await redis.sismember("timer::channels", channelid)
        log.info('redis.sismember("timer::channels", channelid) result', result=ok)
        if not ok:
            return json({"msg": "未找到channel"}, status=404, ensure_ascii=False)

        async def sample_streaming_fn(response: StreamingHTTPResponse) -> None:
            p = redis.pubsub()
            await p.subscribe(f"timer::{channelid}")
            log.info("subscribe ok")
            while True:
                message = await p.get_message(ignore_subscribe_messages=True, timeout=0.01)
                if message is not None:
                    sse = SSE.from_content(message["data"])
                    if sse.comment and sse.comment.strip() == "END":
                        await response.write(message["data"])
                        break
                    else:
                        await response.write(message["data"])
            log.info("send done")

        return stream(
            sample_streaming_fn,
            content_type="text/event-stream;charset=UTF-8",
            headers={
                "Connection": "keep-alive",
                "Cache-Control": "no-cache"
            })
