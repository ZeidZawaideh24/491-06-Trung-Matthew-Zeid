__import__("sys").path.insert(0, __import__("pathlib").Path(__file__).parent.parent.parent.absolute())

print(__import__("sys").path)

# 3rd party
import aiohttp.web

from code.base.base import Server

print(Server)