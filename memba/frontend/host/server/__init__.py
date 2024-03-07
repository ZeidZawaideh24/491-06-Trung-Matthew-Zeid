import aiohttp
import aiohttp.web
import asyncio
import uuid
import logging
import functools

import memba.backend.base.misc as memba_misc
import memba.backend.plugin.base as memba_plugin_run
import memba.backend.base as memba_base

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

	async def start(self):
		self.app.add_routes(self.route)
		await self.run.setup()
		self.site = aiohttp.web.TCPSite(self.run, "localhost", 30303)
		await self.site.start()
		await memba_base.start()

	async def close(self):
		await memba_base.close()
		asyncio.gather(*[
			self.state[client_id].socket.close() \
				for client_id in self.state \
					if self.state[client_id].socket is not None and \
						not self.state[client_id].socket.closed
		])
		await self.site.stop()
		await self.app.shutdown()
		await self.app.cleanup()
		await self.run.cleanup()

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