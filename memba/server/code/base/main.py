__import__("sys").path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent.parent.parent.parent.absolute()))

import memba.server.code.base.base as memba_base

print(dir(memba_base))