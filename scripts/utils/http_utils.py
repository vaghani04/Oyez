import aiohttp

class HttpUtils:
    async def fetch_json(self, session, url):
        try:
            async with session.get(url) as response:
                return await response.json()
        except Exception as e:
            print(f"Failed to fetch JSON from {url}: {e}")
            return None

    async def fetch_binary(self, session, url):
        try:
            async with session.get(url) as response:
                return await response.read()
        except Exception as e:
            print(f"Failed to fetch binary from {url}: {e}")
            return None