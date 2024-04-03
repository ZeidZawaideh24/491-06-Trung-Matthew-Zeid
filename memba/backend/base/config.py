import argparse

CONFIG = argparse.ArgumentParser()

CONFIG.add_argument("--data-path", help="Path to data db", default="data/memba.db")
CONFIG.add_argument("--schedule-path", help="Path to schedule db", default="data/schedule.db")

CONFIG.add_argument("--plugin-path", help="Path to plugin", action="append", default=["memba/backend/plugin/site"])

CONFIG.add_argument("--server", help="Run as server", action="store_true")

CONFIG = CONFIG.parse_args()