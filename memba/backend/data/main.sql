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
	"json" TEXT NOT NULL,
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
	"json" TEXT NOT NULL, -- Used to track what link downloaded/uploaded so far
	FOREIGN KEY ("memba_id") REFERENCES "memba_account"("id") ON DELETE CASCADE,
	FOREIGN KEY ("user_id", "site_id") REFERENCES "site_account"("user_id", "site_id") ON DELETE CASCADE -- uuid
);