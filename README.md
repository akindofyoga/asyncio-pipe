# Asyncio Pipe

This package allows you to read from a `multiprocessing.Connection` object
without blocking an `asyncio` event loop.

The `Connection` class has the same API functions as
`multiprocessing.Connection`.

## Usage

```python
import asyncio
import multiprocessing
import asyncio_pipe

async def reader(read):
    connection = asyncio_pipe.Connection(read)
    print(await connection.recv())

def writer(write):
    write.send('Hello World')

read, write = multiprocessing.Pipe(duplex=False)
writer_process = multiprocessing.Process(target=writer, args=(write,))
writer_process.start()
asyncio.get_event_loop().run_until_complete(reader(read))
```
