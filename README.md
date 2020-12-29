# Asyncio Pipe

This package allows you to read from a `multiprocessing.Connection` object
without blocking an `asyncio` event loop using `AsyncConnection` wrapper.

The `Connection` class has the same API functions as `multiprocessing.Connection`.

## Usage

```python
import asyncio
import multiprocessing
import asyncio_pipe


def worker(connection):
    name = connection.recv()
    connection.send(f'Hello {name}')

async def coro(connection):
    await connection.send('World')
    print(await connection.recv())


async_connection, sync_connection = asyncio_pipe.AsyncPipe(duplex=True)
process = multiprocessing.Process(target=worker, args=(sync_connection,))
process.start()
asyncio.get_event_loop().run_until_complete(coro(async_connection))
```
