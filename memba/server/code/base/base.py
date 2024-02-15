import aiohttp.web

class Server:
	# async def websocket(self, request):
	# 	ws = aiohttp.web.WebSocketResponse()
	# 	await ws.prepare(request)
	# 	async for msg in ws:
	# 		if msg.type == aiohttp.WSMsgType.TEXT:
	# 			if msg.data == "close":
	# 				await ws.close()
	# 			else:
	# 				ws.send_str(msg.data + "/answer")
	# 		elif msg.type == aiohttp.WSMsgType.ERROR:
	# 			print("ws connection closed with exception %s" % ws.exception())
	# 	return ws

	comm = aiohttp.web.WebSocketResponse()
	core = aiohttp.web.Application()

	async def __init__(self):
		pass