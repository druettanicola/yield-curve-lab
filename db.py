"""Il database SQL.

Salviamo i dati in SQLite (un singolo file, già incluso in Python).
Formato "lungo": una riga per ogni giorno e per ogni scadenza, così le query SQL
sono semplici e flessibili.

    date        maturity   years   yield_pct
    2026-11-12  10 Yr      10.0    5.10

Tabelle: yields (curva nominale), real_yields (curva reale, TIPS), fred (serie macro).
"""
import os
import shutil
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from fetch_data import fetch_fred, fetch_year

DB_PATH = Path(__file__).parent / "data" / "yields.db"

# Nome della colonna nei dati del Tesoro -> durata in anni
MATURITY_YEARS = {
    "1 Mo": 1 / 12, "1.5 Month": 1.5 / 12, "2 Mo": 2 / 12, "3 Mo": 3 / 12,
    "4 Mo": 4 / 12, "6 Mo": 6 / 12, "1 Yr": 1, "2 Yr": 2, "3 Yr": 3,
    "5 Yr": 5, "7 Yr": 7, "10 Yr": 10, "20 Yr": 20, "30 Yr": 30,
}
REAL_MATURITIES = {"5 YR": 5, "7 YR": 7, "10 YR": 10, "20 YR": 20, "30 YR": 30}
FRED_SERIES = [
    "FEDFUNDS", "CPIAUCSL", "UNRATE", "USREC", "GS10", "TB3MS",
    # Europa (OECD via FRED, mensili): rendimento a 10 anni di Germania, Italia, Francia, Spagna, USA
    "IRLTLT01DEM156N", "IRLTLT01ITM156N", "IRLTLT01FRM156N", "IRLTLT01ESM156N", "IRLTLT01USM156N",
    # tassi interbancari a 3 mesi (Germania/area euro e USA), per confrontare la pendenza delle curve
    "IR3TIB01DEM156N", "IR3TIB01USM156N",
]
# FEDFUNDS = tasso Fed, CPIAUCSL = prezzi, UNRATE = disoccupazione, USREC = recessioni NBER,
# GS10 e TB3MS = titoli a 10 anni e a 3 mesi (mensili dal 1953)
MAX_WORKERS = 6  # download in parallelo


# ------------------------------------------------------------- download ----
def _retry(func, *args, attempts: int = 3, **kwargs):
    """Chiama func; se il download fallisce riprova (la rete a volte perde un colpo)."""
    for i in range(attempts):
        try:
            return func(*args, **kwargs)
        except Exception:
            if i == attempts - 1:
                raise
            time.sleep(2)


def _to_long(df: pd.DataFrame, maturities: dict) -> pd.DataFrame:
    """Da tabella 'larga' (una colonna per scadenza) a tabella 'lunga'."""
    cols = [c for c in df.columns if c in maturities]
    long = df.melt(id_vars="Date", value_vars=cols, var_name="maturity", value_name="yield_pct")
    long = long.dropna(subset=["yield_pct"])
    long["years"] = long["maturity"].map(maturities)
    long["date"] = long["Date"].dt.strftime("%Y-%m-%d")
    return long[["date", "maturity", "years", "yield_pct"]]


def _fetch_years(years: list[int], kind: str) -> pd.DataFrame:
    """Scarica più anni in parallelo (curva 'nominal' o 'real') e li restituisce in formato lungo."""
    maturities = MATURITY_YEARS if kind == "nominal" else REAL_MATURITIES
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        frames = list(pool.map(lambda year: _retry(fetch_year, year, kind), years))
    return pd.concat([_to_long(f, maturities) for f in frames]).sort_values(["date", "years"])


def _fred_all() -> pd.DataFrame:
    """Tutte le serie FRED, scaricate in parallelo."""
    def one(series: str) -> pd.DataFrame:
        df = _retry(fetch_fred, series)
        df.insert(0, "series", series)
        return df

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        return pd.concat(list(pool.map(one, FRED_SERIES)))


def _refresh_years() -> list[int]:
    """Anno corrente e precedente.

    Serve anche l'anno scorso: se l'ultimo aggiornamento è di fine dicembre e il successivo di gennaio,
    i giorni mancanti stanno nell'anno scorso e non vanno persi.
    """
    year = pd.Timestamp.today().year
    return [year - 1, year]


