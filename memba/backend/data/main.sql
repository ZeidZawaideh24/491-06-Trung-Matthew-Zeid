-- SQLite

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "memba_account" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	"user" TEXT NOT NULL UNIQUE,
	"pwd" TEXT NOT NULL,
	"email" TEXT NOT NULL UNIQUE,
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP
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

CREATE TABLE IF NOT EXISTS "site_account" (
	"memba_id" INTEGER NOT NULL,
	"user_id" BLOB NOT NULL, -- uuid
	"site_id" BLOB NOT NULL, -- uuid, basically plugin id
	"data" TEXT NOT NULL,
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated" DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY ("user_id", "site_id"),
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id")
);

CREATE TABLE IF NOT EXISTS "site_log" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"memba_id" INTEGER NOT NULL,
	"user_id" BLOB NOT NULL, -- uuid
	"site_id" BLOB NOT NULL, -- uuid
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"data" TEXT NOT NULL,
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id"),
	FOREIGN KEY ("user_id") REFERENCES "site_account"("user_id"), -- uuid
	FOREIGN KEY ("site_id") REFERENCES "site_account"("site_id") -- uuid
);

CREATE TABLE IF NOT EXISTS "site_link" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"memba_id" INTEGER NOT NULL,
	"user_id" BLOB NOT NULL, -- uuid
	"site_id" BLOB NOT NULL, -- uuid
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"data" TEXT NOT NULL,
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id"),
	FOREIGN KEY ("user_id") REFERENCES "site_account"("user_id"), -- uuid
	FOREIGN KEY ("site_id") REFERENCES "site_account"("site_id") -- uuid
);