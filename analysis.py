"""Analisi della curva dei rendimenti: dati in forma "larga", spread, fasi, modello.

Questo modulo non disegna niente: prepara i numeri che poi la dashboard (app.py) mostra.
"""
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, minimize
from scipy.stats import norm, rankdata

import db

# Scadenze "standard" usate per la superficie 3D, con la loro etichetta
GRID = {
    0.25: "3M", 0.5: "6M", 1: "1Y", 2: "2Y", 3: "3Y",
    5: "5Y", 7: "7Y", 10: "10Y", 20: "20Y", 30: "30Y",
}

# Recessioni USA secondo il NBER (National Bureau of Economic Research)
RECESSIONS = [
    ("1990-07-01", "1991-03-31"),
    ("2001-03-01", "2001-11-30"),
    ("2007-12-01", "2009-06-30"),
    ("2020-02-01", "2020-04-30"),
]

# --- SQL: spread 10 anni - 2 anni (stessa query che hai visto in queries.sql) ---
SPREAD_SQL = """
SELECT a.date,
       a.yield_pct AS y10,
       b.yield_pct AS y2,
       ROUND(a.yield_pct - b.yield_pct, 2) AS spread
FROM yields a
JOIN yields b ON a.date = b.date
WHERE a.maturity = '10 Yr' AND b.maturity = '2 Yr'
ORDER BY a.date
"""


def load_wide() -> pd.DataFrame:
    """Una riga per giorno, una colonna per scadenza (in anni). Buchi riempiti per interpolazione.

    Prima del 1993 non esiste il 20 anni: lo ricaviamo interpolando tra 10 e 30 anni.
    """
    long = db.query("SELECT date, years, yield_pct FROM yields")
    long["date"] = pd.to_datetime(long["date"])
    wide = long.pivot_table(index="date", columns="years", values="yield_pct")
    wide = wide.reindex(columns=sorted(GRID))  # solo le scadenze standard
    wide = wide.interpolate(axis=1, limit_area="inside")  # interpola tra scadenze vicine
    return wide.dropna(how="any")


def load_spread() -> pd.DataFrame:
    df = db.query(SPREAD_SQL)
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")


def curve_state(spread: float) -> str:
    """Fase della curva in base allo spread 10Y-2Y (in punti percentuali)."""
    if spread < 0:
        return "Inverted"
    elif spread < 0.25:
        return "Flat"
    return "Normal"


def days_since_inversion(spread: pd.Series) -> int | None:
    """Giorni passati dall'ultimo giorno con curva invertita (None se mai invertita)."""
    inverted = spread[spread < 0]
    if inverted.empty:
        return None
    return (spread.index[-1] - inverted.index[-1]).days


def inversion_episodes(spread: pd.Series, min_days: int = 10) -> pd.DataFrame:
    """Periodi consecutivi con spread negativo (ignora i 'lampi' più corti di min_days giorni).

    Restituisce una riga per periodo: inizio, fine, durata in giorni e spread minimo.
    """
    negative = spread < 0
    run_id = (negative != negative.shift()).cumsum()  # numera i blocchi consecutivi
    rows = []
    for _, block in spread[negative].groupby(run_id[negative]):
        days = (block.index[-1] - block.index[0]).days + 1
        if days >= min_days:
            rows.append({"start": block.index[0], "end": block.index[-1], "days": days, "low": block.min()})
    return pd.DataFrame(rows, columns=["start", "end", "days", "low"])


def inversion_clusters(spread: pd.Series, min_days: int = 10, merge_months: int = 12) -> list[dict]:
    """Raggruppa le inversioni vicine nel tempo in un'unica "ondata" (es. 2006-07 sono più episodi, una sola ondata)."""
    clusters: list[dict] = []
    for _, ep in inversion_episodes(spread, min_days).iterrows():
        if clusters and ep["start"] <= clusters[-1]["end"] + pd.DateOffset(months=merge_months):
            clusters[-1]["end"] = ep["end"]
            clusters[-1]["low"] = min(clusters[-1]["low"], ep["low"])
        else:
            clusters.append({"start": ep["start"], "end": ep["end"], "low": ep["low"]})
    return clusters


def months_between(start: pd.Timestamp, end: pd.Timestamp) -> int:
    return (end.year - start.year) * 12 + end.month - start.month


def inversion_lead_times(spread: pd.Series, recession_starts: list[str], window_months: int = 36) -> list[int]:
    """Mesi passati tra la PRIMA inversione di un'ondata e l'inizio della recessione successiva.

    Si considerano solo le recessioni con un'inversione nei 36 mesi precedenti.
    """
    clusters = inversion_clusters(spread)
    leads = []
    for rec_start in recession_starts:
        rec_start = pd.Timestamp(rec_start)
        before = [c for c in clusters if c["start"] <= rec_start
                  and months_between(c["start"], rec_start) <= window_months]
        if before:
            leads.append(months_between(max(before, key=lambda c: c["start"])["start"], rec_start))
    return leads


