import gspread
from flask import Flask, jsonify, request

app = Flask(__name__)

SHEET_ID = "1Y2arrQ-c-8lcWLX3873g-3MRxkztCtZJLsxc5DJnULY"
CREDS_PATH = "service-account.json"
WORKSHEET_NAME = "exchange_rate"  


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.post("/gsheets/ping")
def gsheets_ping():
    token = request.headers.get("X-API-Token")
    if token != "dev_token":
        return jsonify({"error": "Unauthorized"}), 401

    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.worksheet(WORKSHEET_NAME)

    ws.update("A1", "PING_OK")

    return jsonify({"ok": True, "sheet": sh.title, "worksheet": ws.title})
