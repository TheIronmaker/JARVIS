import asyncio
from collections import defaultdict
import logging

class AsyncDataBus:
    def __init__(self):
        self._data = {}