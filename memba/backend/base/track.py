import asyncio
import pathlib

import apscheduler # https://github.com/agronholm/apscheduler/issues/465
import apscheduler.datastores.sqlalchemy

import memba.backend.base.config as memba_config
import memba.backend.base.misc as memba_misc
import memba.backend.base.data as memba_data

TRACK_ENGINE = None
TRACK_DB = None
TRACK_TASK = None
TRACK_SCHEDULE = None

async def schedule():
	global TRACK_DB
	global TRACK_SCHEDULE
	try:
		TRACK_SCHEDULE = apscheduler.AsyncScheduler(data_store=TRACK_DB)
		await TRACK_SCHEDULE.run_until_stopped()
	except Exception as e:
		memba_misc.log(
			"SCHEDULE",
			msg=f"Error: {e}",
			level=memba_misc.logging.ERROR
		)

async def start():
	global TRACK_ENGINE
	global TRACK_DB
	global TRACK_TASK
	
	if pathlib.Path(memba_config.config["schedule_path"]).exists():
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
	
	TRACK_ENGINE = apscheduler.datastores.sqlalchemy.create_async_engine(f"sqlite+aiosqlite:///{memba_config.config['schedule_path']}")
	pathlib.Path(memba_config.config["schedule_path"]).parent.mkdir(parents=True, exist_ok=True)
	TRACK_DB = apscheduler.datastores.sqlalchemy.SQLAlchemyDataStore(engine=TRACK_ENGINE)
	TRACK_TASK = schedule()

async def close():
	global TRACK_TASK
	global TRACK_SCHEDULE
	memba_misc.log(
		"SCHEDULE",
		msg="Closing schedule.",
		level=memba_misc.logging.INFO
	)
	await asyncio.gather(TRACK_SCHEDULE.stop(), TRACK_SCHEDULE.wait_until_stopped())