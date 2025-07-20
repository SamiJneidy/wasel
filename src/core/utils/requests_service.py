import httpx
import asyncio
import backoff
import requests
from src.core.config import settings


class AsyncRequestService:
    
    def __init__(self, timeout=settings.TIMEOUT, max_retries=settings.MAX_RETRIES):
        self.timeout = timeout
        self.max_retries = max_retries

        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout), follow_redirects=True)

    async def close(self):
        await self.client.aclose()

    @backoff.on_exception(
        backoff.expo,
        (httpx.RequestError, httpx.HTTPStatusError),
        max_tries=lambda self: self.max_retries,
        jitter=None,
    )
    async def request(self, method, url, json, headers, auth=None, **kwargs):
        try:
            response: httpx.Response = await self.client.request(method=method, url=url, json=json, headers=headers, **kwargs)
            return response
        except httpx.RequestError as e:
            return None

    async def get(self, url, headers, json, params=None, **kwargs):
        return await self.request("GET", url, json, headers, params=params, **kwargs)

    async def post(self, url, headers, json, params=None, **kwargs):
        return await self.request("POST", url, json, headers, params=params, **kwargs)
    
    async def put(self, url, headers, json, params=None, **kwargs):
        return await self.request("PUT", url, json, headers, params=params, **kwargs)

    async def delete(self, url, headers, json, params=None, **kwargs):
        return await self.request("DELETE", url, json, headers, params=params, **kwargs)
