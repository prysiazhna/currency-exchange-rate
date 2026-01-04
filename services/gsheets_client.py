import gspread
from gspread import Spreadsheet, Worksheet
from datetime import datetime


HEADER = ["date", "USD", "EUR", "updated_at"]


def open_google_worksheet(
    spreadsheet_id: str,
    credentials_path: str,
    worksheet_name: str,
) -> tuple[Spreadsheet, Worksheet]:
    client = gspread.service_account(filename=credentials_path)
    spreadsheet = client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)
    return spreadsheet, worksheet


def write_exchange_rates_header(worksheet: Worksheet):
    worksheet.update("A1:D1", [HEADER])


def ensure_header_exists(worksheet: Worksheet):
    current_header = worksheet.row_values(1)
    if current_header != HEADER:
        write_exchange_rates_header(worksheet)


def upsert_exchange_rates_row(
    worksheet: Worksheet,
    rate_date_iso: str,
    usd_rate: float,
    eur_rate: float,
) -> dict:
    dates_column = worksheet.col_values(1)
    updated_at = datetime.utcnow().isoformat()

    try:
        row_number = dates_column.index(rate_date_iso) + 1
        worksheet.update(
            f"A{row_number}:D{row_number}",
            [[rate_date_iso, usd_rate, eur_rate, updated_at]],
        )
        return {"action": "updated", "row": row_number}
    except ValueError:
        worksheet.append_row(
            [rate_date_iso, usd_rate, eur_rate, updated_at]
        )
        return {"action": "inserted"}
