import asyncio


class Connection:
    def __init__(self, connection):
        self._connection = connection
        self._event = asyncio.Event()
        loop = asyncio.get_event_loop()
        loop.add_reader(self._connection.fileno(), self._event.set)

    def send(self, obj):
        """Send a (picklable) object"""

        self._connection.send(obj)

    async def _wait_for_input(self):
        """Wait until there is an input available to be read"""

        while not self._connection.poll():
            await self._event.wait()
            self._event.clear()

    async def recv(self):
        """Receive a (picklable) object"""

        await self._wait_for_input()
        return self._connection.recv()

    def fileno(self):
        """File descriptor or handle of the connection"""
        return self._connection.fileno()

    def close(self):
        """Close the connection"""
        self._connection.close()

    async def poll(self, timeout=0.0):
        """Whether there is an input available to be read"""

        if self._connection.poll():
            return True

        try:
            await asyncio.wait_for(self._wait_for_input(), timeout=timeout)
        except asyncio.TimeoutError:
            return False
        return self._connection.poll()

    def send_bytes(self, buf, offset=0, size=None):
        """Send the bytes data from a bytes-like object"""

        self._connection.send_bytes(buf, offset, size)

    async def recv_bytes(self, maxlength=None):
        """
        Receive bytes data as a bytes object.
        """

        await self._wait_for_input()
        return self._connection.recv_bytes(maxlength)

    async def recv_bytes_into(self, buf, offset=0):
        """
        Receive bytes data into a writeable bytes-like object.
        Return the number of bytes read.
        """

        await self._wait_for_input()
        return self._connection.recv_bytes_into(buf, offset)
