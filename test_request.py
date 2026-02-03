#!/usr/bin/env python3
import asyncio
import json
import sys

sys.path.insert(0, 'src')

from btt_mcp.client import btt_request
from btt_mcp.formatters import format_floating_menus_list
from btt_mcp.models import BTTConnectionConfig


async def test():
    config = BTTConnectionConfig()
    result = await btt_request('get_triggers', {'trigger_id': 767}, config)
    print(f'Raw result: {repr(result)}')

    menus = json.loads(result)
    print(f'Parsed menus: {menus}')

    formatted = format_floating_menus_list(menus)
    print('Formatted output:')
    print(formatted)

asyncio.run(test())
