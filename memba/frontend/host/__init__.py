from . import server as memba_server
from ...backend.base import misc as memba_misc
# from twikit import twikit

import asyncio
import functools
import logging
# import threading

memba_loop = asyncio.new_event_loop()
asyncio.set_event_loop(memba_loop)
memba_server = memba_server.Server()

log_func = functools.partial(memba_misc.log, "SERVER", **{}, level=logging.INFO)

log_func(msg="Starting server.")
memba_loop.run_until_complete(memba_server.start())
log_func(msg="Server started.")

try:
	memba_loop.run_until_complete(memba_server.loop())
except KeyboardInterrupt:
	log_func(msg="Closing server.")
	memba_loop.run_until_complete(memba_server.close())
	log_func(msg="Server closed.")
finally:
	memba_loop.close()