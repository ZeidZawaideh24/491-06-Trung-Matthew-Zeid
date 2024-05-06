-- SQLite

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS "memba_account" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	"pwd" TEXT NOT NULL,
	"email" TEXT NOT NULL UNIQUE,
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "site_account" (
	"memba_id" INTEGER NOT NULL,
	"user_id" VARCHAR(36) NOT NULL, -- uuid
	"site_id" VARCHAR(36) NOT NULL, -- uuid, basically plugin id
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"json" JSON NOT NULL,
	PRIMARY KEY ("user_id", "site_id"),
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "site_data" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"memba_id" INTEGER NOT NULL,
	"user_id" VARCHAR(36) NOT NULL, -- uuid
	"site_id" VARCHAR(36) NOT NULL, -- uuid
	"schedule_id" VARCHAR(36), -- uuid
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"json" JSON NOT NULL, -- Used to track what link downloaded/uploaded so far
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id") ON DELETE CASCADE,
	FOREIGN KEY ("user_id", "site_id") REFERENCES "site_account"("user_id", "site_id") ON DELETE CASCADE -- uuid
);

CREATE TABLE IF NOT EXISTS "site_import_log" (
	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"memba_id" INTEGER NOT NULL,
	"user_id" VARCHAR(36) NOT NULL, -- uuid
	"site_id" VARCHAR(36) NOT NULL, -- uuid
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"since" DATETIME DEFAULT CURRENT_TIMESTAMP,
	"url" TEXT NOT NULL,
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id") ON DELETE CASCADE,
	FOREIGN KEY ("user_id", "site_id") REFERENCES "site_account"("user_id", "site_id") ON DELETE CASCADE -- uuid
);

-- Only store N urls per set of memba_id, user_id, site_id.
CREATE TABLE IF NOT EXISTS "site_history" (
	"order" INTEGER, -- Used to track the order of the url
	"url_id" INTEGER PRIMARY KEY NOT NULL, -- Used to prevent url deletion if being used to track history
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY ("url_id") REFERENCES "site_import_log"("id") ON DELETE CASCADE
);

CREATE TRIGGER increment_order AFTER INSERT ON "site_history"
BEGIN
	UPDATE "site_history" SET "order" = (SELECT IFNULL(MAX("order"), 0) + 1 FROM "site_history") WHERE "rowid" = new.rowid;
END;

-- Mark the url as done for set of user_id, site_id. memba_id will be same.
CREATE TABLE IF NOT EXISTS "site_export_log" (
	"url_id" INTEGER NOT NULL, -- Used to track the url
	"user_id" VARCHAR(36) NOT NULL, -- uuid, separate from url_id
	"site_id" VARCHAR(36) NOT NULL, -- uuid, used to check if all active exporter are done
	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY ("url_id", "user_id", "site_id"),
	FOREIGN KEY ("url_id") REFERENCES "site_import_log"("id") ON DELETE CASCADE,
	FOREIGN KEY ("user_id", "site_id") REFERENCES "site_account"("user_id", "site_id") ON DELETE CASCADE -- uuid
);

------------------------------

-- PRAGMA foreign_keys = ON;

-- CREATE TABLE IF NOT EXISTS "memba_account" (
-- 	"id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
-- 	"pwd" TEXT NOT NULL,
-- 	"email" TEXT NOT NULL UNIQUE,
-- 	"created" DATETIME DEFAULT CURRENT_TIMESTAMP
-- );

-- CREATE TABLE IF NOT EXISTS "site_account" (
-- 	"memba_id" INTEGER NOT NULL,
-- 	"user_id" VARCHAR(36) NOT NULL, -- uuid
-- 	"site_id" VARCHAR(36) NOT NULL, -- uuid, basically plugin id
-- 	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
-- 	"updated" DATETIME DEFAULT CURRENT_TIMESTAMP,
-- 	"json" TEXT NOT NULL,
-- 	PRIMARY KEY ("user_id", "site_id"),
-- 	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id") ON DELETE CASCADE
-- );

-- CREATE TABLE IF NOT EXISTS "site_data" (
-- 	"id" INTEGER PRIMARY KEY AUTOINCREMENT,
-- 	"memba_id" INTEGER NOT NULL,
-- 	"user_id" VARCHAR(36) NOT NULL, -- uuid
-- 	"site_id" VARCHAR(36) NOT NULL, -- uuid
-- 	"schedule_id" VARCHAR(36), -- uuid
-- 	"created" DATETIME DEFAULT CURRENT_TIMESTAMP,
-- 	"updated" DATETIME DEFAULT CURRENT_TIMESTAMP,
-- 	"json" TEXT NOT NULL, -- Used to track what link downloaded/uploaded so far
-- 	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id") ON DELETE CASCADE,
-- 	FOREIGN KEY ("user_id", "site_id") REFERENCES "site_account"("user_id", "site_id") ON DELETE CASCADE -- uuid
-- );