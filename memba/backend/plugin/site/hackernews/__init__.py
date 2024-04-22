import memba.backend.plugin.base.core as memba_plugin_core
import apscheduler.triggers.interval

async def start():
	print("Starting demo plugin.")

async def handle(*args, **kwargs):
	print("Handling job.", args, kwargs)

async def load(schedule: apscheduler.AsyncScheduler):
	print("Loading demo plugin.")

async def job_acquired(raw):
	print("Job acquired.", raw)

MEMBA_PLUGIN_V1 = {
	"name": __name__,
	"flag": memba_plugin_core.v1.SERVE_FLAG.BOTH,
	"ver": "0.0.1",
	"evt": {
		"start": start,
		"load": load,
		"handle": handle,
		"job_acquired": job_acquired,
	},
}