import memba.backend.plugin.base as memba_plugin
from . import data as memba_data
from . import track as memba_track
from . import misc as memba_misc

import asyncio

async def start():
	await memba_data.start()
	await memba_plugin.start()

	# [TODO] Keep track of which plugins is still exist
		# To not trigger leftover jobs
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
	await asyncio.gather(memba_track.TRACK_TASK, core_loop())

async def close():
	await memba_track.close()
	await memba_plugin.close()
	await memba_data.close()

# Spawn asyncio task to run memba_track

# Print all column of memba_account table using sqlite syntax
# print(await memba_data.DATA_DB.fetch_all("PRAGMA table_info(memba_account)"))

# List all tables name
# print(list(record["name"] for record in await memba_data.DATA_DB.fetch_all("SELECT name FROM sqlite_master WHERE type='table';")))