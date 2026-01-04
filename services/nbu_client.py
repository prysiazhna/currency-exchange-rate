import requests
from datetime import date

NBU_EXCHANGE_API_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"


def fetch_nbu_exchange_rates(target_date: date) -> dict[str, float]:
    formatted_date = target_date.strftime("%Y%m%d")

    response = requests.get(
        NBU_EXCHANGE_API_URL,
        params={"date": formatted_date, "json": ""},
        timeout=20,
    )
    response.raise_for_status()

    raw_rates = response.json()

    exchange_rates: dict[str, float] = {}
    for rate_row in raw_rates:
        currency_code = rate_row.get("cc")
        currency_rate = rate_row.get("rate")

        if currency_code and currency_rate is not None:
            exchange_rates[currency_code] = float(currency_rate)

    return exchange_rates
