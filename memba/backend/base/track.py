import asyncio
import pathlib

# https://apscheduler.readthedocs.io/en/master/
import apscheduler # https://github.com/agronholm/apscheduler/issues/465
import apscheduler.datastores.sqlalchemy
import sqlalchemy.ext.asyncio

import memba.backend.base.config as memba_config
import memba.backend.base.misc as memba_misc

TRACK_ENGINE: sqlalchemy.ext.asyncio.AsyncEngine = None
TRACK_DB: apscheduler.datastores.sqlalchemy.SQLAlchemyDataStore = None
TRACK_SCHEDULE: apscheduler.AsyncScheduler = None

TRACK_EVT = []
TRACK_EVT_INST = None
for evt_class in vars(apscheduler):
	if isinstance(getattr(apscheduler, evt_class), type) and (
		issubclass(getattr(apscheduler, evt_class), apscheduler.Event) or
		issubclass(getattr(apscheduler, evt_class), apscheduler.DataStoreEvent)
	) and evt_class not in ["Event", "DataStoreEvent"]:
		TRACK_EVT.append(getattr(apscheduler, evt_class))

async def handle(event: apscheduler.Event):
	# [TODO] Event reroute to all plugins
	print(f"Received {event.__class__.__name__}")

async def track():
	global TRACK_DB
	global TRACK_SCHEDULE
	global TRACK_EVT
	global TRACK_EVT_INST

	try:
		async with apscheduler.AsyncScheduler(data_store=TRACK_DB) as scheduler:
			TRACK_SCHEDULE = scheduler
			TRACK_EVT_INST = TRACK_SCHEDULE.subscribe(handle, TRACK_EVT)
			await TRACK_SCHEDULE.run_until_stopped()
	except Exception as e:
		memba_misc.log(
			"SCHEDULE",
			msg=f"Error: {e}",
			level=memba_misc.logging.ERROR
		)

async def check(plugin_db):
	# [TODO] Keep track of which plugins is still exist
		# To not trigger leftover jobs
	global TRACK_SCHEDULE

	job_list = await TRACK_SCHEDULE.get_jobs()

	for job in job_list:
		pass

async def start():
	global TRACK_ENGINE
	global TRACK_DB
	
	if pathlib.Path(memba_config.CONFIG.schedule_path).exists():
		memba_misc.log(
			"SCHEDULE",
			msg="Connecting to existing schedule database.",
			level=memba_misc.logging.INFO
		)
	else:
		memba_misc.log(
			"SCHEDULE",
			msg="Creating new schedule database.",
			level=memba_misc.logging.INFO
		)
	
	TRACK_ENGINE = sqlalchemy.ext.asyncio.create_async_engine(f"sqlite+aiosqlite:///{memba_config.CONFIG.schedule_path}")
	pathlib.Path(memba_config.CONFIG.schedule_path).parent.mkdir(parents=True, exist_ok=True)
	TRACK_DB = apscheduler.datastores.sqlalchemy.SQLAlchemyDataStore(engine=TRACK_ENGINE)

async def close():
	global TRACK_SCHEDULE
	global TRACK_EVT_INST
	memba_misc.log(
		"SCHEDULE",
		msg="Closing schedule.",
		level=memba_misc.logging.INFO
	)
	TRACK_EVT_INST.unsubscribe()
	await asyncio.gather(TRACK_SCHEDULE.stop(), TRACK_SCHEDULE.wait_until_stopped())