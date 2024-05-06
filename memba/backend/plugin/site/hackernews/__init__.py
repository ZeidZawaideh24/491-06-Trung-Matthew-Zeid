import memba.backend.plugin.base.core as memba_plugin_core

import memba.backend.base.data as memba_data
import memba.backend.base.misc as memba_misc

import aiohttp
import lxml.html
import json
import asyncio
import datetime

# https://news.ycombinator.com/favorites?id=deadcoder0904
	# Dead at page 5
# https://news.ycombinator.com/favorites?id=kawera
	# Dead at page 1
# https://news.ycombinator.com/user?id=gkoberger
	# No page

async def handle(*args, **kwargs):
	if kwargs["__flag__"] == memba_plugin_core.v1.SERVE_FLAG.IMPORT:
		res_account = await memba_data.get_site_account(kwargs["__memba_id__"], "hackernews", kwargs["__user_id__"])
		res_site = await memba_data.get_site_data(kwargs["__memba_id__"], "hackernews", kwargs["__user_id__"])
		json_account_data = res_account["json"]
		json_site_data = res_site["json"]

		i = 1
		async with aiohttp.ClientSession() as session:
			link_list = []
			while True:
				async with session.get(f"https://news.ycombinator.com/favorites?id={json_account_data['username']}&p={i}") as resp:
					if resp.status != 200:
						return
					html_inst = lxml.html.fromstring(await resp.text())
					link_tag = html_inst.xpath("//td[@class='title']/span/a")
					age_tag = html_inst.xpath("//span[@class='age']")

					link_list_temp = []
					for link, age in zip(link_tag, age_tag):
						href = link.get("href")
						if href:
							if href.startswith("item?id="):
								href = f"https://news.ycombinator.com/{href}"
							link_list_temp.append({
								"url": href,
								"since": datetime.datetime.fromisoformat(age.get("title")),
							})

					# HN expect chunk of 30 links per page so when we either encounter
						# page with less than 30 links or no more links, we stop
					link_list.extend(link_list_temp)
					if len(link_list_temp) < 30 or \
						await memba_plugin_core.v1_check(link_list_temp, **kwargs):
						await memba_plugin_core.v1_import(link_list, cap=30, **kwargs)
						break
				memba_misc.log(
					"PLUGIN",
					msg=f"HN {json_account_data['username']} page {i} done.",
					level=memba_misc.logging.INFO
				)
				i += 1
				await asyncio.sleep(json_site_data.get("rate", 5))

async def set_site_account(data, func, server, *args, **kwargs):
	data["data"] = {
		"username": data["data"],
	}
	data["msg"] = "Account set."
	return await func(data)

MEMBA_PLUGIN_V1 = {
	"name": __name__,
	"flag": memba_plugin_core.v1.SERVE_FLAG.IMPORT,
	"ver": "0.0.1",
	"evt": {
		"handle": handle,
		"set_site_account": set_site_account,
	},
}