# --- Modello Nelson-Siegel -------------------------------------------------
def nelson_siegel(t, level, slope, curvature, tau):
    """Curva "liscia" descritta da 4 numeri:
    level     = rendimento di lungo periodo
    slope     = quanto i tassi corti stanno sotto (o sopra) quelli lunghi
    curvature = la "gobba" a medio termine
    tau       = dove si trova la gobba (in anni)
    """
    t = np.asarray(t, dtype=float)
    x = t / tau
    f1 = (1 - np.exp(-x)) / x
    f2 = f1 - np.exp(-x)
    return level + slope * f1 + curvature * f2


def fit_nelson_siegel(maturities, yields) -> dict:
    """Trova i 4 parametri che avvicinano di più il modello ai rendimenti osservati."""
    maturities = np.asarray(maturities, dtype=float)
    yields = np.asarray(yields, dtype=float)
    bounds = ([-5, -20, -40, 0.2], [20, 20, 40, 15])

    # Il problema ha più "valli": se partiamo da un solo punto l'ottimizzatore può fermarsi
    # in una valle mediocre. Proviamo diverse partenze e teniamo la soluzione migliore.
    best_params, best_error = None, np.inf
    for tau0 in (0.5, 1.5, 3.0, 6.0):
        for curvature0 in (-6.0, 0.0, 6.0):
            start = [yields[-1], yields[0] - yields[-1], curvature0, tau0]
            try:
                params, _ = curve_fit(nelson_siegel, maturities, yields, p0=start,
                                      bounds=bounds, maxfev=20000)
            except (RuntimeError, ValueError):
                continue  # questa partenza non converge o è fuori dai limiti: passiamo alla prossima
            error = float(np.sum((nelson_siegel(maturities, *params) - yields) ** 2))
            if error < best_error:
                best_params, best_error = params, error

    if best_params is None:
        raise RuntimeError("Nelson-Siegel: nessun punto di partenza ha portato a una soluzione")
    rmse_bps = float(np.sqrt(best_error / len(yields)) * 100)
    return {
        "level": best_params[0], "slope": best_params[1],
        "curvature": best_params[2], "tau": best_params[3], "rmse_bps": rmse_bps,
    }


# =============================================================================
# MACRO: inflazione attesa, politica monetaria, probabilità di recessione
# =============================================================================
def load_fred(series: str) -> pd.Series:
    """Una serie macro dal database (indice = data)."""
    df = db.query("SELECT date, value FROM fred WHERE series = ? ORDER BY date", (series,))
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")["value"]


def load_breakeven(wide: pd.DataFrame) -> pd.DataFrame:
    """Inflazione attesa dal mercato, dall'equazione di Fisher.

        tasso nominale = tasso reale + inflazione attesa
        breakeven      = nominale (titoli normali) - reale (titoli TIPS, protetti dall'inflazione)

    Il 5y5y forward e' l'inflazione attesa tra 5 e 10 anni da oggi: toglie l'effetto dei prezzi
    di breve periodo ed e' la misura che le banche centrali guardano per giudicare se le attese
    sono "ancorate". Si ricava da: (10 * BE10 - 5 * BE5) / 5 = 2 * BE10 - BE5.
    """
    real = db.query("SELECT date, years, yield_pct FROM real_yields")
    real["date"] = pd.to_datetime(real["date"])
    real = real.pivot_table(index="date", columns="years", values="yield_pct")
    out = pd.DataFrame({
        "nominal_10": wide[10], "real_10": real[10],
        "nominal_5": wide[5], "real_5": real[5],
    }).dropna()
    out["be_5"] = out["nominal_5"] - out["real_5"]
    out["be_10"] = out["nominal_10"] - out["real_10"]
    out["fwd_5y5y"] = 2 * out["be_10"] - out["be_5"]
    return out


def load_policy() -> pd.DataFrame:
    """Tasso della Fed, inflazione (variazione annua dei prezzi CPI), tasso reale e disoccupazione, per mese."""
    fed = load_fred("FEDFUNDS")
    cpi = load_fred("CPIAUCSL")
    unemployment = load_fred("UNRATE")
    # Regola di Sahm: media a 3 mesi della disoccupazione meno il suo minimo dei 12 mesi precedenti.
    # Da 0.5 punti in su, storicamente, l'economia e' gia' in recessione.
    avg3 = unemployment.rolling(3).mean()
    sahm = avg3 - avg3.shift(1).rolling(12).min()
    df = pd.DataFrame({
        "fed_funds": fed,
        "inflation": cpi.pct_change(12) * 100,
        "unemployment": unemployment,
        "sahm": sahm,
    }).dropna()
    # Tasso reale di politica monetaria: quanto "costa davvero" il denaro dopo l'inflazione.
    df["real_rate"] = df["fed_funds"] - df["inflation"]
    return df


def recession_bands(since: str = "1989-01-01") -> list[tuple[str, str]]:
    """Periodi di recessione NBER presi dall'indicatore ufficiale su FRED (USREC)."""
    usrec = load_fred("USREC")
    usrec = usrec[usrec.index >= since]
    bands, start = [], None
    for date, flag in usrec.items():
        if flag == 1 and start is None:
            start = date
        elif flag == 0 and start is not None:
            bands.append((str(start.date()), str((date - pd.Timedelta(days=1)).date())))
            start = None
    if start is not None:
        bands.append((str(start.date()), str(usrec.index[-1].date())))
    return bands


