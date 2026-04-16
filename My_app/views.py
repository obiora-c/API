from django.shortcuts import render

# Create your views here.
import requests 
from datetime import datetime, timezone
from django.http import JsonResponse


def classify_name(request):
    name = request.GET.get("name")

    # -------------------------
    # ERROR: missing name
    # -------------------------
    if name is None or name.strip() == "":
        return JsonResponse(
            {"status": "error", "message": "Missing or empty name parameter"},
            status=400
        )

    # -------------------------
    # ERROR: invalid type
    # -------------------------
    if not isinstance(name, str):
        return JsonResponse(
            {"status": "error", "message": "name must be a string"},
            status=422
        )

    # -------------------------
    # Call Genderize API
    # -------------------------
    try:
        response = requests.get(
            "https://api.genderize.io",
            params={"name": name},
            timeout=3
        )
    except requests.RequestException:
        return JsonResponse(
            {"status": "error", "message": "Upstream service failure"},
            status=502
        )

    if response.status_code != 200:
        return JsonResponse(
            {"status": "error", "message": "External API error"},
            status=502
        )

    data = response.json()

    gender = data.get("gender")
    probability = data.get("probability")
    count = data.get("count")

    # -------------------------
    # EDGE CASE: no prediction
    # -------------------------
    if gender is None or count == 0:
        return JsonResponse(
            {"status": "error", "message": "No prediction available for the provided name"},
            status=200
        )

    # -------------------------
    # Processing rules
    # -------------------------
    sample_size = count
    probability = float(probability or 0)

    is_confident = probability >= 0.7 and sample_size >= 100

    processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # -------------------------
    # SUCCESS RESPONSE
    # -------------------------
    return JsonResponse({
        "status": "success",
        "data": {
            "name": name.lower(),
            "gender": gender,
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": is_confident,
            "processed_at": processed_at
        }
    })