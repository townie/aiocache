import pytest
import asyncio

from aiocache import SimpleMemoryCache
from aiocache.serializers import DefaultSerializer

KEY = "key"


@pytest.fixture
def memory_cache():
    cache = SimpleMemoryCache(namespace="test")
    yield cache
    cache._cache.pop("test:" + KEY, None)


class TestSimpleMemoryCache:

    def test_setup(self, memory_cache):
        assert memory_cache.namespace == "test"
        assert isinstance(memory_cache.serializer, DefaultSerializer)

    @pytest.mark.asyncio
    async def test_get_missing(self, memory_cache):
        assert await memory_cache.get(KEY) is None
        assert await memory_cache.get(KEY, default=1) == 1

    @pytest.mark.asyncio
    async def test_get_existing(self, memory_cache):
        await memory_cache.set(KEY, "value")
        assert await memory_cache.get(KEY) == "value"

    @pytest.mark.asyncio
    async def test_set_with_ttl(self, memory_cache, mocker):
        loop = asyncio.get_event_loop()
        mocker.spy(loop, 'call_later')
        await memory_cache.set(KEY, "value", ttl=2)
        loop.call_later.assert_called_with(2, memory_cache._delete, KEY)

        await asyncio.sleep(2)
        assert await memory_cache.get(KEY) is None

    @pytest.mark.asyncio
    async def test_delete(self, memory_cache):
        assert await memory_cache.delete(KEY) is None
        await memory_cache.set(KEY, "value")
        assert await memory_cache.delete(KEY) is "value"

    @pytest.mark.asyncio
    async def test_incr(self, memory_cache):
        assert await memory_cache.incr(KEY) == 1
        assert await memory_cache.incr(KEY, 1) == 2
        assert await memory_cache.incr(KEY, 5) == 7