import asyncio
import pathlib
import datetime

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

async def schedule_handle(event: apscheduler.Event):
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
			TRACK_EVT_INST = TRACK_SCHEDULE.subscribe(schedule_handle, TRACK_EVT)
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

	# Temporary manual cleanup
	# https://github.com/agronholm/apscheduler/issues/903
	job_list = await TRACK_SCHEDULE.get_jobs()
	for job in job_list:
		await TRACK_SCHEDULE.data_store.release_job(
			TRACK_SCHEDULE.identity, job.id,
			apscheduler._structures.JobResult(
				job_id=job.id,
				outcome=apscheduler._structures.JobOutcome.cancelled,
				expires_at=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
			)
		)

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
				weeks=data.get("weeks", 0),
				days=data.get("days", 0),
				hours=data.get("hours", 0),
				minutes=data.get("minutes", 0),
				seconds=data.get("seconds", 0),
				microseconds=data.get("microseconds", 0),
				start_time=data.get("start_time", datetime.datetime.now()),
				end_time=data.get("end_time", None),
			)
		case "calendar":
			curr = apscheduler.triggers.calendarinterval.CalendarIntervalTrigger(
				years=data.get("years", 0),
				months=data.get("months", 0),
				weeks=data.get("weeks", 0),
				days=data.get("days", 0),
				hour=data.get("hour", 0),
				minute=data.get("minute", 0),
				second=data.get("second", 0),
				start_time=data.get("start_time", datetime.datetime.now()),
				end_time=data.get("end_time", None),
			)
		case "cron":
			curr = apscheduler.triggers.cron.CronTrigger(
				year=data.get("year", None),
				month=data.get("month", None),
				day=data.get("day", None),
				week=data.get("week", None),
				day_of_week=data.get("day_of_week", None),
				hour=data.get("hour", None),
				minute=data.get("minute", None),
				second=data.get("second", None),
				start_time=data.get("start_time", datetime.datetime.now()),
				end_time=data.get("end_time", None),
				timezone=data.get("timezone", None),
			)
		case "and":
			curr = apscheduler.triggers.combining.AndTrigger(
				await asyncio.gather(
					*[build_trigger(x) for x in data["data"]],
				)
			)
		case "or":
			curr = apscheduler.triggers.combining.OrTrigger(
				await asyncio.gather(
					*[build_trigger(x) for x in data["data"]],
				)
			)
		case _:
			pass
	return curr

async def track_handle(*args, **kwargs):
	await memba_plugin.trigger("handle", kwargs.get("__site_id__", False), *args, **kwargs)

async def set_track(memba_id: int, site_id: str, user_id: str, data: dict):
	global TRACK_SCHEDULE

	row = await memba_data.get_site_data(memba_id, site_id, user_id)
	if row is not None and row["schedule_id"] is not None:
		return None
	
	return str(await TRACK_SCHEDULE.add_schedule(
		track_handle,
		await build_trigger(data),
		max_running_jobs = 1,
		conflict_policy = apscheduler.ConflictPolicy.do_nothing,
		id=f"{memba_id}-{site_id}-{user_id}",
		kwargs={
			"__memba_id__": memba_id,
			"__site_id__": site_id,
			"__user_id__": user_id,
			"__flag__": getattr(memba_plugin.PLUGIN_DB, site_id).__memba_plugin__.flag
		}
	))

async def get_track(memba_id: int, site_id: str, user_id: str):
	global TRACK_SCHEDULE
	job_uuid = await memba_data.get_site_data(memba_id, site_id, user_id)
	if job_uuid["schedule_id"] is None:
		return None
	return await TRACK_SCHEDULE.data_store.get_schedules([job_uuid["schedule_id"]])

async def del_track(memba_id: int, site_id: str, user_id: str):
	global TRACK_SCHEDULE
	job_uuid = await memba_data.get_site_data(memba_id, site_id, user_id)
	if job_uuid is None:
		return None
	await memba_data.set_schedule(memba_id, site_id, user_id, None)
	return await TRACK_SCHEDULE.remove_schedule(job_uuid)

async def get_all_site_id(account):
	return await memba_data.get_all_site_id(account)