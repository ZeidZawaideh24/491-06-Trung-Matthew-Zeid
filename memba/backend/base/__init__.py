import memba.backend.plugin.base.run as memba_plugin_run
from . import data as memba_data

async def start():
	await memba_data.start()
	await memba_plugin_run.run()

	# Print all column of memba_account table using sqlite syntax
	# print(await memba_data.DATA_DB.fetch_all("PRAGMA table_info(memba_account)"))

	pass

async def close():
	await memba_data.close()
	pass