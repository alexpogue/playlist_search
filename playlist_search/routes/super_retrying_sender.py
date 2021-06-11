import time
import asyncio

from tekore import Sender, RetryingSender, Request, Response
from typing import Coroutine, Union
from httpx import ConnectError

class SuperRetryingSender(RetryingSender):
    def __init__(self, retries: int = 0, sender: Sender = None):
        super().__init__(retries, sender)

    def send(self, request: Request) -> Union[Response, Coroutine[None, None, Response]]:
        if self.is_async:
            return self._async_send(request)

        tries = self.retries + 1
        delay_seconds = 1

        while tries > 0:
            try:
                r = self.sender.send(request)
                if r.status_code == 429:
                    seconds = r.headers.get('Retry-After', 1)
                    time.sleep(int(seconds) + 1)
                elif r.status_code >= 400 and tries > 1:
                    tries -= 1
                    time.sleep(delay_seconds)
                    delay_seconds *= 2
                else:
                    return r
            except ConnectError:
                tries -= 1
                time.sleep(delay_seconds)
                delay_seconds *= 2

    async def _async_send(self, request: Request) -> Response:
        tries = self.retries + 1
        delay_seconds = 1

        while tries > 0:
            try:
                r = await self.sender.send(request)

                if r.status_code == 429:
                    seconds = r.headers.get('Retry-After', 1)
                    await asyncio.sleep(int(seconds) + 1)
                elif r.status_code >= 400 and tries > 1:
                    tries -= 1
                    await asyncio.sleep(delay_seconds)
                    delay_seconds *= 2
                else:
                    return r
            except ConnectError:
                tries -= 1
                await asyncio.sleep(delay_seconds)
                delay_seconds *= 2

