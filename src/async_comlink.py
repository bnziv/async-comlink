import aiohttp
import asyncio
from urllib.parse import urlparse

class Comlink:
    """
    Async wrapper for Comlink API
    """
    def __init__(self, 
                 url: str = "http://localhost:3000",
                 host: str | None = None,
                 port: int = 3000):
        """
        Initialize

        Args:
            url (str): The URL of the Comlink API. Defaults to "http://localhost:3000"
            host (str, optional): The host of the Comlink API
            port (int, optional): The port of the Comlink API. Defaults to 3000
        """

        if host:
            # Set the URL based on the host and port
            protocol = "https" if port == 443 else "http"
            port = port or (443 if protocol == "https" else 80)
            self.url = f"{protocol}://{host}:{port}"
        else:
            # Set the URL based on the provided URL
            parsed_url = urlparse(url.rstrip("/"))
            if not parsed_url.scheme:
                raise ValueError("URL must include a scheme (http or https)")
            
            self.url = url.rstrip("/")
            if not parsed_url.port:
                default_port = 443 if parsed_url.scheme == "https" else 80
                self.url = f"{parsed_url.scheme}://{parsed_url.hostname}:{default_port}"

        self.session = aiohttp.ClientSession(base_url=self.url)

    async def _post(self,
                    endpoint: str,
                    payload: dict = None) -> dict:
        """
        Send a POST request to the Comlink URL

        Args:
            endpoint (str): The endpoint to send the request to
            payload (dict, optional): The payload to send. Defaults to None.

        Raises:
            e: Exception from aiohttp

        Returns:
            dict: The response
        """
        try:
            async with self.session.post(endpoint, json=payload) as response:
                response = await response.json()
            return response
        except Exception as e:
            raise e

    async def get_events(self, enums=False):
        """
        Get current and scheduled events in the game

        Args:
            enums (bool, optional): If the response should use enums instead of integers. Defaults to False.

        Returns: dict
        """
        endpoint = "/getEvents"
        payload = {
            "enums": enums
        }
        response = await self._post(endpoint=endpoint, payload=payload)
        return response
    
    async def get_enums(self):
        """
        Get the enums for the API responses

        Returns: dict
        """
        endpoint = "/enums"
        async with self.session.get(endpoint) as response:
            response = await response.json()
        return response

    async def close(self):
        """
        Close the session
        """
        if self.session:
            await self.session.close()
            self.session = None

    def __del__(self):
        """
        Close the session when the object is deleted
        """
        if self.session and not self.session.closed:
            if asyncio.get_event_loop().is_running():
                asyncio.create_task(self.close())
            else:
                asyncio.run(self.close())