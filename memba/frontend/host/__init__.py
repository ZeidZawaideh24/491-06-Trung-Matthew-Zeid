from . import server as memba_server
# from twikit import twikit

import asyncio
# import threading

memba_loop = asyncio.new_event_loop()
asyncio.set_event_loop(memba_loop)
memba_server = memba_server.Server()

print("[MSG] Starting server")
memba_loop.run_until_complete(memba_server.start())
print("[MSG] Server started")

async def loop():
	while True:
		print("loop")
		await asyncio.sleep(1)

try:
	memba_loop.run_until_complete(loop())
except KeyboardInterrupt:
	print("[MSG] Closing server")
	memba_loop.run_until_complete(memba_server.close())
	print("[MSG] Server closed")
finally:
	memba_loop.close()