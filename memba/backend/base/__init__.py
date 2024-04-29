import memba.backend.plugin.base as memba_plugin
from . import data as memba_data
from . import track as memba_track
from . import misc as memba_misc

import asyncio

async def start():
	await memba_data.start()
	await memba_plugin.start()
	await memba_track.start()
	await memba_plugin.trigger("start")

async def core_loop():
	while True:
		memba_misc.log(
			"CORE",
			msg="loop",
			level=memba_misc.logging.INFO
		)
		await asyncio.sleep(1)

async def loop():
	# await asyncio.gather(memba_track.track(), core_loop())
	await asyncio.gather(memba_track.track())

async def close():
	await memba_plugin.trigger("close")
	await memba_track.close()
	await memba_plugin.close()
	await memba_data.close()