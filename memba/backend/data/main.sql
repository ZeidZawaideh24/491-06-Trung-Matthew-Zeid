-- SQLite

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "memba_account" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	"user" TEXT NOT NULL UNIQUE,
	"pwd" TEXT NOT NULL,
	"email" TEXT NOT NULL UNIQUE,
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "memba_account_key" (
	"memba_id" INTEGER PRIMARY KEY NOT NULL,
	"key" TEXT NOT NULL,
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id")
);

CREATE TABLE IF NOT EXISTS "site_account" (
	"memba_id" INTEGER NOT NULL,
	"user_id" VARCHAR(36) NOT NULL, -- uuid
	"site_id" VARCHAR(36) NOT NULL, -- uuid, basically plugin id
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"json" TEXT NOT NULL,
	PRIMARY KEY ("user_id", "site_id"),
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id")
);

CREATE TABLE IF NOT EXISTS "site_data" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"memba_id" INTEGER NOT NULL,
	"user_id" VARCHAR(36) NOT NULL, -- uuid
	"site_id" VARCHAR(36) NOT NULL, -- uuid
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"json" TEXT NOT NULL, -- Used to track what link downloaded/uploaded so far
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id"),
	FOREIGN KEY ("user_id") REFERENCES "site_account"("user_id"), -- uuid
	FOREIGN KEY ("site_id") REFERENCES "site_account"("site_id") -- uuid
);

CREATE TABLE IF NOT EXISTS "site_track" (
	"schedule_id" VARCHAR(36) PRIMARY KEY NOT NULL, -- uuid
	"memba_id" INTEGER NOT NULL,
	"site_id" VARCHAR(36) NOT NULL, -- uuid
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id"),
	FOREIGN KEY ("site_id") REFERENCES "site_account"("site_id") -- uuid
);

-- CREATE TABLE IF NOT EXISTS "memba_schedule" (
-- 	"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
-- 	"memba_id" INTEGER NOT NULL,
-- 	"cron" TEXT NOT NULL,
-- 	"last" DATETIME DEFAULT CURRENT_TIMESTAMP,
-- 	"task" TEXT NOT NULL,
-- 	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
-- 	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id"),
-- );

-- CREATE TABLE IF NOT EXISTS "memba_schedule_cron" (
-- 	"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
-- 	"schedule_id" INTEGER NOT NULL,
-- 	"cron" TEXT NOT NULL,
-- 	FOREIGN KEY ("schedule_id") REFERENCES "memba_schedule"("id"),
-- );

-- CREATE TABLE IF NOT EXISTS "site_link" (
-- 	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
-- 	"memba_id" INTEGER NOT NULL,
-- 	"user_id" BLOB NOT NULL, -- uuid
-- 	"site_id" BLOB NOT NULL, -- uuid
-- 	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
-- 	"data" TEXT NOT NULL, -- This should store chunk of links
-- 	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id"),
-- 	FOREIGN KEY ("user_id") REFERENCES "site_account"("user_id"), -- uuid
-- 	FOREIGN KEY ("site_id") REFERENCES "site_account"("site_id") -- uuid
-- );

-- # site_link_table = make_table(
-- # 	"site_link",
-- # 	sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True, nullable=False),
-- # 	sqlalchemy.Column("memba_id", sqlalchemy.Integer, nullable=False),
-- # 	sqlalchemy.Column("user_id", sqlalchemy.BLOB, nullable=False),
-- # 	sqlalchemy.Column("site_id", sqlalchemy.BLOB, nullable=False),
-- # 	sqlalchemy.Column("created", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
-- # 	sqlalchemy.Column("json", sqlalchemy.Text, nullable=False),
-- # 	sqlalchemy.ForeignKeyConstraint(["memba_id"], ["memba_account.id"]),
-- # 	sqlalchemy.ForeignKeyConstraint(["user_id", "site_id"], ["site_account.user_id", "site_account.site_id"])
-- # )