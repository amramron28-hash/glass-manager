hereimport os
import json
import time
import asyncio
import traceback
import hashlib
from datetime import datetime
from database import load_db

# إعدادات المسارات
BACKUP_FILE = os.path.join("www", "models_db.json")
MODELS_INDEX_FILE = "models_index.txt"
LOG_FILE = "silent_monitor.log"

STATUS_ONLINE = "ONLINE"
STATUS_FALLBACK = "FALLBACK"
STATUS_OFFLINE = "OFFLINE"

CACHE_SECONDS = 60

class SilentMonitor:
    def __init__(self):
        self.status = STATUS_OFFLINE
        self.last_sync = None
        self.last_error = ""
        self.source = "NONE"
        self.db = {}
        self.last_refresh_time = 0
        self.stats = {"phones": 0, "sizes": 0, "panels": 0, "sensors": 0, "duplicates": 0, "empty_groups": 0}

    def log(self, message):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{now}] {message}"
        print(line)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception: pass

    def save_backup(self):
        try:
            os.makedirs("www", exist_ok=True)
            with open(BACKUP_FILE, "w", encoding="utf-8") as f:
                json.dump(self.db, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            traceback.print_exc()
            self.log(f"BACKUP_SAVE_ERROR : {type(e).__name__}: {e}")
            return False

    def build_models_index(self):
        try:
            models = set()
            for panel_dict in self.db.values():
                if not isinstance(panel_dict, dict): continue
                for sensor_dict in panel_dict.values():
                    if not isinstance(sensor_dict, dict): continue
                    for data in sensor_dict.values():
                        if not isinstance(data, dict): continue
                        for model in data.get("models", []):
                            if isinstance(model, str) and model.strip():
                                models.add(model.strip())
            models = sorted(models)
            with open(MODELS_INDEX_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(models))
            self.log(f"MODELS_INDEX_UPDATED : {len(models)} models")
        except Exception as e:
            traceback.print_exc()
            self.log(f"MODELS_INDEX_ERROR : {type(e).__name__}: {e}")

    def load_backup(self):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                self.db = json.load(f)
            self.source = "LOCAL_BACKUP"
            self.status = STATUS_FALLBACK
            self.log("Silent Monitor loaded backup database")
            return True
        except Exception as e:
            self.last_error = str(e)
            self.log(f"BACKUP_LOAD_ERROR : {type(e).__name__}: {e}")
            return False

    def load_from_supabase(self):
        try:
            db = load_db()
            if not isinstance(db, dict) or not db: raise Exception("Invalid database")
            self.db = db
            self.source = "SUPABASE"
            self.status = STATUS_ONLINE
            self.last_sync = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_error = ""
            self.save_backup()
            self.build_models_index()
            self.log("Silent Monitor connected to Supabase")
            return True
        except Exception as e:
            self.last_error = str(e)
            self.log(f"SUPABASE_ERROR : {type(e).__name__}: {e}")
            return False

    def synchronize(self):
        now = time.time()
        if self.db and (now - self.last_refresh_time) < CACHE_SECONDS:
            return self.db
        if self.load_from_supabase():
            self.last_refresh_time = now
            return self.db
        if self.load_backup():
            self.last_refresh_time = now
            return self.db
        self.status = STATUS_OFFLINE
        self.source = "NONE"
        self.db = {}
        return {}

    def count_statistics(self):
        phones, sizes, panels, sensors = 0, 0, set(), set()
        duplicates, empty_groups = 0, 0
        for panel_dict in self.db.values():
            if not isinstance(panel_dict, dict): continue
            sizes += 1
            has_models = False
            for panel_name, sensor_dict in panel_dict.items():
                panels.add(panel_name)
                if not isinstance(sensor_dict, dict): continue
                for sensor_name, data in sensor_dict.items():
                    sensors.add(sensor_name)
                    if not isinstance(data, dict): continue
                    models = data.get("models", [])
                    phones += len(models)
                    if len(models) != len(set(models)): duplicates += 1
                    if models: has_models = True
            if not has_models: empty_groups += 1
        self.stats = {"phones": phones, "sizes": sizes, "panels": len(panels), "sensors": len(sensors), "duplicates": duplicates, "empty_groups": empty_groups}
        return self.stats

    def check_required_files(self):
        report = {f: os.path.isfile(f) for f in [BACKUP_FILE, MODELS_INDEX_FILE, os.path.join("www", "service-worker.js"), os.path.join("www", "manifest.json")]}
        return report

    def health_report(self):
        return {"status": self.status, "source": self.source, "last_sync": self.last_sync, "last_error": self.last_error, "statistics": self.stats, "files": self.check_required_files()}

    def monitor(self):
        self.synchronize()
        self.count_statistics()
        return self.health_report()

watcher = SilentMonitor()

# --- الدوال المطلوبة للربط ---
def get_database(): return watcher.synchronize()
def get_status(): return watcher.health_report()
def refresh(): return watcher.monitor()
def monitor(): return watcher.monitor()
def get_statistics(): return watcher.count_statistics()

# دالة get_db_hash الجديدة والمطلوبة لـ server.py
def get_db_hash():
    """حساب هاش لقاعدة البيانات للتحقق من تغيرها"""
    db = get_database() or {}
    db_str = json.dumps(db, sort_keys=True)
    return hashlib.md5(db_str.encode()).hexdigest()


# ==========================================================
# نسخ ASYNC آمنة — لا تحظر حلقة الأحداث المشتركة (event loop)
# ==========================================================
# ⚠️ مهم: get_database() و monitor() يقومان أحياناً باستدعاء
# Supabase عبر HTTP بشكل متزامن (blocking). استدعاؤهما مباشرة
# داخل دالة async في Shiny يُجمّد حلقة الأحداث المشتركة بين كل
# الجلسات المتصلة في نفس اللحظة. الحل: تشغيلهما في خيط منفصل
# عبر asyncio.to_thread حتى لا يتأثر أي مستخدم آخر بالانتظار.

async def get_database_async():
    return await asyncio.to_thread(get_database)

async def monitor_async():
    return await asyncio.to_thread(monitor)
