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

async def v1_check(url_list, **kwargs):
	import memba.backend.base.data as memba_data
	return any([
		await memba_data.check_import_log(kwargs["__memba_id__"], kwargs["__site_id__"], kwargs["__user_id__"], url["url"], url["since"])
		for url in url_list
	])

async def v1_import(url_list, **kwargs):
	import memba.backend.base.data as memba_data
	for url in reversed(url_list):
		if await memba_data.unique_import_log(kwargs["__memba_id__"], kwargs["__site_id__"], kwargs["__user_id__"], url["url"]) or \
			await memba_data.check_import_log(kwargs["__memba_id__"], kwargs["__site_id__"], kwargs["__user_id__"], url["url"], url["since"]):
			continue
		await memba_data.update_import_log(kwargs["__memba_id__"], kwargs["__site_id__"], kwargs["__user_id__"], url["url"], url["since"], kwargs.get("cap", 10))

async def v1_export(url_list, **kwargs):
	pass