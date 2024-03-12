# All plugins should import this file
# This file should contains basic stuff to let a plugin running

(lambda: exec("""
global v1
memba_run = __import__("memba.backend.plugin.base").backend.plugin.base
v1_lib = type("v1_lib", (object,), {
	"PLUGIN_DB": memba_run.PLUGIN_DB,
	"SERVE_FLAG": memba_run.SERVE_FLAG
})
v1 = v1_lib()
"""))()