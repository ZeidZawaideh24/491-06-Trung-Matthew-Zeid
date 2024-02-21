(lambda: exec("""
import sys
import pathlib
temp_path = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(temp_path.parent.parent.parent.absolute()))
sys.path.insert(0, str(temp_path / "lib"))
"""))()

import memba.server.code.base.base as memba_base
# from twikit import twikit

import asyncio
# import threading

memba_loop = asyncio.new_event_loop()
asyncio.set_event_loop(memba_loop)
memba_server = memba_base.Server()

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