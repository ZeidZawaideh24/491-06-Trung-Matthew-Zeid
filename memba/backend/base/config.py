import argparse
import pprint

CONFIG = argparse.ArgumentParser()

CONFIG.add_argument("--data-path", help="Path to data db", default="data/memba.db")
CONFIG.add_argument("--schedule-path", help="Path to schedule db", default="data/schedule.db")
CONFIG.add_argument("--plugin-path", help="Path to plugin", action="append", default=["memba/backend/plugin/site"])
CONFIG.add_argument("--server", help="Run as server", action="store_true")

CONFIG.add_argument("--host", type=str, default="localhost")
CONFIG.add_argument("--port", type=int, default=30303)

CONFIG.add_argument("extra", nargs=argparse.REMAINDER)

CONFIG = CONFIG.parse_args()

async def config_api(path, data, kind="post"):
	async with __import__("aiohttp").ClientSession() as session:
	# async with aiohttp.ClientSession() as session:
		async with getattr(session, kind)(f"http://{CONFIG.host}:{CONFIG.port}/api/v1/{path}", json=data) as resp:
		# async with session.post(f"http://{CONFIG.host}:{CONFIG.port}/api/v1/{path}", json=data) as resp:
			return await resp.json()

def config_event():
	global CONFIG

	if len(CONFIG.extra) > 0:
		import asyncio
		match CONFIG.extra[0]:
			case "set_account":
				match asyncio.run(config_api("set_account", {
					"email": CONFIG.extra[1],
					"password": CONFIG.extra[2],
				})):
					case {"status": "OK"}:
						print("Account set.")
					case {"status": "ERR"}:
						print("Error setting account.")
			case "get_account":
				res = asyncio.run(config_api("get_account", {
					"email": CONFIG.extra[1],
					"password": CONFIG.extra[2],
				}, "get"))
				if res["status"] == "OK":
					print("Account exists. ID:", res["data"]["id"])
				else:
					print("Account does not exist.")
			case "del_account":
				match asyncio.run(config_api("del_account", {
					"email": CONFIG.extra[1],
					"password": CONFIG.extra[2],
				})):
					case {"status": "OK"}:
						print("Account deleted.")
					case {"status": "ERR"}:
						print("Error deleting account.")
			case "set_site_account":
				res = asyncio.run(config_api("set_site_account", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
					"data": CONFIG.extra[3] if len(CONFIG.extra) > 3 else ""
				}))
				if res["status"] == "OK":
					print(*res["msg"])
				else:
					print("Error setting site account.")
			case "get_site_account":
				res = asyncio.run(config_api("get_site_account", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
					"user_id": CONFIG.extra[3],
				}, "get"))
				if res["status"] == "OK":
					print(f"Date: {res['data']['updated']}")
				else:
					print("Site account does not exist.")
			case "get_site_account_all":
				res = asyncio.run(config_api("get_site_account_all", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
				}, "get"))
				if res["status"] == "OK":
					print(f"Site accounts for {CONFIG.extra[2]}:")
					for acc in res["data"]:
						print(f"ID: {acc['user_id']}, Date: {acc['updated']}")
				else:
					print("Site account does not exist.")
			case "del_site_account":
				match asyncio.run(config_api("del_site_account", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
					"user_id": CONFIG.extra[3],
				})):
					case {"status": "OK"}:
						print("Site account deleted.")
					case {"status": "ERR"}:
						print("Error deleting site account.")
			case "set_site_data":
				match asyncio.run(config_api("set_site_data", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
					"user_id": CONFIG.extra[3],
					"data": CONFIG.extra[4],
				})):
					case {"status": "OK"}:
						print("Site data set.")
					case {"status": "ERR"}:
						print("Error setting site data.")
			case "get_site_data":
				res = asyncio.run(config_api("get_site_data", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
					"user_id": CONFIG.extra[3],
				}, "get"))
				if res["status"] == "OK":
					pprint.pprint(res["data"])
				else:
					print("Site data does not exist.")
			case "del_site_data":
				match asyncio.run(config_api("del_site_data", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
					"user_id": CONFIG.extra[3],
				}))["status"]:
					case {"status": "OK"}:
						print("Site data deleted.")
					case {"status": "ERR"}:
						print("Error deleting site data.")
			case "set_track":
				res = asyncio.run(config_api("set_track", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
					"user_id": CONFIG.extra[3],
					"data": CONFIG.extra[4],
				}))
				if res["status"] == "OK":
					print("Track set.")
				else:
					print("Error setting track.")
			case "get_track":
				res = asyncio.run(config_api("get_track", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
					"user_id": CONFIG.extra[3],
				}, "get"))
				if res["status"] == "OK":
					for track in res["data"]:
						print(f"ID: {track['schedule_id']}, Next: {track['next_fire_time']}, Last: {track['last_fire_time']}")
				else:
					print("Track does not exist.")
			case "del_track":
				match asyncio.run(config_api("del_track", {
					"memba_id": CONFIG.extra[1],
					"site_id": CONFIG.extra[2],
					"user_id": CONFIG.extra[3],
				}))["status"]:
					case {"status": "OK"}:
						print("Track deleted.")
					case {"status": "ERR"}:
						print("Error deleting track.")
			case _:
				print("Unknown command.")