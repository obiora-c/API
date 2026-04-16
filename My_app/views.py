import requests
from datetime import datetime, timezone
from django.http import JsonResponse


def classify_name(request):
    # -------------------------
    # GET PARAM
    # -------------------------
    name = request.GET.get("name")

    # -------------------------
    # ERROR: missing or empty
    # -------------------------
    if name is None or name.strip() == "":
        return JsonResponse(
            {"status": "error", "message": "Missing or empty name parameter"},
            status=400
        )

    # -------------------------
    # VALIDATION: must be string
    # -------------------------
    if not isinstance(name, str):
        return JsonResponse(
            {"status": "error", "message": "name must be a string"},
            status=422
        )

    name = name.strip().lower()

    # -------------------------
    # CALL EXTERNAL API
    # -------------------------
    try:
        res = requests.get(
            "https://api.genderize.io",
            params={"name": name},
            timeout=5
        )
        res.raise_for_status()
    except requests.RequestException:
        return JsonResponse(
            {"status": "error", "message": "Upstream service failure"},
            status=502
        )

    data = res.json()

    gender = data.get("gender")
    probability = data.get("probability")
    count = data.get("count")

    # -------------------------
    # EDGE CASE
    # -------------------------
    if gender is None or count == 0:
        return JsonResponse(
            {"status": "error", "message": "No prediction available for the provided name"},
            status=200
        )

    # -------------------------
    # PROCESSING
    # -------------------------
    probability = float(probability)
    sample_size = int(count)

    is_confident = probability >= 0.7 and sample_size >= 100

    processed_at = (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )

    # -------------------------
    # SUCCESS RESPONSE
    # -------------------------
    return JsonResponse({
        "status": "success",
        "data": {
            "name": name,
            "gender": gender,
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": is_confident,
            "processed_at": processed_at
        }
    })