import asyncio
import os
import sys
from typing import Dict


async def async_should_reload() -> bool:
    mtimes: Dict[str, float] = {}
    while True:
        for module in set(sys.modules.values()):
            filename: str = getattr(module, '__file__', None)
            if not filename:
                continue

            mtime: float = os.path.getmtime(filename)
            if mtime > mtimes.get(filename, mtime):
                return True
            mtimes[filename] = mtime

        await asyncio.sleep(2)
