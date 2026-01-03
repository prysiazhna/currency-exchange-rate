import gspread

SHEET_ID = "1Y2arrQ-c-8lcWLX3873g-3MRxkztCtZJLsxc5DJnULY"
CREDS_PATH = "service-account.json"

gc = gspread.service_account(filename=CREDS_PATH)
sh = gc.open_by_key(SHEET_ID)

print("OK. Spreadsheet title:", sh.title)
print("Worksheets:", [ws.title for ws in sh.worksheets()])
