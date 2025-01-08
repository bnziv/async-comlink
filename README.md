# Async Comlink

Async Comlink is an asynchronous Python wrapper for the [swgoh-comlink](https://github.com/swgoh-utils/swgoh-comlink) service. It provides a convenient way for making API requests and includes built-in support for HMAC authentication, enabling secure communication with the service.

## Features

- Fully asynchronous, non-blocking API requests via `aiohttp`
- Compact JSON serialization for compatibility with the API
- Parameter validation to prevent invalid requests
- Debug mode to log requests and help with troubleshooting
- Support for HMAC authentication to ensure secure communication

## Installation
Async Comlink is available on [PyPi](https://pypi.org/project/async-comlink/):
```bash
pip install async-comlink
```
Dependencies: aiohttp

## Usage
Basic example of using Async Comlink to make an API request:
```python
import asyncio
from async_comlink import AsyncComlink

async def main():
    # Basic use (for long-lived usage)
    comlink = AsyncComlink()
    response = await comlink.get_player(allycode=123456789)

    # Context manager use (for short-lived usage)
    async with AsyncComlink() as comlink:
        response = await comlink.get_player(allycode=123456789)

asyncio.run(main())
```
For more information regarding endpoints and their parameters, refer to the [swgoh-comlink documentation](https://github.com/swgoh-utils/swgoh-comlink/wiki/Getting-Started#endpoints).

## Initialization Parameters
| Parameter | Description | Default |
| --- | --- | --- |
| `url` | The base URL of the swgoh-comlink service. | `http://localhost:3000` |
| `host` | The host of the swgoh-comlink service. | `None` |
| `port` | The port of the swgoh-comlink service. | `3000` |
| `access_key` | The access key to use for HMAC authentication. | `None` |
| `secret_key` | The secret key to use for HMAC authentication. | `None` |
| `debug` | If debug mode should be enabled to log requests and suppress raised exceptions on errors. | `False` |

## License
Async Comlink is released under the [MIT License](https://opensource.org/licenses/MIT).