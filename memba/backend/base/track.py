import asyncio
import pathlib

# https://apscheduler.readthedocs.io/en/master/
import apscheduler # https://github.com/agronholm/apscheduler/issues/465
import apscheduler.datastores.sqlalchemy
import sqlalchemy.ext.asyncio

import memba.backend.base.data as memba_data
import memba.backend.base.config as memba_config
import memba.backend.base.misc as memba_misc
import memba.backend.plugin.base as memba_plugin

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
	await memba_plugin.trigger(
		memba_misc.camel_to_snake(event.__class__.__name__), False,
		raw=event
	)

async def track():
	global TRACK_DB
	global TRACK_SCHEDULE
	global TRACK_EVT
	global TRACK_EVT_INST

	try:
		async with apscheduler.AsyncScheduler(data_store=TRACK_DB) as scheduler:
			TRACK_SCHEDULE = scheduler
			TRACK_EVT_INST = TRACK_SCHEDULE.subscribe(handle, TRACK_EVT)
			# job_list = await TRACK_SCHEDULE.get_jobs()

			# [TODO] Keep track of which plugins is still exist
				# To not trigger leftover jobs
			# for job in job_list:
			# 	print(job.id)

			await memba_plugin.trigger(
				"load", False,
				schedule=TRACK_SCHEDULE
			)

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
	TRACK_DB = apscheduler.datastores.sqlalchemy.SQLAlchemyDataStore(
		engine=TRACK_ENGINE,
		# serializer=memba_data.DillSerializer
	)

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

###################### API ######################

import apscheduler.triggers.calendarinterval
import apscheduler.triggers.cron
import apscheduler.triggers.interval
import apscheduler.triggers.combining
import apscheduler.triggers.date

"""
[
	{
		"kind": "interval",
		"weeks": 1,
		"days": 1,
		"hours": 1,
		"minutes": 1,
		"seconds": 1,
		"microseconds": 1,
		"start_time": null,
		"end_time": null,
	},
	{
		"kind": "calendar",
		"years": 1,
		"months": 1,
		"weeks": 1,
		"days": 1,
		"hour": 1,
		"minute": 1,
		"second": 1,
		"start_time": null,
		"end_time": null,
	},
	{
		"kind": "cron",
		"year": 2020,
		"month": 1,
		"day": 1,
		"week": 1,
		"day_of_week": 1,
		"hour": 1,
		"minute": 1,
		"second": 1,
		"start_time": null,
		"end_time": null,
		"timezone": null,
	},
	{
		"kind": "and",
		"data": [...],
	},
	{
		"kind": "or",
		"data": [...],
	}
]
"""

async def build_trigger(data):
	# Build the final trigger object from the json
	curr = None
	match data["kind"]:
		case "interval":
			curr = apscheduler.triggers.interval.IntervalTrigger(
				weeks=data["weeks"],
				days=data["days"],
				hours=data["hours"],
				minutes=data["minutes"],
				seconds=data["seconds"],
				microseconds=data["microseconds"],
				start_time=data["start_time"],
				end_time=data["end_time"],
			)
		case "calendar":
			curr = apscheduler.triggers.calendarinterval.CalendarIntervalTrigger(
				years=data["years"],
				months=data["months"],
				weeks=data["weeks"],
				days=data["days"],
				hour=data["hour"],
				minute=data["minute"],
				second=data["second"],
				start_time=data["start_time"],
				end_time=data["end_time"],
			)
		case "cron":
			curr = apscheduler.triggers.cron.CronTrigger(
				year=data["year"],
				month=data["month"],
				day=data["day"],
				week=data["week"],
				day_of_week=data["day_of_week"],
				hour=data["hour"],
				minute=data["minute"],
				second=data["second"],
				start_time=data["start_time"],
				end_time=data["end_time"],
				timezone=data["timezone"],
			)
		case "and":
			curr = apscheduler.triggers.combining.AndTrigger(
				asyncio.gather(
					*[build_trigger(x) for x in data["data"]],
				)
			)
		case "or":
			curr = apscheduler.triggers.combining.OrTrigger(
				asyncio.gather(
					*[build_trigger(x) for x in data["data"]],
				)
			)
		case _:
			pass
	return curr

async def set_track(memba_id: int, site_id: str, user_id: str, data: dict):
	global TRACK_SCHEDULE

	row = await memba_data.get_site_data(memba_id, site_id, user_id)
	if row is not None and row["schedule_id"] is not None:
		return None

	return str(TRACK_SCHEDULE.add_job(
		memba_plugin.v1_handle,
		await build_trigger(data),
		kwargs={
			"__memba_id__": memba_id,
			"__site_id__": site_id,
			"__user_id__": user_id,
		}
	))

async def get_track(memba_id: int, site_id: str, user_id: str):
	global TRACK_SCHEDULE
	job_uuid = await memba_data.get_site_data(memba_id, site_id, user_id)
	if job_uuid is None:
		return None
	return await TRACK_SCHEDULE.data_store.get_jobs([job_uuid])

async def del_track(memba_id: int, site_id: str, user_id: str):
	global TRACK_SCHEDULE
	job_uuid = await memba_data.get_site_data(memba_id, site_id, user_id)
	if job_uuid is None:
		return None
	await memba_data.set_schedule(memba_id, site_id, user_id, None)
	return await TRACK_SCHEDULE.remove_job(job_uuid)

async def get_all_site_id(account):
	return await memba_data.get_all_site_id(account)