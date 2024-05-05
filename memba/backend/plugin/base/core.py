# All plugins should import this file
# This file should contains basic stuff to let a plugin running

# "PLUGIN_DB": memba_run.PLUGIN_DB,

(lambda: exec("""
global v1
memba_run = __import__("memba.backend.plugin.base").backend.plugin.base
v1_lib = type("v1_lib", (object,), {
	"SERVE_FLAG": memba_run.SERVE_FLAG,
	# "TRIGGER_FUNC": staticmethod(memba_run.trigger),
})
v1 = v1_lib()
"""))()

# async def v1_handle(*args, **kwargs):
# 	await globals()['v1'].TRIGGER_FUNC("handle", kwargs.get("__memba_id__", False), *args, **kwargs)