# ------------------------------------------------------------- database ----
def _connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or DB_PATH
    path.parent.mkdir(exist_ok=True)
    return sqlite3.connect(path)


def _replace_recent(con: sqlite3.Connection, table: str, new_rows: pd.DataFrame, since: str) -> None:
    """Sostituisce le righe dalla data 'since' in poi con quelle appena scaricate."""
    con.execute(f"DELETE FROM {table} WHERE date >= ?", (since,))
    new_rows.to_sql(table, con, if_exists="append", index=False)


def build(start_year: int = 1990) -> None:
    """Scarica tutto lo storico della curva nominale e crea il database."""
    data = _fetch_years(list(range(start_year, pd.Timestamp.today().year + 1)), "nominal")
    with _connect() as con:
        data.to_sql("yields", con, if_exists="replace", index=False)
        con.execute("CREATE INDEX idx_yields_date ON yields(date)")
    print(f"Database creato: {len(data):,} righe, {data['date'].min()} -> {data['date'].max()}")


def update(path: Path | None = None) -> None:
    """Riscarica solo gli ultimi due anni e aggiorna le righe (veloce)."""
    years = _refresh_years()
    new = _fetch_years(years, "nominal")
    with _connect(path) as con:
        _replace_recent(con, "yields", new, f"{years[0]}-01-01")


def build_macro(start_year: int = 2003) -> None:
    """Scarica i tassi reali (esistono dal 2003) e le serie FRED, e li salva nel database."""
    real = _fetch_years(list(range(start_year, pd.Timestamp.today().year + 1)), "real")
    fred = _fred_all()
    with _connect() as con:
        real.to_sql("real_yields", con, if_exists="replace", index=False)
        con.execute("CREATE INDEX idx_real_date ON real_yields(date)")
        fred.to_sql("fred", con, if_exists="replace", index=False)
    print(f"Dati macro creati: {len(real):,} righe di tassi reali, serie FRED: {FRED_SERIES}")


def update_macro(path: Path | None = None) -> None:
    """Aggiorna le serie FRED e gli ultimi due anni dei tassi reali."""
    years = _refresh_years()
    real = _fetch_years(years, "real")
    fred = _fred_all()
    with _connect(path) as con:
        _replace_recent(con, "real_yields", real, f"{years[0]}-01-01")
        fred.to_sql("fred", con, if_exists="replace", index=False)


_refresh_lock = threading.Lock()


def _refresh_copy() -> bool:
    """Aggiorna i dati su una COPIA del database e poi la sostituisce in un colpo solo.

    Chi sta leggendo il database in quel momento non vede mai una tabella a metà: o i dati vecchi
    o quelli nuovi. Se qualcosa va storto (rete assente, sito del Tesoro lento) il database
    originale resta com'è. Restituisce True se l'aggiornamento è riuscito.
    """
    if not _refresh_lock.acquire(blocking=False):
        return False  # un altro aggiornamento è già in corso
    tmp = DB_PATH.with_name(DB_PATH.name + ".refresh")
    try:
        shutil.copyfile(DB_PATH, tmp)
        update(tmp)
        update_macro(tmp)
        os.replace(tmp, DB_PATH)  # sostituzione atomica
        return True
    except Exception:
        return False
    finally:
        tmp.unlink(missing_ok=True)
        _refresh_lock.release()


def refresh_in_background() -> None:
    """Fa partire l'aggiornamento dei dati in secondo piano: la pagina non aspetta il download."""
    threading.Thread(target=_refresh_copy, name="data-refresh", daemon=True).start()


def macro_exists() -> bool:
    if not DB_PATH.exists():
        return False
    with _connect() as con:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    return {"real_yields", "fred"} <= tables


def exists() -> bool:
    return DB_PATH.exists()


def latest_date() -> "pd.Timestamp | None":
    """Data più recente nel database (serve per capire se i dati sono già aggiornati)."""
    if not DB_PATH.exists():
        return None
    with _connect() as con:
        row = con.execute("SELECT MAX(date) FROM yields").fetchone()
    return pd.Timestamp(row[0]) if row and row[0] else None


def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Esegue una query SQL e restituisce il risultato come tabella pandas."""
    with _connect() as con:
        return pd.read_sql_query(sql, con, params=params)


if __name__ == "__main__":
    build()
    build_macro()
