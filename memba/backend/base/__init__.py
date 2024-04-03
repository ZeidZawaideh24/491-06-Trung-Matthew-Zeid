import memba.backend.plugin.base as memba_plugin
from . import data as memba_data
from . import track as memba_track
from . import misc as memba_misc

import asyncio

async def start():
	await memba_data.start()
	await memba_plugin.start()

	await memba_track.start()
	await memba_track.check(memba_plugin.PLUGIN_DB)

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
	await memba_track.close()
	await memba_plugin.close()
	await memba_data.close()

"""
[
	{
		"kind": "interval",
		"weeks": 1,
		"days": 1,
		"hours": 1,
		"minutes": 1,
		"seconds": 1,
		"microseconds": 1,
		"start_time": null,
		"end_time": null,
	},
	{
		"kind": "calendar",
		"years": 1,
		"months": 1,
		"weeks": 1,
		"days": 1,
		"hour": 1,
		"minute": 1,
		"second": 1,
		"start_time": null,
		"end_time": null,
	},
	{
		"kind": "cron",
		"year": 2020,
		"month": 1,
		"day": 1,
		"week": 1,
		"day_of_week": 1,
		"hour": 1,
		"minute": 1,
		"second": 1,
		"start_time": null,
		"end_time": null,
		"timezone": null,
	},
	{
		"kind": "and",
	},
	{
		"kind": "or",
	}
]
"""

# Spawn asyncio task to run memba_track

# Print all column of memba_account table using sqlite syntax
# print(await memba_data.DATA_DB.fetch_all("PRAGMA table_info(memba_account)"))

# List all tables name
# print(list(record["name"] for record in await memba_data.DATA_DB.fetch_all("SELECT name FROM sqlite_master WHERE type='table';")))