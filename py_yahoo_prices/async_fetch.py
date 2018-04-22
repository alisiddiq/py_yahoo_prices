import asyncio
from aiohttp import ClientSession

async def fetch_url(url, session, headers, params):
    async with session.get(url, headers=headers, params=params) as response:
        return await response.read()

async def run(urls_list, params, header):
    tasks = []
    async with ClientSession() as session:
        for u in urls_list:
            task = asyncio.ensure_future(fetch_url(u, session, headers=header, params=params))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return responses
