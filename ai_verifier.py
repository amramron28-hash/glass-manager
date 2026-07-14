import os
import json
import requests
from core.logger import get_logger

log = get_logger("ai_verifier")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)


def verify_phone_specs(model_name):
    """
    يسأل Gemini عن المواصفات الحقيقية لهاتف معيّن.

    يُرجع:
        dict مثل {"size": 6.5, "panel": "Notch Screen", "sensor": "hardware"}
        أو None عند عدم الثقة/الفشل.
    """

    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY غير موجود في متغيرات البيئة")
        return None

    prompt = (
        "What is the exact screen size in inches (one decimal, e.g. 6.5), "
        "the display notch type (Notch or Punch-Hole), and whether the "
        "proximity sensor is a real hardware sensor or a virtual/software "
        f'one, for the phone model "{model_name}"? '
        "Reply ONLY with strict JSON, no explanation, in this exact format: "
        '{"size": 6.5, "panel": "Notch Screen", "sensor": "hardware"} '
        'or {"size": 6.5, "panel": "Punch-Hole Screen", "sensor": "virtual"}. '
        "If you are not confident about this specific model, reply with: "
        '{"size": null, "panel": null, "sensor": null}'
    )

    try:

        response = requests.post(

            f"{GEMINI_URL}?key={GEMINI_API_KEY}",

            json={
                "contents": [
                    {"parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "temperature": 0,
                    "response_mime_type": "application/json",
                },
            },

            timeout=25,

        )

        response.raise_for_status()

        data = response.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]

        parsed = json.loads(text)

        if not parsed.get("size"):
            return None

        return {
            "size": parsed.get("size"),
            "panel": parsed.get("panel") or "",
            "sensor": parsed.get("sensor") or "",
        }

    except Exception as e:

        log.error(f"AI verify error for '{model_name}': {e}")
        return None
