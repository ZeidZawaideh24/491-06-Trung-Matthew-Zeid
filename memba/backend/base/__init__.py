import memba.backend.plugin.base as memba_plugin
from . import data as memba_data

async def start():
	await memba_data.start()
	await memba_plugin.start()

	# Print all column of memba_account table using sqlite syntax
	# print(await memba_data.DATA_DB.fetch_all("PRAGMA table_info(memba_account)"))

	pass

async def close():
	await memba_plugin.close()
	await memba_data.close()
	pass