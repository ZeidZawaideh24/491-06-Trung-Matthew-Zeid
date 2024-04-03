from . import config as memba_config
from . import misc as memba_misc

import sqlalchemy
import sqlalchemy.dialects.sqlite
import databases
import sqlite3
import pathlib

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
	sqlalchemy.Column("user", sqlalchemy.Text, nullable=False, unique=True),
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
	sqlalchemy.Column("json", sqlalchemy.Text, nullable=False),
	sqlalchemy.PrimaryKeyConstraint("user_id", "site_id"),
	sqlalchemy.ForeignKeyConstraint(["memba_id"], ["memba_account.id"])
)

site_data_table = make_table(
	"site_log",
	sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False),
	sqlalchemy.Column("memba_id", sqlalchemy.Integer, nullable=False),
	sqlalchemy.Column("user_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.Column("site_id", sqlalchemy.VARCHAR(36), nullable=False),
	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.Column("updated", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
	sqlalchemy.Column("json", sqlalchemy.Text, nullable=False),
	sqlalchemy.ForeignKeyConstraint(["memba_id"], ["memba_account.id"]),
	sqlalchemy.ForeignKeyConstraint(["user_id", "site_id"], ["site_account.user_id", "site_account.site_id"])
)

# site_link_table = make_table(
# 	"site_link",
# 	sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False),
# 	sqlalchemy.Column("memba_id", sqlalchemy.Integer, nullable=False),
# 	sqlalchemy.Column("user_id", sqlalchemy.BLOB, nullable=False),
# 	sqlalchemy.Column("site_id", sqlalchemy.BLOB, nullable=False),
# 	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
# 	sqlalchemy.Column("json", sqlalchemy.Text, nullable=False),
# 	sqlalchemy.ForeignKeyConstraint(["memba_id"], ["memba_account.id"]),
# 	sqlalchemy.ForeignKeyConstraint(["user_id", "site_id"], ["site_account.user_id", "site_account.site_id"])
# )

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