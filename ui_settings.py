from shiny import ui

print("USING ui_settings.py:", __file__)

# ==========================================================
# SETTINGS DRAWER
# ==========================================================

def draw_settings_drawer():

    return ui.div(

        ui.div(

            ui.div(

                ui.span("⚙️", class_="drawer-icon"),

                ui.span("الإعدادات", class_="drawer-title"),

                class_="drawer-title-row",

            ),

            ui.tags.button(

                "✕",

                id="btn_close_drawer_trigger",

                class_="drawer-close-btn",

                title="إغلاق",

            ),

            class_="drawer-header",

        ),

        ui.div(

            ui.output_ui("system_info_area"),

            ui.output_ui("database_status_area"),

            ui.output_ui("monitor_area"),

            ui.output_ui("notification_area"),

            ui.output_ui("duplicate_issues_area"),

            ui.output_ui("silent_inspector_area"),

            class_="drawer-body",

        ),

        id="settings-drawer",

        class_="drawer",

    )


# ==========================================================
# SYSTEM INFO
# ==========================================================

def draw_system_info():

    return ui.div(

        ui.h4("معلومات النظام"),

        ui.div("ZEGAAR AMMAR GLASS MANAGER"),

        ui.div("Version 2026.07"),

        class_="metric-box glass-card",

    )


# ==========================================================
# DATABASE STATUS
# ==========================================================

def draw_database_status(count):

    return ui.div(

        ui.h4("عدد الهواتف"),

        ui.div(str(count), class_="metric-value"),

        class_="metric-box glass-card",

    )


# ==========================================================
# MONITOR
# ==========================================================

def draw_monitor_component(status):

    online = str(status).upper() == "ONLINE"

    return ui.div(

        ui.h4("المراقب الصامت"),

        ui.div(

            "🟢 ONLINE" if online else "🔴 OFFLINE",

            class_="metric-value",

        ),

        class_="metric-box glass-card",

    )


# ==========================================================
# NOTIFICATIONS
# ==========================================================

def draw_notification_component(count=0):

    return ui.div(

        ui.h4("الإشعارات"),

        ui.div(

            f"🔔 {count}",

            class_="metric-value",

        ),

        class_="metric-box glass-card",

    )


# ==========================================================
# SILENT INSPECTOR
# ==========================================================

def draw_silent_inspector():

    return ui.div(

        ui.input_action_button(

            "btn_run_inspector",

            "🛠 تشغيل الفحص الذكي",

            class_="btn-neon",

        ),

        class_="glass-card",

    )


# ==========================================================
# DUPLICATE ISSUES (المراقب الصامت - عيني ويدي)
# ==========================================================

def draw_duplicate_issues(issues, auto_fix_log=None):

    auto_fix_log = auto_fix_log or []

    sections = []

    if auto_fix_log:

        log_rows = []

        for entry in reversed(auto_fix_log):

            log_rows.append(
                ui.div(
                    f"✅ تم نقل \"{entry.get('model','')}\" تلقائياً — "
                    f"حُذف من ({entry.get('removed_from','-')}) "
                    f"وبقي في ({entry.get('kept_in','-')}) — {entry.get('time','')}",
                    class_="coord-line",
                    style="font-size:13px;"
                )
            )

        sections.append(
            ui.div(

                ui.h4("📋 آخر التصحيحات التلقائية"),

                *log_rows,

                class_="metric-box glass-card",

            )
        )

    if not issues:

        sections.append(
            ui.div(

                ui.h4("🔔 الإشعارات"),

                ui.div("لا توجد مشاكل تحتاج تدخلاً يدوياً ✅"),

                class_="metric-box glass-card",

            )
        )

        return ui.TagList(*sections)

    rows = []

    for issue in issues:

        model = issue.get("model", "")
        correct = issue.get("correct", {})
        wrongs = issue.get("wrongs", [])

        rows.append(
            ui.div(
                f"📱 {model}",
                class_="phone-title",
                style="font-size:16px;margin-bottom:6px;"
            )
        )

        rows.append(
            ui.div(
                f"✅ المجموعة الصحيحة المرجّحة: {correct.get('size','-')} / "
                f"{correct.get('panel','-')} / {correct.get('sensor','-')} "
                f"({correct.get('group_size',0)} موديل)",
                class_="coord-line",
            )
        )

        for w in wrongs:

            payload = "|".join([
                str(model),
                str(w.get("size", "")),
                str(w.get("panel", "")),
                str(w.get("sensor", "")),
            ])

            rows.append(
                ui.div(

                    ui.div(
                        f"⚠️ مكرر في: {w.get('size','-')} / "
                        f"{w.get('panel','-')} / {w.get('sensor','-')}",
                        class_="coord-line",
                        style="flex:1;"
                    ),

                    ui.tags.button(
                        "🔧 حذف هذا المكرر الخاطئ",
                        class_="btn-close",
                        onclick=(
                            "Shiny.setInputValue("
                            f"'fix_duplicate', '{payload}', "
                            "{priority:'event'});"
                        ),
                        style="white-space:nowrap;font-size:13px;padding:8px 12px;"
                    ),

                    style="display:flex;align-items:center;gap:8px;margin:6px 0;"

                )
            )

    sections.append(

        ui.div(

            ui.h4(f"🔔 الإشعارات ({len(issues)})"),

            *rows,

            class_="metric-box glass-card",

        )

    )

    return ui.TagList(*sections)


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "draw_settings_drawer",

    "draw_system_info",

    "draw_database_status",

    "draw_monitor_component",

    "draw_notification_component",

    "draw_silent_inspector",

    "draw_duplicate_issues",

]
