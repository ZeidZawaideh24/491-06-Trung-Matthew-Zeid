from . import config as memba_config
from . import misc as memba_misc
from . import track as memba_track

import sqlalchemy
import sqlalchemy.dialects.sqlite
import databases
import sqlite3
import pathlib
import uuid
import hashlib

import apscheduler.abc
import dill
import attrs

@attrs.define(kw_only=True, eq=False)
class DillSerializer(apscheduler.abc.Serializer):
	def serialize(self, obj: object = None) -> bytes:
		return dill.dumps(obj)

	def deserialize(self, serialized: bytes = None):
		return dill.loads(serialized)

class ForeignKeyConnection(sqlite3.Connection):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.execute("PRAGMA foreign_keys = ON")

def make_table(name, *cols):
	meta = sqlalchemy.MetaData()
	return sqlalchemy.Table(name, meta, *cols)

DATA_DB: databases.Database | None = None

memba_account_table = make_table(
	"memba_account",
	sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False),
	# sqlalchemy.Column("user", sqlalchemy.Text, nullable=False, unique=True),
	sqlalchemy.Column("pwd", sqlalchemy.Text, nullable=False),
	sqlalchemy.Column("email", sqlalchemy.Text, nullable=False, unique=True),
	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now())
)

memba_account_key_table = make_table(
	"memba_account_key",
	sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False),
	sqlalchemy.Column("memba_id", sqlalchemy.Integer, nullable=False),
	sqlalchemy.Column("key", sqlalchemy.Text, nullable=False),
	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.ForeignKeyConstraint(["memba_id"], ["memba_account.id"])
)

