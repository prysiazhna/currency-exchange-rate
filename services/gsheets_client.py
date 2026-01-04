import gspread
from gspread import Spreadsheet, Worksheet


def open_google_worksheet(
    spreadsheet_id: str,
    credentials_path: str,
    worksheet_name: str
) -> tuple[Spreadsheet, Worksheet]:
    google_client = gspread.service_account(filename=credentials_path)
    spreadsheet = google_client.open_by_key(spreadsheet_id)
    worksheet = spreadsheet.worksheet(worksheet_name)
    return spreadsheet, worksheet


def write_exchange_rates_header(worksheet: Worksheet):
    worksheet.update("A1:C1", [["date", "USD", "EUR"]])


def append_exchange_rates_row(
    worksheet: Worksheet,
    rate_date_iso: str,
    usd_rate: float,
    eur_rate: float
):
    worksheet.append_row([rate_date_iso, usd_rate, eur_rate])