def bond_equivalent_to_discount(rate_pct: float, days: int = 91) -> float:
    """Converte un tasso a breve "bond-equivalent" (quello della curva par del Tesoro) nel tasso "a sconto".

    La serie TB3MS usata per stimare il probit è un tasso a sconto: per confrontare mele con mele,
    il valore di oggi va convertito allo stesso modo. Da  BEY = 365 d / (360 - d t)  si ricava
    d = 360 BEY / (365 + BEY t),  con t = giorni alla scadenza.
    """
    y = rate_pct / 100
    return 360 * y / (365 + days * y) * 100


def recession_probit(wide: pd.DataFrame, horizon: int = 12, start: str = "1960-01-01") -> dict:
    """Modello probit di Estrella-Mishkin (1996), lo stesso schema usato dalla Fed di New York.

        P(economia in recessione tra 12 mesi) = Phi(a + b * spread)    con spread = 10 anni - 3 mesi

    Phi e' la funzione di ripartizione della normale. Si stima per massima verosimiglianza sui dati
    mensili: la variabile da spiegare vale 1 se il mese t+12 e' un mese di recessione NBER.
    Per avere abbastanza recessioni la stima usa le serie mensili FRED dal 1960; la probabilita'
    di oggi usa invece lo spread piu' recente della curva del Tesoro, con il tasso a 3 mesi convertito
    "a sconto" per essere coerente con la serie usata nella stima.
    """
    spread_m = (load_fred("GS10") - load_fred("TB3MS")).dropna()
    spread_m = spread_m[spread_m.index >= start]
    usrec = load_fred("USREC").reindex(spread_m.index.union(load_fred("USREC").index)).fillna(0)
    # per il mese t: il mese t+horizon e' di recessione? (definizione standard di Estrella-Mishkin)
    future = usrec.shift(-horizon)
    data = pd.DataFrame({"spread": spread_m, "y": future}).dropna()

    x, y = data["spread"].to_numpy(), data["y"].to_numpy()

    def neg_log_likelihood(params):
        p = np.clip(norm.cdf(params[0] + params[1] * x), 1e-9, 1 - 1e-9)
        return -np.sum(y * np.log(p) + (1 - y) * np.log(1 - p))

    result = minimize(neg_log_likelihood, x0=[0.0, -0.5], method="BFGS")
    a, b = result.x
    null_ll = -neg_log_likelihood([norm.ppf(y.mean()), 0.0])
    mcfadden = 1 - (-result.fun) / null_ll  # quanto il modello migliora rispetto a "nessuna informazione"

    ranks = rankdata(norm.cdf(a + b * x))  # AUC: capacità di separare mesi pre-recessione dagli altri
    n1, n0 = int(y.sum()), int(len(y) - y.sum())
    auc = float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

    fitted = pd.Series(norm.cdf(a + b * spread_m), index=spread_m.index)
    spread_now = float(wide.iloc[-1][10] - bond_equivalent_to_discount(wide.iloc[-1][0.25]))
    # aggiungiamo il mese in corso, calcolato sulla curva del Tesoro piu' recente
    current_month = wide.index[-1].to_period("M").to_timestamp()
    if current_month > fitted.index[-1]:
        fitted.loc[current_month] = norm.cdf(a + b * spread_now)
    recent = fitted[fitted.index >= "2021-01-01"]
    return {
        "a": float(a), "b": float(b), "mcfadden": float(mcfadden), "auc": auc, "start": data.index[0],
        "n": len(data), "fitted": fitted,
        "spread_now": spread_now, "prob_now": float(norm.cdf(a + b * spread_now)),
        "recent_peak": float(recent.max()), "recent_peak_date": recent.idxmax(),
    }


def load_europe() -> pd.DataFrame:
    """Rendimenti a 10 anni di Germania, Italia, Francia, Spagna e USA (mensili), spread contro il Bund
    e pendenza della curva (10 anni meno 3 mesi) per USA e Germania/area euro. Dati OECD via FRED."""
    names = {
        "de10": "IRLTLT01DEM156N", "it10": "IRLTLT01ITM156N", "fr10": "IRLTLT01FRM156N",
        "es10": "IRLTLT01ESM156N", "us10": "IRLTLT01USM156N",
        "de3m": "IR3TIB01DEM156N", "us3m": "IR3TIB01USM156N",
    }
    df = pd.DataFrame({k: load_fred(v) for k, v in names.items()})
    df = df[df.index >= "1991-03-01"]  # prima data disponibile per l'Italia
    df["it_de"] = df["it10"] - df["de10"]  # spread BTP-Bund
    df["fr_de"] = df["fr10"] - df["de10"]
    df["es_de"] = df["es10"] - df["de10"]
    df["term_us"] = df["us10"] - df["us3m"]
    df["term_de"] = df["de10"] - df["de3m"]
    return df