site_account_table = make_table(
	"site_account",
	sqlalchemy.Column("memba_id", sqlalchemy.Integer, nullable=False),
	sqlalchemy.Column("user_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.Column("site_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.Column("updated", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.Column("json", sqlalchemy.JSON, nullable=False),
	sqlalchemy.PrimaryKeyConstraint("user_id", "site_id"),
	sqlalchemy.ForeignKeyConstraint(["memba_id"], ["memba_account.id"])
)

site_data_table = make_table(
	"site_data",
	sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False),
	sqlalchemy.Column("memba_id", sqlalchemy.Integer, nullable=False),
	sqlalchemy.Column("user_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.Column("site_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.Column("schedule_id", sqlalchemy.VARCHAR(36), nullable=True),
	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.Column("updated", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.Column("json", sqlalchemy.JSON, nullable=False),
	sqlalchemy.ForeignKeyConstraint(["memba_id"], ["memba_account.id"]),
	sqlalchemy.ForeignKeyConstraint(["user_id", "site_id"], ["site_account.user_id", "site_account.site_id"])
)

site_import_log_table = make_table(
	"site_import_log",
	sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False),
	sqlalchemy.Column("memba_id", sqlalchemy.Integer, nullable=False),
	sqlalchemy.Column("user_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.Column("site_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.Column("since", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.Column("url", sqlalchemy.Text, nullable=False),
	sqlalchemy.ForeignKeyConstraint(["memba_id"], ["memba_account.id"]),
	sqlalchemy.ForeignKeyConstraint(["user_id", "site_id"], ["site_account.user_id", "site_account.site_id"])
)

site_history_table = make_table(
	"site_history",
	sqlalchemy.Column("order", sqlalchemy.Integer),
	sqlalchemy.Column("url_id", sqlalchemy.Integer, primary_key=True, nullable=False),
	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.ForeignKeyConstraint(["url_id"], ["site_import_log.id"]),
);

site_export_log_table = make_table(
	"site_export_log",
	sqlalchemy.Column("url_id", sqlalchemy.Integer, nullable=False),
	sqlalchemy.Column("user_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.Column("site_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.PrimaryKeyConstraint("url_id", "user_id", "site_id"),
	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.ForeignKeyConstraint(["url_id"], ["site_import_log.id"]),
	sqlalchemy.ForeignKeyConstraint(["user_id", "site_id"], ["site_account.user_id", "site_account.site_id"])
);

async def start():
	global DATA_DB
	if DATA_DB is not None:
		return
	
	DATA_DB = databases.Database(f"sqlite+aiosqlite:///{memba_config.CONFIG.data_path}", factory=ForeignKeyConnection)
	await DATA_DB.connect()
	if pathlib.Path(memba_config.CONFIG.data_path).exists():
		memba_misc.log(
			"DATA",
			msg="Connecting to existing database.",
			level=memba_misc.logging.INFO
		)
	else:
		memba_misc.log(
			"DATA",
			msg="Creating new database.",
			level=memba_misc.logging.INFO
		)

		# Recursively create directory if it doesn't exist
		pathlib.Path(memba_config.CONFIG.data_path).parent.mkdir(parents=True, exist_ok=True)

		async with DATA_DB.connection() as conn:
			with open("memba/backend/data/main.sql", "r") as f:
				await conn.raw_connection.executescript(f.read())

async def close():
	global DATA_DB
	memba_misc.log(
		"DATA",
		msg="Closing database.",
		level=memba_misc.logging.INFO
	)
	await DATA_DB.disconnect()
	DATA_DB = None

###################### API ######################

def import_filter_query(memba_id, site_id, user_id):
	return site_history_table.join(
		site_import_log_table,
		(site_history_table.c.url_id == site_import_log_table.c.id) & (
			(site_import_log_table.c.memba_id == memba_id) &
			(site_import_log_table.c.site_id == site_id) &
			(site_import_log_table.c.user_id == user_id)
		)
	)

async def check_import_log(memba_id: int, site_id: str, user_id: str, url: str, since: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		return (await conn.fetch_one(
			sqlalchemy.select(site_history_table.c.url_id).select_from(
				import_filter_query(memba_id, site_id, user_id)
			).where(
				(site_import_log_table.c.url == url) &
				(site_import_log_table.c.since == since)
			)
		)) is not None

async def unique_import_log(memba_id: int, site_id: str, user_id: str, url: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		return (await conn.fetch_one(
			sqlalchemy.select(site_import_log_table.c.id).select().where(
				(site_import_log_table.c.memba_id == memba_id) &
				(site_import_log_table.c.site_id == site_id) &
				(site_import_log_table.c.user_id == user_id) &
				(site_import_log_table.c.url == url)
			)
		)) is not None

async def update_import_log(memba_id: int, site_id: str, user_id: str, url: str, since: str, cap=10):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		# Check if the cap is exceeded and delete the oldest entry if necessary
		count = await conn.fetch_val(
			sqlalchemy.select(sqlalchemy.func.count()).select_from(import_filter_query(memba_id, site_id, user_id))
		)
		if count >= cap:
			# Execute the query to fetch the oldest url_id
			await conn.execute(
				site_history_table.delete().where(
					site_history_table.c.url_id == await conn.fetch_val(sqlalchemy.select(site_history_table.c.url_id).select_from(
						import_filter_query(memba_id, site_id, user_id)
					).order_by(site_history_table.c.order.asc()).limit(1))
				)
			)

		url_id = await conn.execute(site_import_log_table.insert().values(
			memba_id=memba_id,
			site_id=site_id,
			user_id=user_id,
			url=url,
			since=since
		).returning(site_import_log_table.c.id))

		# Insert the new log url_id to site_history_table
		await conn.execute(site_history_table.insert().values(
			url_id=url_id
		))

async def get_export_queue(memba_id: int, site_id: str, user_id: str, cap=10):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		return await conn.fetch_all(
			site_import_log_table.select().where(
				(site_import_log_table.c.memba_id == memba_id) &
				~site_import_log_table.c.id.in_(
					sqlalchemy.select(site_export_log_table.c.url_id).select().where(
						(site_export_log_table.c.user_id == user_id) &
						(site_export_log_table.c.site_id == site_id)
					)
				)
			).limit(cap)
		)

async def set_export_queue(url_id: int, user_id: str, site_id: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		await conn.execute(site_export_log_table.insert().values(
			url_id=url_id,
			user_id=user_id,
			site_id=site_id
		))

async def set_account(email: str, pwd: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		if await conn.fetch_one(memba_account_table.select().where(memba_account_table.c.email == email)):
			raise ValueError("Account already exist.")
		await conn.execute(memba_account_table.insert().values(
			pwd=hashlib.sha256(pwd.encode()).hexdigest(),
			email=email
		))

async def del_account(email: str, pwd: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		account = await conn.fetch_one(memba_account_table.select().where(memba_account_table.c.email == email))
		if not account:
			raise ValueError("Account does not exist.")
		if account["pwd"] != hashlib.sha256(pwd.encode()).hexdigest():
			raise ValueError("Incorrect password.")

		await conn.execute(memba_account_table.delete().where(memba_account_table.c.email == email))

async def get_account(email: str, pwd: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		account = await conn.fetch_one(memba_account_table.select().where(memba_account_table.c.email == email))
		if not account:
			raise ValueError("Account does not exist.")
		if account["pwd"] != hashlib.sha256(pwd.encode()).hexdigest():
			raise ValueError("Incorrect password.")
		return {
			"id": account["id"]
		}

async def set_site_account(memba_id: int, site_id: str, data: dict):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		acc_id = uuid.uuid4().hex

		await conn.execute(site_account_table.insert().values(
			memba_id=memba_id,
			user_id=acc_id,
			site_id=site_id,
			json=data
		))

		return acc_id

async def update_site_account(memba_id: int, site_id: str, user_id: str, data: dict):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		await conn.execute(site_account_table.update().where(
			(site_account_table.c.memba_id == memba_id) &
			(site_account_table.c.user_id == user_id) &
			(site_account_table.c.site_id == site_id)
		).values(
			json=data
		))

async def get_site_account(memba_id: int, site_id: str, user_id: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		return await conn.fetch_one(site_account_table.select().where(
			(site_account_table.c.memba_id == memba_id) &
			(site_account_table.c.user_id == user_id) &
			(site_account_table.c.site_id == site_id)
		))

async def get_site_account_all(memba_id: int, site_id: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		return await conn.fetch_all(site_account_table.select().where(
			(site_account_table.c.memba_id == memba_id) &
			(site_account_table.c.site_id == site_id)
		))

async def del_site_account(memba_id: int, site_id: str, user_id: str):
	global DATA_DB
	await memba_track.del_track(memba_id, site_id, user_id)
	async with DATA_DB.connection() as conn:
		await conn.execute(site_account_table.delete().where(
			(site_account_table.c.memba_id == memba_id) &
			(site_account_table.c.user_id == user_id) &
			(site_account_table.c.site_id == site_id)
		))

async def get_site_data(memba_id: int, site_id: str, user_id: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		return await conn.fetch_one(site_data_table.select().where(
			(site_data_table.c.memba_id == memba_id) &
			(site_data_table.c.user_id == user_id) &
			(site_data_table.c.site_id == site_id)
		))

async def set_site_data(memba_id: int, site_id: str, user_id: str, data: dict):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		row = await get_site_data(memba_id, site_id, user_id)
		if row is None:
			await conn.execute(site_data_table.insert().values(
				memba_id=memba_id,
				user_id=user_id,
				site_id=site_id,
				json=data
			))
			return

		# Update the row
		await conn.execute(site_data_table.update().where(
			(site_data_table.c.memba_id == memba_id) &
			(site_data_table.c.user_id == user_id) &
			(site_data_table.c.site_id == site_id)
		).values(
			json=data
		))

async def del_site_data(memba_id: int, site_id: str, user_id: str):
	global DATA_DB
	await memba_track.del_track(memba_id, site_id, user_id)
	async with DATA_DB.connection() as conn:
		await conn.execute(site_data_table.delete().where(
			(site_data_table.c.memba_id == memba_id) &
			(site_data_table.c.user_id == user_id) &
			(site_data_table.c.site_id == site_id)
		))

async def set_schedule(memba_id: int, site_id: str, user_id: str, schedule_id: str):
	global DATA_DB
	async with DATA_DB.connection() as conn:
		row = await get_site_data(memba_id, site_id, user_id)
		if row is None:
			raise ValueError("Site data does not exist.")

		await conn.execute(site_data_table.update().where(
			(site_data_table.c.memba_id == memba_id) &
			(site_data_table.c.user_id == user_id) &
			(site_data_table.c.site_id == site_id)
		).values(schedule_id=schedule_id))