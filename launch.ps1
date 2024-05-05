# https://github.com/ZeidZawaideh24/491-06-Trung-Matthew-Zeid

# Credential setup
# https://stackoverflow.com/questions/38333752/trying-to-understand-wincred-with-git-for-windows-confused

# Useful stuff
# https://news.ycombinator.com/item?id=39442273

# Fetch submodule
git submodule update --init --recursive

python -m pip install -r .\requirements.txt

# Run the current python folder using ./server/code/base/main.py as beginning
python .\memba\main.py

# sqlalchemy prev ver: 1.4.51

# Curent roadblockers:
# data.db schema

# Test client side code
# var socket = new WebSocket("ws://localhost:30303/dev/ws");

# socket.addEventListener("open", (event) => {
#   socket.send("Hello Server!");
# });

# // Listen for messages
# socket.addEventListener("message", (event) => {
#   console.log("Message from server ", event.data);
# });
# socket.addEventListener("close", (event) => {
#   console.log("Close server ", event.data);
# });

# https://github.com/HackerNews/API

# Personal stuff
# &"C:\Program Files (Sole)\ComfyUI\python_embeded\python.exe" .\memba\main.py --server


		
		# site_track = await conn.execute(site_track_table.select().where(site_track_table.c.memba_id == account["id"])).fetchall()
		# for track in site_track:
		# 	memba_track.del_track(account["id"], track["site_id"])
		# 	await del_site_track(account["id"], track["site_id"])

# Spawn asyncio task to run memba_track

# Print all column of memba_account table using sqlite syntax
# print(await memba_data.DATA_DB.fetch_all("PRAGMA table_info(memba_account)"))

# List all tables name
# print(list(record["name"] for record in await memba_data.DATA_DB.fetch_all("SELECT name FROM sqlite_master WHERE type='table';")))

# site_track_table = make_table(
# 	"site_track",
# 	sqlalchemy.Column("schedule_id", sqlalchemy.VARCHAR(36), primary_key=True, nullable=False),
# 	sqlalchemy.Column("memba_id", sqlalchemy.Integer, nullable=False),
# 	sqlalchemy.Column("site_id", sqlalchemy.VARCHAR(36), nullable=False),
# 	sqlalchemy.ForeignKeyConstraint(["memba_id"], ["memba_account.id"]),
# 	sqlalchemy.ForeignKeyConstraint(["site_id"], ["site_account.site_id"])
# )

# async def set_account_key(memba_id: int, key: str):
# 	global DATA_DB
# 	async with DATA_DB.connection() as conn:
# 		await conn.execute(memba_account_key_table.insert().values(
# 			memba_id=memba_id,
# 			key=key)
# 		)

# async def set_site_track(memba_id: int, site_id: str, schedule_id: str):
# 	global DATA_DB
# 	async with DATA_DB.connection() as conn:
# 		await conn.execute(site_track_table.insert().values(
# 			memba_id=memba_id,
# 			site_id=site_id,
# 			schedule_id=schedule_id
# 		))

# async def get_site_track(memba_id: int, site_id: str):
# 	global DATA_DB
# 	async with DATA_DB.connection() as conn:
# 		return await conn.execute(site_track_table.select().where(
# 			(site_track_table.c.memba_id == memba_id) &
# 			(site_track_table.c.site_id == site_id)
# 		)).first()
	
# async def del_site_track(memba_id: int, site_id: str):
# 	global DATA_DB
# 	async with DATA_DB.connection() as conn:
# 		await conn.execute(site_account_table.delete().where(
# 			(site_account_table.c.memba_id == memba_id) &
# 			(site_account_table.c.site_id == site_id)
# 		))

# 		await conn.execute(site_data_table.delete().where(
# 			(site_data_table.c.memba_id == memba_id) &
# 			(site_data_table.c.site_id == site_id)
# 		)).fetchall()

# 		await conn.execute(site_track_table.delete().where(
# 			(site_track_table.c.memba_id == memba_id) &
# 			(site_track_table.c.site_id == site_id)
# 		))



# async def del_track(account, plugin):
# 	global TRACK_SCHEDULE
# 	job_uuid = await memba_data.get_site_track(account, plugin)
# 	if job_uuid is None:
# 		return None
# 	await memba_data.del_site_track(account, plugin)
# 	return TRACK_SCHEDULE.remove_job(job_uuid)



# async def get_track(account, plugin):
# 	global TRACK_SCHEDULE
# 	job_uuid = await memba_data.get_site_track(account, plugin)
# 	if job_uuid is None:
# 		return None
# 	return TRACK_SCHEDULE.get_job(job_uuid)


# await memba_data.del_site_data(memba_id, site_id, user_id)
# Update schedule_id to None



	# try:
	# 	# print(globals()['sys'].modules)
	# 	print(__builtins__.keys())
	# 	# pass
	# except Exception as e:
	# 	print("Error: ", e)
	# try:
	# 	await schedule.add_schedule(
	# 		memba_plugin_core.v1_handle,
	# 		# lambda *args, **kwargs: handle(*args, **kwargs),
	# 		apscheduler.triggers.interval.IntervalTrigger(
	# 			seconds=5,
	# 		),
	# 		kwargs={
	# 			"test": "test",
	# 			"__memba_name__": "demo"
	# 		},
	# 	)
	# except Exception as e:
	# 	print(e)
	# 	# Stack trace of the exception
	# 	import traceback
	# 	traceback.print_exc()