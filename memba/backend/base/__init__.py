import memba.backend.plugin.base.run as memba_plugin_run
from . import data as memba_data

async def start():
	await memba_plugin_run.run()
	pass

async def close():
	pass