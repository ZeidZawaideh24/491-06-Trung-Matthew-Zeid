(lambda: exec("""
import sys
import pathlib
script_path = pathlib.Path(__file__).parent
sys.path.insert(0, str(script_path / "backend" / "lib"))
sys.path.insert(0, str(script_path.parent.absolute()))
"""))()

# [TODO] Maybe support two paradigm: client/server and cmd
# client/server: with scheduler to run task
# cmd: use system task scheduler like cron

import logging

logging.basicConfig(
	level=logging.DEBUG,
	format="%(asctime)s [%(levelname)s] %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S"
)

# Temporary
from memba.frontend import host