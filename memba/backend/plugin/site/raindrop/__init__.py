import urllib.parse
import memba.backend.plugin.base.core as memba_plugin_core
import memba.backend.base.config as memba_config
import apscheduler.triggers.interval

import memba.backend.base.data as memba_data

import aiohttp
import json
import asyncio
import urllib.parse

API_URL = "https://api.raindrop.io/v1/"
CLIENT_ID = "6631b90194b900af9141962f"

async def start():
	print("RD Starting demo plugin.")

async def handle(*args, **kwargs):
	print("RD Handling job.", args, kwargs)

async def load(schedule: apscheduler.AsyncScheduler):
	print("RD Loading demo plugin.")

async def job_acquired(raw):
	print("RD Job acquired.", raw)

async def set_site_account(data: dict, func, server, *args, **kwargs):
	if "code" not in data:
		__import__("webbrowser").open_new_tab(
			urllib.parse.urlunparse((
				"https",
				"api.raindrop.io",
				f"/v1/oauth/authorize",
				"",
				urllib.parse.urlencode({
					"redirect_uri": f"http://{memba_config.CONFIG.host}:{memba_config.CONFIG.port}/api/v1/raindrop_account",
					"client_id": CLIENT_ID,
				}),
				""
			))
		)

		result = await asyncio.wait_for(
			server.process_queue(lambda _: _.get("kind", "") == "raindrop_account"),
			timeout=60
		)
		if result is None:
			return {
				"msg": "Authorization timed out."
			}
		data["data"] = {
			"code": result["code"]
		}
		data["msg"] = "Authorization successful."
		return await func(data)

async def upload(*args, **kwargs):
	print("RD Upload job.", args, kwargs)

MEMBA_PLUGIN_V1 = {
	"name": __name__,
	"flag": memba_plugin_core.v1.SERVE_FLAG.BOTH,
	"ver": "0.0.1",
	"evt": {
		"start": start,
		"load": load,
		"handle": handle,
		"set_site_account": set_site_account,
		"job_acquired": job_acquired,
		"upload": upload,
	},
}