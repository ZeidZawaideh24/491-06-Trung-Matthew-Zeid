(lambda: exec("""
import sys
import pathlib
temp_path = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(temp_path.parent.parent.parent.absolute()))
sys.path.insert(0, str(temp_path / "lib"))
"""))()

import memba.server.code.base.base as memba_base
from twikit import twikit

print(dir(memba_base))
print(dir(twikit))