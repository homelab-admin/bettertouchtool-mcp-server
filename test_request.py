#!/usr/bin/env python3
import asyncio
import sys

sys.path.insert(0, 'src')

from btt_mcp.client import btt_request
from btt_mcp.models import BTTConnectionConfig


async def test():
    config = BTTConnectionConfig()
    result = await btt_request('get_clipboard_content', {'format': 'public.utf8-plain-text'}, config)
    print(f'Raw result repr: {repr(result)}')
    print(f'Raw result len: {len(result) if result else 0}')
    print(f'Bool of result: {bool(result)}')

asyncio.run(test())
