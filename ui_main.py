# ==========================================================
    # HEAD (تمت إضافة الشرطة المائلة للمسارات لضمان توافق Hugging Face)
    # ==========================================================

    ui.tags.head(

        ui.tags.meta(charset="utf-8"),

        ui.tags.meta(
            name="viewport",
            content="width=device-width, initial-scale=1"
        ),

        ui.tags.link(
            rel="stylesheet",
            href="/style_v2.css?v=7"
        ),

        ui.tags.link(
            rel="manifest",
            href="/manifest.json"
        ),

        # إضافة الشرطة المائلة لإجبار المتصفح على الوصول للمسار الصحيح للصورة على سيرفر Hugging Face مباشرة
        ui.tags.link(
            rel="icon",
            type="image/png",
            href="/AMMAR.png"
        ),

        ui.tags.link(
            rel="shortcut icon",
            type="image/png",
            href="/AMMAR.png"
        ),

        ui.tags.link(
            rel="apple-touch-icon",
            href="/AMMAR.png"
        ),

        ui.HTML("""
<script>
if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker
            .register("/service-worker.js")
            .catch(console.error);
    });
}
</script>
"""),

    ),
