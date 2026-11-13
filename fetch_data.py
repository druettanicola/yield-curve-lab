"""Tappa 1: scarica la curva dei rendimenti dei titoli di stato USA (US Treasury).

I dati sono pubblici e gratuiti: il Tesoro americano pubblica ogni giorno
quanto rende un titolo di stato a 1 mese, 3 mesi, ..., 30 anni.
"""
import io

import pandas as pd
import requests

URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "daily-treasury-rates.csv/{year}/all"
    "?type={kind}&field_tdr_date_value={year}&page&_format=csv"
)
# Due curve pubblicate dal Tesoro: quella nominale e quella "reale" (titoli TIPS, protetti dall'inflazione)
KINDS = {"nominal": "daily_treasury_yield_curve", "real": "daily_treasury_real_yield_curve"}

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"


def fetch_year(year: int, kind: str = "nominal") -> pd.DataFrame:
    """Scarica un anno di dati e li restituisce come tabella (DataFrame)."""
    response = requests.get(URL.format(year=year, kind=KINDS[kind]), timeout=60)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df["Date"] = pd.to_datetime(df["Date"])
    return df.sort_values("Date").reset_index(drop=True)


def fetch_fred(series: str) -> pd.DataFrame:
    """Serie macro dalla banca dati FRED (Federal Reserve Bank of St. Louis): colonne date, value."""
    response = requests.get(FRED_URL.format(series=series), timeout=60)
    response.raise_for_status()
    df = pd.read_csv(io.StringIO(response.text))
    df.columns = ["date", "value"]
    df["value"] = pd.to_numeric(df["value"], errors="coerce")  # FRED usa "." per i valori mancanti
    return df.dropna().reset_index(drop=True)


if __name__ == "__main__":
    df = fetch_year(2025)
    print(df.tail(3).to_string())
    print(f"\nRighe scaricate: {len(df)}")
