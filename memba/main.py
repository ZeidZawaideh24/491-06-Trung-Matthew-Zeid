(lambda: exec("""
import sys
import pathlib
script_path = pathlib.Path(__file__)
sys.path.insert(0, str(script_path.parent / "backend" / "lib"))
sys.path.insert(0, str(script_path.parent.parent.absolute()))
"""))()

from memba.frontend import host