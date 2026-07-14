import os
import json
import time
import asyncio
import traceback
import hashlib
from datetime import datetime
from database import load_db, delete_model, update_model_specs
from logic_engine import detect_cross_group_duplicates, normalize_panel
from ai_verifier import verify_phone_specs

AUTO_FIX_LOG_FILE = "auto_fix_log.json"
AI_CHECKED_FILE = "ai_checked.json"
AI_ISSUES_FILE = "ai_issues.json"
AI_BATCH_SIZE = 15

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
        self.duplicate_issues = []
        self.auto_fix_log = self._load_auto_fix_log()
        self.ai_checked = self._load_json_set(AI_CHECKED_FILE)
        self.ai_issues = self._load_json_list(AI_ISSUES_FILE)

    def _load_json_set(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()

    def _load_json_list(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_json(self, path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"AI_SAVE_ERROR({path}) : {type(e).__name__}: {e}")

    def _load_auto_fix_log(self):
        try:
            with open(AUTO_FIX_LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_auto_fix_log(self):
        try:
            # نحتفظ بآخر 200 عملية فقط لتفادي تضخم الملف
            trimmed = self.auto_fix_log[-200:]
            with open(AUTO_FIX_LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(trimmed, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"AUTO_FIX_LOG_SAVE_ERROR : {type(e).__name__}: {e}")

    def _remove_model_from_db(self, model, size, panel, sensor):
        try:
            models = self.db[size][panel][sensor]["models"]
            if model in models:
                models.remove(model)
        except Exception:
            pass

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
        try:
            raw_issues = detect_cross_group_duplicates(self.db)
            self.duplicate_issues = self._auto_fix_confident_issues(raw_issues)
        except Exception as e:
            self.log(f"DUPLICATE_DETECT_ERROR : {type(e).__name__}: {e}")
            self.duplicate_issues = []
        return self.stats

    def _classify_sensor(self, sensor_text):
        """يصنّف نص المستشعر إلى hardware أو virtual تقريبياً"""
        t = str(sensor_text or "").lower()
        if "virtual" in t or "software" in t or "camera" in t:
            return "virtual"
        return "hardware"

    def run_ai_batch_check(self, batch_size=AI_BATCH_SIZE):
        """
        يفحص دفعة من الهواتف غير المفحوصة سابقاً عبر Gemini،
        ويقارن نتيجة الذكاء الاصطناعي بما هو مخزّن في القاعدة.
        كل هاتف يُفحص مرة واحدة فقط (تُحفظ في ai_checked.json)
        لتوفير الحصة المجانية.
        """

        candidates = []

        for size, panels in self.db.items():
            if not isinstance(panels, dict):
                continue
            for panel, sensors in panels.items():
                if not isinstance(sensors, dict):
                    continue
                for sensor, data in sensors.items():
                    models = data.get("models", []) if isinstance(data, dict) else data
                    if not isinstance(models, list):
                        continue
                    for model in models:
                        key = f"{model}|{size}|{panel}|{sensor}"
                        if key in self.ai_checked:
                            continue
                        candidates.append((model, size, panel, sensor, key))

        batch = candidates[:batch_size]

        checked_now = 0
        found_now = 0

        for model, size, panel, sensor, key in batch:

            result = verify_phone_specs(model)

            self.ai_checked.add(key)
            checked_now += 1

            if not result:
                continue

            ai_size = result.get("size")
            ai_panel_norm = normalize_panel(result.get("panel", ""))
            ai_sensor_cat = self._classify_sensor(result.get("sensor", ""))

            db_panel_norm = normalize_panel(panel)
            db_sensor_cat = self._classify_sensor(sensor)

            size_mismatch = (
                ai_size is not None
                and abs(float(ai_size) - float(size)) > 0.05
            )
            panel_mismatch = (
                result.get("panel")
                and ai_panel_norm != db_panel_norm
            )
            sensor_mismatch = (ai_sensor_cat != db_sensor_cat)

            if size_mismatch or panel_mismatch or sensor_mismatch:

                self.ai_issues.append({
                    "model": model,
                    "db_size": size,
                    "db_panel": panel,
                    "db_sensor": sensor,
                    "ai_size": ai_size,
                    "ai_panel": result.get("panel"),
                    "ai_sensor": result.get("sensor"),
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })

                found_now += 1

                self.log(f"AI_ISSUE_FOUND : {model} (DB: {size}/{panel}/{sensor} <> AI: {ai_size}/{result.get('panel')}/{result.get('sensor')})")

        if checked_now:
            self._save_json(AI_CHECKED_FILE, list(self.ai_checked))
            self._save_json(AI_ISSUES_FILE, self.ai_issues[-300:])
            self.ai_issues = self.ai_issues[-300:]

        remaining = len(candidates) - checked_now

        return {
            "checked_now": checked_now,
            "found_now": found_now,
            "remaining": max(remaining, 0),
        }

    def fix_ai_issue(self, index):
        """
        يطبّق تصحيح الذكاء الاصطناعي المقترح رقم index (بعد تأكيد يدوي من المستخدم)
        """
        try:
            issue = self.ai_issues[index]
        except (IndexError, TypeError):
            return False

        model = issue["model"]

        new_size = issue.get("ai_size") or issue["db_size"]
        new_panel = issue.get("ai_panel") or issue["db_panel"]
        new_sensor_cat = self._classify_sensor(issue.get("ai_sensor", ""))

        # نحافظ على تسمية المستشعر المستخدمة فعلياً في القاعدة لنفس الفئة
        # (hardware_top_sensor أو Virtual) بدل نص Gemini الحر
        new_sensor = (
            "Virtual"
            if new_sensor_cat == "virtual"
            else "hardware_top_sensor"
        )

        ok = update_model_specs(
            model,
            issue["db_size"], issue["db_panel"], issue["db_sensor"],
            new_size, new_panel, new_sensor,
        )

        if ok:

            self._remove_model_from_db(
                model, issue["db_size"], issue["db_panel"], issue["db_sensor"]
            )

            self.db.setdefault(str(new_size), {}) \
                    .setdefault(new_panel, {}) \
                    .setdefault(new_sensor, {"models": []})

            if model not in self.db[str(new_size)][new_panel][new_sensor]["models"]:
                self.db[str(new_size)][new_panel][new_sensor]["models"].append(model)

            self.ai_issues.pop(index)
            self._save_json(AI_ISSUES_FILE, self.ai_issues)

        return ok

    def _auto_fix_confident_issues(self, raw_issues):
        """
        يصحّح تلقائياً فقط الحالات الواضحة جداً: مكرر معزول
        (موديل واحد فقط في مجموعته) مقابل مجموعة صحيحة تحتوي
        عدة موديلات. أي حالة أقل وضوحاً تبقى للتصحيح اليدوي.
        كل تصحيح تلقائي يُسجَّل في auto_fix_log.json.
        """
        remaining_issues = []

        for issue in raw_issues:

            correct = issue["correct"]
            manual_wrongs = []

            for wrong in issue["wrongs"]:

                confident = (
                    wrong["group_size"] == 1
                    and correct["group_size"] >= 2
                )

                if not confident:
                    manual_wrongs.append(wrong)
                    continue

                ok = delete_model(
                    issue["model"],
                    wrong["size"],
                    wrong["panel"],
                    wrong["sensor"],
                )

                if ok:

                    self._remove_model_from_db(
                        issue["model"],
                        wrong["size"],
                        wrong["panel"],
                        wrong["sensor"],
                    )

                    self.auto_fix_log.append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "model": issue["model"],
                        "removed_from": f'{wrong["size"]} / {wrong["panel"]} / {wrong["sensor"]}',
                        "kept_in": f'{correct["size"]} / {correct["panel"]} / {correct["sensor"]}',
                    })

                    self.log(
                        f"AUTO_FIX : {issue['model']} removed from "
                        f'{wrong["size"]}/{wrong["panel"]}/{wrong["sensor"]}'
                    )

                else:
                    # فشل الحذف الفعلي -> أرسلها للتصحيح اليدوي بدل تجاهلها
                    manual_wrongs.append(wrong)

            if manual_wrongs:
                remaining_issues.append({
                    "model": issue["model"],
                    "correct": correct,
                    "wrongs": manual_wrongs,
                })

        if self.auto_fix_log:
            self._save_auto_fix_log()

        return remaining_issues

    def check_required_files(self):
        report = {f: os.path.isfile(f) for f in [BACKUP_FILE, MODELS_INDEX_FILE, os.path.join("www", "service-worker.js"), os.path.join("www", "manifest.json")]}
        return report

    def health_report(self):
        return {"status": self.status, "source": self.source, "last_sync": self.last_sync, "last_error": self.last_error, "statistics": self.stats, "files": self.check_required_files(), "notifications": len(self.duplicate_issues), "duplicate_issues": self.duplicate_issues, "auto_fix_log": self.auto_fix_log[-10:], "ai_issues": self.ai_issues}

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
def run_ai_check(): return watcher.run_ai_batch_check()
def fix_ai_issue_index(index): return watcher.fix_ai_issue(index)

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
