from flask import Flask, jsonify, request
from dateutil.parser import isoparse
from datetime import date, timedelta

from config import (
    API_TOKEN,
    GOOGLE_SHEET_ID,
    GOOGLE_CREDS_PATH,
    GOOGLE_WORKSHEET_NAME,
)

from services.nbu_client import fetch_nbu_exchange_rates
from services.gsheets_client import (
    open_google_worksheet,
    ensure_header_exists,
    upsert_exchange_rates_row,
)

app = Flask(__name__)


@app.get("/health")
def health_check():
    return jsonify({"ok": True})


@app.post("/rates/update")
def update_exchange_rates_for_date():
    token = request.headers.get("X-API-Token")
    if token != API_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    date_param = request.args.get("date")
    if not date_param:
        return jsonify({"error": "Missing required param: date (yyyy-mm-dd)"}), 400

    try:
        target_date = isoparse(date_param).date()
    except Exception:
        return jsonify({"error": "Invalid date format. Use yyyy-mm-dd"}), 400

    rates = fetch_nbu_exchange_rates(target_date)
    usd = rates.get("USD")
    eur = rates.get("EUR")

    if usd is None or eur is None:
        return jsonify({"error": "NBU response missing USD/EUR"}), 502

    spreadsheet, worksheet = open_google_worksheet(
        GOOGLE_SHEET_ID,
        GOOGLE_CREDS_PATH,
        GOOGLE_WORKSHEET_NAME,
    )

    ensure_header_exists(worksheet)

    result = upsert_exchange_rates_row(
        worksheet,
        target_date.isoformat(),
        usd,
        eur,
    )

    return jsonify({
        "ok": True,
        "date": target_date.isoformat(),
        "USD": usd,
        "EUR": eur,
        **result,
        "sheet": spreadsheet.title,
        "worksheet": worksheet.title,
    })


@app.post("/rates/update-range")
def update_exchange_rates_range():
    token = request.headers.get("X-API-Token")
    if token != API_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    today = date.today()
    update_from = request.args.get("update_from", today.isoformat())
    update_to = request.args.get("update_to", today.isoformat())

    try:
        date_from = isoparse(update_from).date()
        date_to = isoparse(update_to).date()
    except Exception:
        return jsonify({"error": "Invalid date format. Use yyyy-mm-dd"}), 400

    if date_from > date_to:
        return jsonify({"error": "update_from must be <= update_to"}), 400

    spreadsheet, worksheet = open_google_worksheet(
        GOOGLE_SHEET_ID,
        GOOGLE_CREDS_PATH,
        GOOGLE_WORKSHEET_NAME,
    )

    ensure_header_exists(worksheet)

    results = []
    current_date = date_from

    while current_date <= date_to:
        rates = fetch_nbu_exchange_rates(current_date)
        usd = rates.get("USD")
        eur = rates.get("EUR")

        if usd is None or eur is None:
            results.append({
                "date": current_date.isoformat(),
                "error": "missing USD/EUR",
            })
        else:
            info = upsert_exchange_rates_row(
                worksheet,
                current_date.isoformat(),
                usd,
                eur,
            )
            results.append({
                "date": current_date.isoformat(),
                "USD": usd,
                "EUR": eur,
                **info,
            })

        current_date += timedelta(days=1)

    return jsonify({
        "ok": True,
        "from": date_from.isoformat(),
        "to": date_to.isoformat(),
        "count": len(results),
        "results": results,
        "sheet": spreadsheet.title,
        "worksheet": worksheet.title,
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
