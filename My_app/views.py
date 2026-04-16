import requests
from datetime import datetime, timezone
from django.http import JsonResponse


def classify_name(request):
    print("🔥 VIEW HIT", request.GET)

    name = request.GET.get("name")

    if not name or name.strip() == "":
        return JsonResponse(
            {"status": "error", "message": "Missing or empty name parameter"},
            status=400
        )

    name = name.strip().lower()

    try:
        r = requests.get("https://api.genderize.io", params={"name": name}, timeout=5)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print("API ERROR:", e)
        return JsonResponse(
            {"status": "error", "message": "Upstream service failure"},
            status=502
        )

    gender = data.get("gender")
    probability = data.get("probability")
    count = data.get("count")

    if gender is None or count == 0:
        return JsonResponse(
            {"status": "error", "message": "No prediction available for the provided name"},
            status=200
        )

    probability = float(probability)
    sample_size = int(count)

    is_confident = probability >= 0.7 and sample_size >= 100

    processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

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
    
    