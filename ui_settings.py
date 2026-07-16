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

            ui.output_ui("ai_issues_area"),

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

            style="margin-bottom:10px;"

        ),

        ui.input_action_button(

            "btn_sync_local_db",

            "🔄 مزامنة الملف المحلي إلى Supabase",

            class_="btn-neon",

            style="background:#3498db;color:white;"

        ),

        class_="glass-card",

    )


# ==========================================================
# DUPLICATE ISSUES (المراقب الصامت - عيني ويدي)
# ==========================================================

def draw_duplicate_issues(issues, auto_fix_log=None, expanded_key=None, read_keys=None):

    auto_fix_log = auto_fix_log or []
    read_keys = read_keys or set()

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

                ui.div(

                    *log_rows,

                    style=(
                        "max-height:220px;"
                        "overflow-y:auto;"
                        "overflow-x:hidden;"
                    ),

                ),

                class_="metric-box glass-card",

            )
        )

    def _manual_edit_panel():
        return ui.div(

            ui.h4(
                "✏️ تعديل يدوي",
                style="margin-top:16px;font-size:15px;"
            ),

            ui.p(
                "اضغط \"تعديل يدوي\" على أي هاتف في الإشعارات لملء الحقول تلقائياً، "
                "أو اكتب اسم الهاتف والقيمة المطلوب تصحيحها يدوياً ثم اضغط حفظ.",
                style="font-size:12px;color:var(--text-muted);margin-bottom:10px;"
            ),

            ui.input_text("edit_model", "اسم الهاتف بالضبط"),

            ui.input_text("edit_size", "المقاس"),

            ui.input_text("edit_panel", "نوع الشاشة"),

            ui.input_text("edit_sensor", "المستشعر"),

            ui.input_action_button(
                "save_manual_edit",
                "💾 حفظ التعديل",
                class_="btn-neon"
            ),

            id="manual-edit-panel",

            style=(
                "margin-top:14px;padding-top:14px;"
                "border-top:1px solid rgba(255,255,255,.12);"
            ),

        )

    if not issues:

        sections.append(
            ui.div(

                ui.h4("🔔 الإشعارات"),

                ui.div("لا توجد مشاكل تحتاج تدخلاً يدوياً ✅"),

                _manual_edit_panel(),

                class_="metric-box glass-card",

            )
        )

        return ui.TagList(*sections)

    unread_count = sum(
        1 for issue in issues
        if issue.get("model", "") not in read_keys
    )

    rows = []

    for issue in issues:

        model = issue.get("model", "")
        correct = issue.get("correct", {})
        wrongs = issue.get("wrongs", [])

        is_unread = model not in read_keys
        is_open = model == expanded_key

        # ------ رأس الإشعار المطوي (قابل للضغط) ------
        rows.append(

            ui.tags.button(

                ui.span(
                    "🔴" if is_unread else "",
                    style="flex-shrink:0;"
                ),

                ui.span(
                    f"📱 {model}",
                    style=(
                        "flex:1;min-width:0;overflow-wrap:break-word;"
                        "white-space:normal;text-align:right;"
                    )
                ),

                ui.span(
                    "▲" if is_open else "▼",
                    style="opacity:.6;flex-shrink:0;"
                ),

                onclick=(
                    "Shiny.setInputValue("
                    f"'open_issue', '{model}', "
                    "{priority:'event'});"
                ),

                style=(
                    "width:100%;background:"
                    + ("rgba(0,229,255,.08)" if is_unread else "transparent")
                    + ";border:none;border-bottom:1px solid rgba(255,255,255,.08);"
                    "color:#fff;padding:10px 4px;font-size:15px;"
                    "font-weight:" + ("800" if is_unread else "500") + ";"
                    "cursor:pointer;display:flex;align-items:center;gap:6px;"
                ),

            )
        )

        if not is_open:
            continue

        # ------ التفاصيل (تظهر فقط عند الفتح) ------

        correct_payload = "|".join([
            str(model),
            str(correct.get("size", "")),
            str(correct.get("panel", "")),
            str(correct.get("sensor", "")),
        ])

        rows.append(
            ui.div(

                ui.div(
                    f"✅ المجموعة الصحيحة المرجّحة (تخمين إحصائي وليس مؤكداً): "
                    f"{correct.get('size','-')} / "
                    f"{correct.get('panel','-')} / {correct.get('sensor','-')} "
                    f"({correct.get('group_size',0)} موديل)",
                    style=(
                        "width:100%;display:block;"
                        "white-space:normal;overflow-wrap:break-word;"
                        "font-size:14px;color:var(--text-muted);"
                        "line-height:1.6;margin-bottom:8px;"
                    )
                ),

                ui.div(

                    ui.tags.button(
                        "🔧 هذا خطأ أيضاً - احذفه من هنا",
                        class_="btn-close",
                        onclick=(
                            "Shiny.setInputValue("
                            f"'fix_duplicate', '{correct_payload}', "
                            "{priority:'event'});"
                        ),
                        style="font-size:12px;padding:6px 10px;opacity:.85;flex:1;"
                    ),

                    ui.tags.button(
                        "✏️ تعديل يدوي",
                        onclick=(
                            f"document.getElementById('edit_model').value='{model}';"
                                f"document.getElementById('edit_size').value='{correct.get('size','')}';"
                            f"document.getElementById('edit_panel').value='{correct.get('panel','')}';"
                            f"document.getElementById('edit_sensor').value='{correct.get('sensor','')}';"
                            "document.getElementById('edit_model').dispatchEvent(new Event('input',{bubbles:true}));document.getElementById('edit_size').dispatchEvent(new Event('input',{bubbles:true}));"
                            "document.getElementById('edit_panel').dispatchEvent(new Event('input',{bubbles:true}));"
                            "document.getElementById('edit_sensor').dispatchEvent(new Event('input',{bubbles:true}));"
                            "Shiny.setInputValue("
                            f"'edit_target', '{correct_payload}', "
                            "{priority:'event'});"
                            "document.getElementById('manual-edit-panel')?.scrollIntoView({behavior:'smooth'});"
                        ),
                        style=(
                            "font-size:12px;padding:6px 10px;flex:1;"
                            "background:rgba(0,229,255,.15);color:#00e5ff;"
                            "border:1px solid rgba(0,229,255,.4);border-radius:14px;"
                        )
                    ),

                    style="display:flex;gap:8px;"

                ),

                style="margin:6px 0;padding-right:14px;"

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
                        style=(
                            "width:100%;display:block;"
                            "white-space:normal;overflow-wrap:break-word;"
                            "font-size:14px;color:var(--text-muted);"
                            "line-height:1.6;margin-bottom:8px;"
                        )
                    ),

                    ui.div(

                        ui.tags.button(
                            "🔧 حذف هذا المكرر الخاطئ",
                            class_="btn-close",
                            onclick=(
                                "Shiny.setInputValue("
                                f"'fix_duplicate', '{payload}', "
                                "{priority:'event'});"
                            ),
                            style="font-size:13px;padding:8px 12px;flex:1;"
                        ),

                        ui.tags.button(
                            "✏️ تعديل يدوي",
                            onclick=(
                                f"document.getElementById('edit_model').value='{model}';"
                                f"document.getElementById('edit_size').value='{w.get('size','')}';"
                                f"document.getElementById('edit_panel').value='{w.get('panel','')}';"
                                f"document.getElementById('edit_sensor').value='{w.get('sensor','')}';"
                                "document.getElementById('edit_model').dispatchEvent(new Event('input',{bubbles:true}));document.getElementById('edit_size').dispatchEvent(new Event('input',{bubbles:true}));"
                                "document.getElementById('edit_panel').dispatchEvent(new Event('input',{bubbles:true}));"
                                "document.getElementById('edit_sensor').dispatchEvent(new Event('input',{bubbles:true}));"
                                "Shiny.setInputValue("
                                f"'edit_target', '{payload}', "
                                "{priority:'event'});"
                                "document.getElementById('manual-edit-panel')?.scrollIntoView({behavior:'smooth'});"
                            ),
                            style=(
                                "font-size:13px;padding:8px 12px;flex:1;"
                                "background:rgba(0,229,255,.15);color:#00e5ff;"
                                "border:1px solid rgba(0,229,255,.4);border-radius:14px;"
                            )
                        ),

                        style="display:flex;gap:8px;"

                    ),

                    style="margin:6px 0;padding-right:14px;"

                )
            )

    sections.append(

        ui.div(

            ui.h4(f"🔔 الإشعارات ({unread_count} غير مقروءة من {len(issues)})"),

            ui.div(

                *rows,

                style=(
                    "max-height:380px;"
                    "overflow-y:auto;"
                    "overflow-x:hidden;"
                ),

            ),

            _manual_edit_panel(),

            class_="metric-box glass-card",

        )

    )

    return ui.TagList(*sections)


