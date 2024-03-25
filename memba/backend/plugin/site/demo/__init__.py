import memba.backend.plugin.base.core as memba_plugin_core

async def start():
	print("Starting demo plugin.")

MEMBA_PLUGIN_V1 = {
	"name": __name__,
	"flag": memba_plugin_core.v1.SERVE_FLAG.BOTH,
	"ver": "0.0.1",
	"evt": {
		"start": start
	},
}