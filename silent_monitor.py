import os
import json
import time
import shutil
import urllib.request
import urllib.error
from datetime import datetime

from database import load_db


BACKUP_FILE = os.path.join("www", "models_db.json")
LOG_FILE = "silent_monitor.log"

STATUS_ONLINE = "ONLINE"
STATUS_FALLBACK = "FALLBACK"
STATUS_OFFLINE = "OFFLINE"


class GlassWatcher:

    def __init__(self):

        self.status = STATUS_OFFLINE
        self.last_sync = None
        self.last_error = ""
        self.source = "NONE"

        self.db = {}

        self.stats = {
            "phones": 0,
            "sizes": 0,
            "panels": 0,
            "sensors": 0,
            "duplicates": 0,
            "empty_groups": 0
        }

    def log(self, message):

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        line = f"[{now}] {message}"

        print(line)

        try:

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")

        except Exception:
            pass

    def save_backup(self):

        try:

            os.makedirs("www", exist_ok=True)

            with open(BACKUP_FILE, "w", encoding="utf-8") as f:

                json.dump(
                    self.db,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            return True

        except Exception as e:

            self.log(f"BACKUP_SAVE_ERROR : {e}")

            return False

    def load_backup(self):

        try:

            with open(BACKUP_FILE, "r", encoding="utf-8") as f:

                self.db = json.load(f)

            self.source = "LOCAL_BACKUP"

            self.status = STATUS_FALLBACK

            self.log("Loaded backup database")

            return True

        except Exception as e:

            self.last_error = str(e)

            self.log(f"BACKUP_LOAD_ERROR : {e}")

            return False

    def load_from_supabase(self):

        try:

            db = load_db()

            if not isinstance(db, dict):
                raise Exception("Database is not dictionary")

            if len(db) == 0:
                raise Exception("Database is empty")

            self.db = db

            self.source = "SUPABASE"

            self.status = STATUS_ONLINE

            self.last_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.last_error = ""

            self.save_backup()

            self.log("Connected to Supabase")

            return True

        except Exception as e:

            self.last_error = str(e)

            self.log(f"SUPABASE_ERROR : {e}")

            return False


    def synchronize(self):

        if self.load_from_supabase():

            return self.db

        self.log("Switching to backup database")

        if self.load_backup():

            return self.db

        self.status = STATUS_OFFLINE

        self.source = "NONE"

        self.db = {}

        return {}


    def count_statistics(self):

        phones = 0
        sizes = 0
        panels = set()
        sensors = set()
        duplicates = 0
        empty_groups = 0

        for size, panel_dict in self.db.items():

            sizes += 1

            has_models = False

            for panel, sensor_dict in panel_dict.items():

                panels.add(panel)

                for sensor, data in sensor_dict.items():

                    sensors.add(sensor)

                    models = data.get("models", [])

                    phones += len(models)

                    if len(models) != len(set(models)):
                        duplicates += 1

                    if models:
                        has_models = True

            if not has_models:
                empty_groups += 1

        self.stats = {

            "phones": phones,

            "sizes": sizes,

            "panels": len(panels),

            "sensors": len(sensors),

            "duplicates": duplicates,

            "empty_groups": empty_groups

        }

        return self.stats
    def check_required_files(self):

        report = {}

        files = [

            BACKUP_FILE,

            os.path.join("www", "service-worker.js"),

            os.path.join("www", "manifest.json")

        ]

        for file in files:

            report[file] = os.path.isfile(file)

            if not report[file]:

                self.log(f"MISSING_FILE : {file}")

        return report


    def health_report(self):

        return {

            "status": self.status,

            "source": self.source,

            "last_sync": self.last_sync,

            "last_error": self.last_error,

            "statistics": self.stats,

            "files": self.check_required_files()

        }


    def monitor(self):

        self.synchronize()

        self.count_statistics()

        return self.health_report()


watcher = GlassWatcher()


def get_database():

    return watcher.synchronize()


def get_status():

    return watcher.health_report()


def refresh():

    return watcher.monitor()


def get_statistics():

    return watcher.count_statistics()


def is_online():

    return watcher.status == STATUS_ONLINE


def is_fallback():

    return watcher.status == STATUS_FALLBACK


def is_offline():

    return watcher.status == STATUS_OFFLINE
    def load_from_supabase(self):

        try:

            db = load_db()

            if not isinstance(db, dict):
                raise Exception("Database is not dictionary")

            if len(db) == 0:
                raise Exception("Database is empty")

            self.db = db

            self.source = "SUPABASE"
            self.status = STATUS_ONLINE
            self.last_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_error = ""

            self.save_backup()

            self.log("Silent Monitor connected to Supabase")

            return True

        except Exception as e:

            self.last_error = str(e)

            self.log(f"SUPABASE_ERROR : {e}")

            return False


    def synchronize(self):

        if self.load_from_supabase():

            return self.db

        self.log("Silent Monitor switched to backup database")

        if self.load_backup():

            return self.db

        self.status = STATUS_OFFLINE
        self.source = "NONE"
        self.db = {}

        return {}


    def count_statistics(self):

        phones = 0
        sizes = 0
        panels = set()
        sensors = set()
        duplicates = 0
        empty_groups = 0

        for size, panel_dict in self.db.items():

            sizes += 1

            has_models = False

            for panel, sensor_dict in panel_dict.items():

                panels.add(panel)

                for sensor, data in sensor_dict.items():

                    sensors.add(sensor)

                    models = data.get("models", [])

                    phones += len(models)

                    if len(models) != len(set(models)):
                        duplicates += 1

                    if models:
                        has_models = True

            if not has_models:
                empty_groups += 1

        self.stats = {

            "phones": phones,
            "sizes": sizes,
            "panels": len(panels),
            "sensors": len(sensors),
            "duplicates": duplicates,
            "empty_groups": empty_groups

        }

        return self.stats

