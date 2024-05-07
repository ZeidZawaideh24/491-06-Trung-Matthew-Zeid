import memba.backend.plugin.base.core as memba_plugin_core

import memba.backend.base.data as memba_data
import memba.backend.base.config as memba_config
import memba.backend.base.misc as memba_misc

import asyncio
import urllib.parse
import json
import datetime
import aiohttp

CLIENT_ID = "66383aa7facf5e5f885ceb4f"
CLIENT_SECRET = "b2e97880-0ac7-4f0f-b5d3-4f08b235bf50"
COLLECTION_ID = -1 # 43802593

async def handle(*args, **kwargs):
	if kwargs["__flag__"] == memba_plugin_core.v1.SERVE_FLAG.EXPORT:
		res_account = await memba_data.get_site_account(kwargs["__memba_id__"], "raindrop", kwargs["__user_id__"])
		res_site = await memba_data.get_site_data(kwargs["__memba_id__"], "raindrop", kwargs["__user_id__"])
		json_account_data = res_account["json"]
		json_site_data = res_site["json"]

		try:
			async with aiohttp.ClientSession() as session:
				if datetime.datetime.now().timestamp() - json_account_data["token"]["time"] > 1209599:
					async with session.post(
						"https://api.raindrop.io/v1/oauth/access_token",
						data={
							"client_id": CLIENT_ID,
							"client_secret": CLIENT_SECRET,
							"grant_type": "refresh_token",
							"refesh_token": json_account_data["token"]["refresh_token"],
						}
					) as resp:
						resp_json = await resp.json()
						json_account_data["token"]["access_token"] = resp_json["access_token"]
						json_account_data["token"]["refresh_token"] = resp_json["refresh_token"]
						json_account_data["token"]["time"] = datetime.datetime.now().timestamp()
						await memba_data.update_site_account(kwargs["__memba_id__"], "raindrop", kwargs["__user_id__"], json_account_data)
				
				json_res = {
					"items": []
				}
				while True:
					res_queue = await memba_data.get_export_queue(kwargs["__memba_id__"], "raindrop", kwargs["__user_id__"], 50)

					if len(res_queue) == 0:
						return

					for res in res_queue:
						json_res["items"].append({
							"pleaseParse": True,
							"link": res["url"],
							"collectionId": json_site_data.get("collection_id", COLLECTION_ID),
							"tags": json_site_data.get("tags", ["Memba"]),
						})
						await memba_data.set_export_queue(
							res["id"],
							kwargs["__user_id__"],
							"raindrop",
						)

					async with session.post(
						"https://api.raindrop.io/rest/v1/raindrops",
						headers={
							"Authorization": f"Bearer {json_account_data['token']['access_token']}"
						},
						json=json_res
					) as resp:
						pass

					# 120 requests per minute, sleep for 0.5s
					await asyncio.sleep(json_site_data.get("rate", 2))
		except Exception as e:
			memba_misc.log(
				"PLUGIN",
				msg=f"Raindrop {json_account_data['username']} failed. {e}",
				level=memba_misc.logging.ERROR,
				**{
					"name": kwargs["__memba_id__"],
				}
			)

async def set_site_account(data: dict, func, server, *args, **kwargs):
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

	result_code = await asyncio.wait_for(
		server.process_queue(lambda _: _.get("kind", "") == "raindrop_account"),
		timeout=60
	)
	if result_code is None:
		return {
			"msg": "Authorization timed out."
		}

	async with aiohttp.ClientSession() as session:
		async with session.post(
			"https://api.raindrop.io/v1/oauth/access_token",
			headers={
				"Content-Type": "application/json",
			},
			json={
				"client_id": CLIENT_ID,
				"client_secret": CLIENT_SECRET,
				"code": result_code["code"],
				"grant_type": "authorization_code",
				"redirect_uri": f"http://_", # This was compared against the one set in the Raindrop.io app
			}
		) as resp:
			# Check for mimetype
			if resp.content_type != "application/json":
				return {
					"msg": f"Autohrization failed: {await resp.text()}"
				}
			
			result_access = await resp.json()

			data["data"] = {
				"code": result_code["code"],
				"token": {
					"access_token": result_access["access_token"],
					"refresh_token": result_access["refresh_token"],
					"time": datetime.datetime.now().timestamp(),
				},
			}
			data["msg"] = "Authorization successful."
			return await func(data)

MEMBA_PLUGIN_V1 = {
	"name": __name__,
	"flag": memba_plugin_core.v1.SERVE_FLAG.EXPORT,
	"ver": "0.0.1",
	"evt": {
		"handle": handle,
		"set_site_account": set_site_account,
	},
}