(lambda: exec("""
import sys
import pathlib
script_path = pathlib.Path(__file__).parent
sys.path.insert(0, str(script_path / "backend" / "lib"))
sys.path.insert(0, str(script_path.parent.absolute()))
"""))()

MEMBA_VERSION = "0.0.1"

# Temporary
from memba.frontend import host