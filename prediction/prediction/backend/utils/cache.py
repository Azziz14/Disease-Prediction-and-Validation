"""
Async LRU cache for fast translation and detection (in-memory).
Replace with aiocache/Redis for production if needed.
"""
import functools
from asyncio import Lock
from collections import OrderedDict

try:
    from cachetools import LRUCache
except ImportError:
    class LRUCache(OrderedDict):
        def __init__(self, maxsize=128):
            super().__init__()
            self.maxsize = maxsize

        def __getitem__(self, key):
            value = super().__getitem__(key)
            self.move_to_end(key)
            return value

        def __setitem__(self, key, value):
            if key in self:
                self.move_to_end(key)
            super().__setitem__(key, value)
            if len(self) > self.maxsize:
                self.popitem(last=False)

_cache = LRUCache(maxsize=128)
_lock = Lock()

def lru_cache_async(maxsize=128):
    def decorator(func):
        cache = LRUCache(maxsize=maxsize)
        lock = Lock()
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            async with lock:
                if key in cache:
                    return cache[key]
            result = await func(*args, **kwargs)
            async with lock:
                cache[key] = result
            return result
        return wrapper
    return decorator
