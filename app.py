from flask import Flask, jsonify, request
from dateutil.parser import isoparse

from config import (
    API_TOKEN,
    GOOGLE_SHEET_ID,
    GOOGLE_CREDS_PATH,
    GOOGLE_WORKSHEET_NAME,
)
from services.nbu_client import fetch_nbu_exchange_rates
from services.gsheets_client import (
    open_google_worksheet,
    write_exchange_rates_header,
    append_exchange_rates_row,
)

app = Flask(__name__)


@app.get("/health")
def health_check():
    return jsonify({"ok": True})


@app.post("/rates/update")
def update_exchange_rates_for_date():
    request_token = request.headers.get("X-API-Token")
    if request_token != API_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    date_param = request.args.get("date")
    if not date_param:
        return jsonify({"error": "Missing required param: date (yyyy-mm-dd)"}), 400

    try:
        target_date = isoparse(date_param).date()
    except Exception:
        return jsonify({"error": "Invalid date format. Use yyyy-mm-dd"}), 400

    exchange_rates = fetch_nbu_exchange_rates(target_date)

    usd_rate = exchange_rates.get("USD")
    eur_rate = exchange_rates.get("EUR")
    if usd_rate is None or eur_rate is None:
        return jsonify({"error": "NBU response missing USD/EUR"}), 502

    spreadsheet, worksheet = open_google_worksheet(
        GOOGLE_SHEET_ID,
        GOOGLE_CREDS_PATH,
        GOOGLE_WORKSHEET_NAME,
    )

    write_exchange_rates_header(worksheet)
    append_exchange_rates_row(
        worksheet,
        target_date.isoformat(),
        usd_rate,
        eur_rate,
    )

    return jsonify({
        "ok": True,
        "date": target_date.isoformat(),
        "USD": usd_rate,
        "EUR": eur_rate,
        "sheet": spreadsheet.title,
        "worksheet": worksheet.title,
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