# ==========================================================
# AI ISSUES (نتائج الفحص الذكي عبر Gemini)
# ==========================================================

def draw_ai_issues(ai_issues):

    ai_issues = ai_issues or []

    if not ai_issues:
        return None

    rows = []

    for i, issue in enumerate(ai_issues):

        model = issue.get("model", "")

        rows.append(

            ui.div(

                ui.div(
                    f"📱 {model}",
                    style="font-weight:800;margin-bottom:6px;"
                ),

                ui.div(
                    f"في القاعدة: {issue.get('db_size','-')} / "
                    f"{issue.get('db_panel','-')} / {issue.get('db_sensor','-')}",
                    style=(
                        "width:100%;display:block;white-space:normal;"
                        "overflow-wrap:break-word;font-size:13px;"
                        "color:var(--text-muted);margin-bottom:4px;"
                    )
                ),

                ui.div(
                    f"اقتراح الذكاء الاصطناعي: {issue.get('ai_size','-')} / "
                    f"{issue.get('ai_panel','-')} / {issue.get('ai_sensor','-')}",
                    style=(
                        "width:100%;display:block;white-space:normal;"
                        "overflow-wrap:break-word;font-size:13px;"
                        "color:#00e5ff;margin-bottom:8px;"
                    )
                ),

                ui.div(

                    ui.tags.button(
                        "✅ اعتماد اقتراح الذكاء الاصطناعي",
                        class_="btn-close",
                        onclick=(
                            "Shiny.setInputValue("
                            f"'fix_ai_issue', {i}, "
                            "{priority:'event'});"
                        ),
                        style="font-size:12px;padding:6px 10px;flex:1;"
                    ),

                    ui.tags.button(
                        "✏️ تعديل يدوي",
                        onclick=(
                            f"document.getElementById('edit_model').value='{model}';"
                            f"document.getElementById('edit_size').value='{issue.get('db_size','')}';"
                            f"document.getElementById('edit_panel').value='{issue.get('db_panel','')}';"
                            f"document.getElementById('edit_sensor').value='{issue.get('db_sensor','')}';"
                            "document.getElementById('edit_model').dispatchEvent(new Event('input',{bubbles:true}));"
                            "document.getElementById('edit_size').dispatchEvent(new Event('input',{bubbles:true}));"
                            "document.getElementById('edit_panel').dispatchEvent(new Event('input',{bubbles:true}));"
                            "document.getElementById('edit_sensor').dispatchEvent(new Event('input',{bubbles:true}));"
                            "Shiny.setInputValue("
                            f"'edit_target', '{model}|{issue.get('db_size','')}|{issue.get('db_panel','')}|{issue.get('db_sensor','')}', "
                            "{priority:'event'});"
                            "document.getElementById('manual-edit-panel')?.scrollIntoView({behavior:'smooth'});"
                        ),
                        style=(
                            "font-size:12px;padding:6px 10px;flex:1;"
                            "background:rgba(0,229,255,.15);color:#00e5ff;"
                            "border:1px solid rgba(0,229,255,.4);border-radius:14px;"
                        )
                    ),

                    style="display:flex;gap:8px;"

                ),

                style=(
                    "margin:10px 0;padding:10px 0;"
                    "border-bottom:1px solid rgba(255,255,255,.08);"
                )

            )
        )

    return ui.div(

        ui.h4(f"🤖 نتائج الفحص الذكي ({len(ai_issues)})"),

        ui.div(
            *rows,
            style="max-height:380px;overflow-y:auto;overflow-x:hidden;"
        ),

        class_="metric-box glass-card",

    )


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

    "draw_ai_issues",

]
