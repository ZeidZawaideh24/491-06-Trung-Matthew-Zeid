import memba.backend.plugin.base.core as memba_plugin_core
import apscheduler.triggers.interval

import memba.backend.base.data as memba_data

import aiohttp
import lxml.html
import json

async def start():
	print("HN Starting demo plugin.")

async def handle(*args, **kwargs):
	print("HN Handling job.", args, kwargs)

async def load(schedule: apscheduler.AsyncScheduler):
	print("HN Loading demo plugin.")

async def job_acquired(raw):
	print("HN Job acquired.", raw)

async def download(*args, **kwargs):
	print("HN Download job.", args, kwargs)

	# Get current account data
	res = await memba_data.get_site_data(kwargs["__memba_id__"], "hackernews", kwargs["__user_id__"])
	json_data = json.loads(res["json"])

	i = 1
	async with aiohttp.ClientSession() as session:
		link_list = []
		while True:
			async with session.get(f"https://news.ycombinator.com/favorites?id={json_data['username']}&p={i}") as resp:
				if resp.status != 200:
					return
				html_inst = lxml.html.fromstring(await resp.text())
				link_tag = html_inst.cssselect("td.title > span > a")

				link_list_temp = []
				for link in link_tag:
					link_list_temp.append(link.get("href"))

				# HN expect chunk of 30 links per page so when we either encounter
					# page with less than 30 links or no more links, we stop
				link_list.extend(link_list_temp)
				if len(link_list_temp) < 30 or any(link in json_data["history"] for link in link_list_temp):
					json_data["history"].extend(link_list_temp)
					await memba_data.set_site_data(kwargs["__memba_id__"], "hackernews", kwargs["__user_id__"], json.dumps(json_data))
					break
				i += 1

MEMBA_PLUGIN_V1 = {
	"name": __name__,
	"flag": memba_plugin_core.v1.SERVE_FLAG.BOTH,
	"ver": "0.0.1",
	"evt": {
		"start": start,
		"load": load,
		"handle": handle,
		"job_acquired": job_acquired,
		"download": download,
	},
}