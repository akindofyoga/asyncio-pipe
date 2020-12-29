#!/usr/bin/env python
# coding: utf8

""" Asynchronous multiprocessing communication. """

import asyncio

from multiprocessing import Pipe
from multiprocessing.connection import Connection
from typing import Any, Optional, Tuple


class AsyncConnection(object):
    """
        Asynchronous wrapper over multiprocessing.Connection class.
        Register reader and write over given connection handle to
        perform asynchronous I/O.

        Parameters:
            sync_connection (multiprocessing.Connection):
                Synchronous process connection to decorate with
                asynchronous methods.
            loop (Optional[asyncio.AbstractEventLoop]):
                Event loop to register connection I/O to, if `None``
                then `asyncio.get_event_loop()` will be used, default
                to `None`.
    """

    def __init__(
            self,
            sync_connection: Connection,
            loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self._loop: asyncio.AbstractEventLoop
        if loop is None:
            self._loop = asyncio.get_event_loop()
        else:
            self._loop = loop
        self._sync_connection: Connection = sync_connection
        self._read_event: asyncio.Event = asyncio.Event()
        self._write_event: asyncio.Event = asyncio.Event()
        self._loop.add_reader(
            self._sync_connection.fileno(),
            self._read_event.set)
        self._loop.add_writer(
            self._sync_connection.fileno(),
            self._write_event.set)

    def __del__(self) -> None:
        self.close()

    def fileno(self):
        return self._sync_connection.fileno()

    def close(self) -> None:
        self._loop.remove_reader(self.fileno())
        self._loop.remove_writer(self.fileno())
        self._sync_connection.close()

    @property
    def closed(self) -> bool:
        """True if the connection is closed"""
        return self._sync_connection.closed

    @property
    def readable(self) -> bool:
        """True if the connection is readable"""
        return self._sync_connection.readable

    @property
    def writable(self) -> bool:
        """True if the connection is writable"""
        return self._sync_connection.writable

    async def send(self, obj: Any) -> None:
        """
            Send a picklable object asynchronously.

            See also:
                multiprocessing.Connection#send
        """
        await self._write_event.wait()
        self._sync_connection.send(obj)
        self._write_event.clear()

    async def send_bytes(
            self,
            buf: bytes,
            offset: int = 0,
            size: Optional[int] = None) -> None:
        """
            Send the bytes data from a bytes-like object.

            See also:
                multiprocessing.Connection#send_bytes
        """
        await self._write_event.wait()
        self._sync_connection.send_bytes(buf, offset, size)
        self._write_event.clear()

    async def poll(self, timeout: float = 0.0) -> bool:
        """
            Whether there is any input available to be read.

            See also:
                multiprocessing.Connection#poll
        """
        try:
            await asyncio.wait_for(self._read_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return False
        return True

    async def recv(self) -> Any:
        """
            Receive a picklable object asynchronously.

            See also:
                multiprocessing.Connection#recv
        """
        await self._read_event.wait()
        obj = self._sync_connection.recv()
        self._read_event.clear()
        return obj

    async def recv_bytes(self, maxlength=None) -> bytes:
        """
            Receive bytes data as a bytes object.

            See also:
                multiprocessing.Connection#recv_bytes
        """
        await self._read_event.wait()
        buf: bytes = self._sync_connection.recv_bytes(maxlength)
        self._read_event.clear()
        return buf

    async def recv_bytes_into(self, buf, offset=0) -> int:
        """
            Receive bytes data into a writeable bytes-like object.
            Return the number of bytes read.

            See also:
                multiprocessing.Connection#recv_bytes_into
        """
        await self._read_event.wait()
        size: int = self._sync_connection.recv_bytes_into(buf, offset)
        self._read_event.clear()
        return size


def AsyncPipe(
        duplex: bool = True,
        loop: Optional[asyncio.AbstractEventLoop] = None) -> Tuple[
            AsyncConnection,
            Connection]:
    """
        Returns pair of connection objects at either end of a pipe.
        The first returned connection in asynchronous and thus can be used
        without blocking an eventloop.

        Parameters:
            duplex (bool):
                see multiprocessing.Pipe
            loop (Optional[asyncio.AbstractEventLoop]):
                Event loop to attach connection to.

        Returns:
            Tuple[AsyncConnection, Connection]:
                Created connection pair.
    """
    c1, c2 = Pipe(duplex=duplex)
    return AsyncConnection(c1, loop=loop), c2
