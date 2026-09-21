import asyncio

import httpx


async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://httpbin.org/get", timeout=30)
        status_code = resp.status_code
        data = resp.json()

    if status_code != 200:
        print(f"错误！状态码: {status_code}")
    else:
        print(f"状态码: {status_code} URL: {data['url']}")

asyncio.run(main())