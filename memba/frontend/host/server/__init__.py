import aiohttp
import aiohttp.web
import asyncio
import uuid

from memba.main import MEMBA_VERSION

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

	async def close(self):
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
				"version": MEMBA_VERSION,
			})
			await self.state[client_id].socket.send_str(client_id)

		header_log = "[CLIENT_ID {}] [{}]".format(client_id, api_path)

		try:
			async for msg in curr_state.socket:
				match msg.type:
					case aiohttp.WSMsgType.TEXT:
						print("[MSG] {} [DATA TEXT] {}".format(header_log, msg.data))
					case aiohttp.WSMsgType.BINARY:
						print("[MSG] {} [DATA BINARY] {}".format(header_log, msg.data))
					case aiohttp.WSMsgType.CLOSE:
						print("[MSG] {} [DATA CLOSE] Connection closed.".format(header_log))
					case aiohttp.WSMsgType.ERROR:
						print("[ERROR] {} [INFO {}] Connection closed.".format(header_log, curr_state.socket.exception()))
					case _:
						print("[ERROR] {} [INFO {}] Unknown message type.".format(header_log, msg.type))
		except (aiohttp.ClientError, aiohttp.ClientPayloadError, ConnectionResetError) as err:
			print("[ERROR] {} [INFO {}] Sending failed.".format(header_log, err))
		except Exception as err:
			print("[ERROR] {} [INFO {}] Unknown error.".format(header_log, err))
		finally:
			print("[MSG] {} Closing connection.".format(header_log))
		
		return curr_state.socket