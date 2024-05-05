import aiohttp
import aiohttp.web
import asyncio
import uuid
import logging
import functools
import json

import aiohttp.web_response

import memba.backend.base.misc as memba_misc
import memba.backend.base as memba_base
import memba.backend.base.track as memba_track
import memba.backend.base.data as memba_data
import memba.backend.plugin.base as memba_plugin

class State:
	socket: aiohttp.web.WebSocketResponse | None = None

class Server:
	route: aiohttp.web.RouteTableDef | None = None
	app: aiohttp.web.Application | None = None
	run: aiohttp.web.AppRunner | None = None
	site: aiohttp.web.TCPSite | None = None
	queue: asyncio.Queue | None = None
	state: dict[str, State] = {}

	def __init__(self):
		self.route = aiohttp.web.RouteTableDef()
		self.app = aiohttp.web.Application()
		self.run = aiohttp.web.AppRunner(self.app)
		self.queue = asyncio.Queue()

		self.route.get("/dev/ws")(self.socket_handle)
		self.route.post("/api/v1/set_account")(self.set_account)
		self.route.get("/api/v1/get_account")(self.get_account)
		self.route.post("/api/v1/del_account")(self.del_account)
		self.route.post("/api/v1/set_site_account")(self.set_site_account)
		self.route.get("/api/v1/get_site_account")(self.get_site_account)
		self.route.get("/api/v1/get_site_account_all")(self.get_site_account_all)
		self.route.post("/api/v1/del_site_account")(self.del_site_account)
		self.route.post("/api/v1/set_site_data")(self.set_site_data)
		self.route.get("/api/v1/get_site_data")(self.get_site_data)
		self.route.post("/api/v1/del_site_data")(self.del_site_data)
		self.route.post("/api/v1/set_track")(self.set_track)
		self.route.get("/api/v1/get_track")(self.get_track)
		self.route.post("/api/v1/del_track")(self.del_track)
		self.route.get("/api/v1/raindrop_account")(self.raindrop_account)

	async def process_queue(self, condition):
		temporary_storage = []
		target_item = None

		while True: #not self.queue.empty():
			item = await self.queue.get()
			if condition(item):  # Condition is a function to determine if the item is the one needed
				target_item = item
				break
			else:
				temporary_storage.append(item)

		# Restore items back to the queue
		# Reversed to maintain the original order in the queue
		for item in reversed(temporary_storage):
			await self.queue.put(item)

		return target_item

	async def start(self):
		self.app.add_routes(self.route)
		await self.run.setup()
		self.site = aiohttp.web.TCPSite(self.run, "localhost", 30303)
		await self.site.start()
		await memba_base.start()

	async def loop(self):
		await memba_base.loop()

	async def close(self):
		await memba_base.close()
		asyncio.gather(*[
			self.state[client_id].socket.close() \
				for client_id in self.state \
					if self.state[client_id].socket is not None and \
						not self.state[client_id].socket.closed
		])
		if self.site._server is not None:
			await self.site.stop()
		await self.app.shutdown()
		await self.app.cleanup()
		if self.run is not None:
			await self.run.cleanup()

	async def change_account(self, func, request: aiohttp.web.Request):
		data = await request.json()
		try:
			if "email" in data and "password" in data:
				return aiohttp.web.json_response({
					"status": "OK",
					"data": await func(data["email"], data["password"])
				})
		except ValueError:
			pass
		return aiohttp.web.json_response({
			"status": "ERR",
		})

	async def set_account(self, request: aiohttp.web.Request):
		return await self.change_account(memba_data.set_account, request)
		
	async def get_account(self, request: aiohttp.web.Request):
		return await self.change_account(memba_data.get_account, request)
		
	async def del_account(self, request: aiohttp.web.Request):
		return await self.change_account(memba_data.del_account, request)
	
	@classmethod
	async def set_site_account_handler(cls, data: dict):
		try:
			await memba_data.set_site_account(data["memba_id"], data["site_id"], data["data"])
			return aiohttp.web.json_response({
				"status": "OK",
				"msg": data["msg"]
			})
		except:
			return aiohttp.web.json_response({
				"status": "ERR",
				"msg": "Error setting account."
			})
	
	@classmethod
	async def set_site_account_fall(cls, data: dict):
		try:
			await memba_data.set_site_account(data["memba_id"], data["site_id"], data["data"])
			return aiohttp.web.json_response({
				"status": "OK",
				"data": {
					"msg": "Account set."
				}
			})
		except:
			return aiohttp.web.json_response({
				"status": "ERR",
				"data": {
					"msg": "Error setting account."
				}
			})

	async def set_site_account(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		data["param"] = request.rel_url.query
		res = await memba_plugin.trigger(
			"set_site_account", data["site_id"],
			data=data,
			server=self,
			func=Server.set_site_account_handler,
			fall=Server.set_site_account_fall
		)
		
		err_flag = False
		data_list = []
		msg_list = []
		for r in res:
			json_response = json.loads(r.body.decode("utf-8"))
			if json_response.get("status") == "ERR":
				err_flag = True
			data_list.append(json_response.get("data", {}))
			msg_list.append(json_response.get("msg", ""))

		return aiohttp.web.json_response({
			"status": "ERR" if err_flag else "OK",
			"data": data_list,
			"msg": msg_list,
		})

	async def get_site_account(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data or "user_id" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		res = {
			k: str(v) for k, v in dict(await memba_data.get_site_account(
				data["memba_id"], data["site_id"], data["user_id"]
			)).items()
		}
		if res is None:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		return aiohttp.web.json_response({
			"status": "OK",
			"data": res,
		})
	
	async def get_site_account_all(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		res = [
			{k: str(v) for k, v in dict(x).items()}
				for x in await memba_data.get_site_account_all(data["memba_id"], data["site_id"])
		]
		if res is None:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		return aiohttp.web.json_response({
			"status": "OK",
			"data": res,
		})

	async def del_site_account(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data or "user_id" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		await memba_data.del_site_account(data["memba_id"], data["site_id"], data["user_id"])
		return aiohttp.web.json_response({
			"status": "OK",
		})

	async def set_site_data(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data or "user_id" not in data or "data" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		try:
			await memba_data.set_site_data(data["memba_id"], data["site_id"], data["user_id"], json.loads(data["data"]))
			return aiohttp.web.json_response({
				"status": "OK",
			})
		except Exception as e:
			memba_misc.log(
				"SERVER",
				msg="Error setting site data ({}).".format(e),
				level=logging.ERROR
			)
			return aiohttp.web.json_response({
				"status": "ERR",
			})
	
	async def get_site_data(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data or "user_id" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		all_res = await memba_data.get_site_data(
			data["memba_id"], data["site_id"], data["user_id"]
		)
		if all_res is None:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		res = {
			k: str(v) for k, v in dict(all_res).items()
		}
		return aiohttp.web.json_response({
			"status": "OK",
			"data": res,
		})
	
	async def del_site_data(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data or "user_id" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		await memba_data.del_site_data(data["memba_id"], data["site_id"], data["user_id"])
		return aiohttp.web.json_response({
			"status": "OK",
		})

	async def set_track(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data or "user_id" not in data or "data" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		try:
			res = await memba_track.set_track(data["memba_id"], data["site_id"], data["user_id"], json.loads(data["data"]))
			if res is None:
				return aiohttp.web.json_response({
					"status": "ERR",
				})
			await memba_data.set_schedule(data["memba_id"], data["site_id"], data["user_id"], res)
			return aiohttp.web.json_response({
				"status": "OK",
				"data": res,
			})
		except Exception as e:
			memba_misc.log(
				"SERVER",
				msg="Error setting track ({}).".format(e),
				level=logging.ERROR
			)
			return aiohttp.web.json_response({
				"status": "ERR",
			})
	
	async def get_track(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data or "user_id" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		try:
			res = [
				{
					"schedule_id": str(_.id),
					"next_fire_time": str(_.next_fire_time),
					"last_fire_time": str(_.last_fire_time),
				} for _ in await memba_track.get_track(data["memba_id"], data["site_id"], data["user_id"])
			]
			if len(res) == 0:
				return aiohttp.web.json_response({
					"status": "ERR",
				})
			return aiohttp.web.json_response({
				"status": "OK",
				"data": res,
			})
		except:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
	
	async def del_track(self, request: aiohttp.web.Request):
		data = await request.json()
		if "memba_id" not in data or "site_id" not in data or "user_id" not in data:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		res = await memba_track.del_track(data["memba_id"], data["site_id"], data["user_id"])
		if res is None:
			return aiohttp.web.json_response({
				"status": "ERR",
			})
		memba_data.set_schedule(data["memba_id"], data["site_id"], data["user_id"], None)
		return aiohttp.web.json_response({
			"status": "OK",
		})

	async def raindrop_account(self, request: aiohttp.web.Request):
		code = request.rel_url.query.get("code", None)
		if code is None:
			await self.queue.put({
				"status": "ERR",
				"kind": "raindrop_account",
			})
		else:
			await self.queue.put({
				"status": "OK",
				"kind": "raindrop_account",
				"code": code,
			})

	"""
	Handles the websocket connection.
	:param request: aiohttp.web.Request
	:return: None
	"""
	async def socket_handle(self, request: aiohttp.web.Request):
		client_id = request.rel_url.query.get("client_id", None)
		api_path = request.path.split("?")[0].split("#")[0]
		curr_state: State | None = self.state.get(client_id, None)

		if curr_state is None:
			client_id = str(uuid.uuid4())
			self.state[client_id] = (curr_state := State())
			curr_state.socket = aiohttp.web.WebSocketResponse()
			await curr_state.socket.prepare(request)
			await self.state[client_id].socket.send_json({
				"command": "client_id_init",
				"format": "str",
				"version": memba_misc.MEMBA_VERSION,
			})
			await self.state[client_id].socket.send_str(client_id)

		log_tag = {
			"client_id": client_id,
			"api_path": api_path,
		}

		try:
			async for msg in curr_state.socket:
				match msg.type:
					case aiohttp.WSMsgType.TEXT:
						memba_misc.log(
							"SERVER WS",
							msg=msg.data,
							level=logging.DEBUG,
							**{
								**log_tag,
								"msg_type": "text",
							}
						)
					case aiohttp.WSMsgType.BINARY:
						memba_misc.log(
							"SERVER WS",
							msg=msg.data,
							level=logging.DEBUG,
							**{
								**log_tag,
								"msg_type": "binary",
							}
						)
					case aiohttp.WSMsgType.CLOSE:
						memba_misc.log(
							"SERVER WS",
							msg="Connection closed.",
							level=logging.DEBUG,
							**{
								**log_tag,
								"msg_type": "close",
							}
						)
					case aiohttp.WSMsgType.ERROR:
						memba_misc.log(
							"SERVER WS",
							msg="Connection closed ({}).".format(curr_state.socket.exception()),
							level=logging.ERROR,
							**log_tag
						)
					case _:
						memba_misc.log(
							"SERVER WS",
							msg="Unknown message type.",
							level=logging.ERROR,
							**log_tag
						)
		except (aiohttp.ClientError, aiohttp.ClientPayloadError, ConnectionResetError) as err:
			memba_misc.log(
				"SERVER WS",
				msg="Sending failed ({}).".format(err),
				level=logging.ERROR,
				**log_tag
			)
		except Exception as err:
			memba_misc.log(
				"SERVER WS",
				msg="Unknown error ({}).".format(err),
				level=logging.ERROR,
				**log_tag
			)
		finally:
			memba_misc.log(
				"SERVER WS",
				msg="Closing connection.",
				level=logging.DEBUG,
				**log_tag
			)
		
		return curr_state.socket