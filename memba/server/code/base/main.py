__import__("sys").path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent.parent.parent.parent.absolute()))
__import__("sys").path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent / "lib"))

import memba.server.code.base.base as memba_base
import twikit

print(dir(memba_base))
print(dir(twikit))