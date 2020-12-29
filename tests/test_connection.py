#!/usr/bin/env python
# coding: utf8

""" Basic connection and pipe test cases. """

import pytest

from asyncio_pipe import AsyncConnection, AsyncPipe
from multiprocessing import Pipe


async def verify_duplex_connection(async_connection, connection):
    connection.send([1, 2, 3])
    assert await async_connection.recv() == [1, 2, 3]
    await async_connection.send([4, 5, 6])
    assert connection.recv() == [4, 5, 6]
    connection.close()
    async_connection.close()


@pytest.mark.asyncio
async def test_async_connection():
    c1, c2 = Pipe()
    await verify_duplex_connection(AsyncConnection(c1), c2)


@pytest.mark.asyncio
async def test_async_pipe():
    c1, c2 = AsyncPipe()
    await verify_duplex_connection(c1, c2)
