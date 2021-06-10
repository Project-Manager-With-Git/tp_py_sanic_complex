import asyncio
import aiohttp
from aiohttp_sse_client import client as sse_client


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:5000/v1_0_0/event/timer', json={'seconds': 10}) as resp:
            resj = await resp.json()
            channel_id = resj.get("channelid")
    async with sse_client.EventSource(f'http://localhost:5000/v1_0_0/event/timer/{channel_id}') as event_source:
        try:
            async for event in event_source:
                print(event)
        except ConnectionError:
            pass


asyncio.run(main())
