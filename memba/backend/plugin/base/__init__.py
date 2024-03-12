import enum
import logging
import pathlib
import importlib.util
import sys

import memba.backend.base.misc as memba_misc

PLUGIN_DB = type("v1_plugin_db", (object,), {})

class SERVE_FLAG(enum.Enum):
	TOOL = 0
	IMPORT = 1
	EXPORT = 2
	BOTH = 3

async def start():
	# [TODO] Loop through directory of plugins through config, not hardcoded

	memba_misc.log(
		"PLUGIN",
		msg="Starting plugin loader.",
		level=logging.INFO
	)

	v1_plugin = type("v1_plugin", (object,), {})
	
	plugin_dir = pathlib.Path(__file__).parent.parent / "site"
	for plugin_path in plugin_dir.iterdir():
		msg = "\033[33mPlugin loader encountered error while loading, ignoring"
		if plugin_path.is_dir():
			try:
				plugin_spec = importlib.util.spec_from_file_location(
					f"MEMBA_PLUGIN_V1.{plugin_path.name}",
					str(plugin_path / "__init__.py"),
					submodule_search_locations=[str(plugin_path)]
				)
				plugin_module = importlib.util.module_from_spec(plugin_spec)
				sys.modules[f"MEMBA_PLUGIN_V1.{plugin_path.name}"] = plugin_module
				plugin_spec.loader.exec_module(plugin_module)

				setattr(PLUGIN_DB, plugin_path.name, v1_plugin())
				v1_plugin_obj = v1_plugin()
				setattr(PLUGIN_DB, plugin_path.name, v1_plugin_obj)
				v1_plugin_meta_obj = v1_plugin()
				setattr(v1_plugin_obj, "__memba_plugin_v1__", v1_plugin_meta_obj)
				for k, v in plugin_module.MEMBA_PLUGIN_V1.items():
					setattr(v1_plugin_meta_obj, k, v)

				for k, v in plugin_module.__dict__.items():
					if k != "MEMBA_PLUGIN_V1" and k != "__memba_plugin_v1__":
						setattr(v1_plugin_obj, k, v)

				del sys.modules[f"MEMBA_PLUGIN_V1.{plugin_path.name}"]

				memba_misc.log(
					"PLUGIN",
					msg=f"Plugin loaded successfully.",
					level=logging.INFO,
					**{
						"name": plugin_path.name,
					}
				)

				continue
			except Exception as e:
				msg += f" ({e})"
		msg += ".\033[0m"
		memba_misc.log(
			"PLUGIN",
			msg=msg,
			level=logging.WARNING,
			**{
				"name": plugin_path.name,
			}
		)

	memba_misc.log(
		"PLUGIN",
		msg="Plugin loader finished.",
		level=logging.INFO
	)

async def close():
	pass