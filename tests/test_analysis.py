"""Test delle funzioni di analisi. Lavorano su dati sintetici: niente rete, niente database."""
import numpy as np
import pandas as pd
import pytest

import analysis as an


def daily(values, start="2020-01-01") -> pd.Series:
    """Serie giornaliera di spread a partire da una lista di valori."""
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="D"))


# --- stato della curva -----------------------------------------------------------------------------
@pytest.mark.parametrize("spread, expected", [
    (-0.50, "Inverted"), (-0.01, "Inverted"),
    (0.00, "Flat"), (0.24, "Flat"),
    (0.25, "Normal"), (2.00, "Normal"),
])
def test_curve_state_thresholds(spread, expected):
    assert an.curve_state(spread) == expected


# --- inversioni ---------------------------------------------------------------------------------------
def test_days_since_inversion():
    s = daily([0.5] * 5 + [-0.2] * 3 + [0.4] * 10)
    assert an.days_since_inversion(s) == 10
    assert an.days_since_inversion(daily([0.5] * 5)) is None


def test_episodes_ignore_short_blips():
    # 30 giorni positivi, 5 negativi (un "lampo"), 30 positivi, 20 negativi (un vero episodio), 10 positivi
    s = daily([0.5] * 30 + [-0.1] * 5 + [0.5] * 30 + [-0.3] * 20 + [0.5] * 10)
    episodes = an.inversion_episodes(s, min_days=10)
    assert len(episodes) == 1
    row = episodes.iloc[0]
    assert row["days"] == 20
    assert row["low"] == pytest.approx(-0.3)


def test_episodes_empty_when_never_inverted():
    assert an.inversion_episodes(daily([0.5] * 50)).empty


def test_clusters_merge_close_episodes_only():
    # due episodi a circa 6 mesi di distanza si fondono; un terzo, due anni dopo, resta separato
    values = [-0.1] * 20 + [0.5] * 180 + [-0.1] * 20 + [0.5] * 730 + [-0.1] * 20 + [0.5] * 10
    clusters = an.inversion_clusters(daily(values))
    assert len(clusters) == 2
    assert clusters[0]["end"] > clusters[0]["start"] + pd.Timedelta(days=180)


def test_lead_time_counts_months_from_first_inversion():
    s = daily([-0.2] * 60 + [0.5] * 600)  # inversione dal gennaio 2020
    assert an.inversion_lead_times(s, ["2020-09-01"]) == [8]


def test_lead_time_ignores_recessions_without_a_recent_inversion():
    s = daily([-0.2] * 60 + [0.5] * 1500)
    assert an.inversion_lead_times(s, ["2024-06-01"]) == []  # troppi mesi dopo: oltre i 36


def test_months_between():
    assert an.months_between(pd.Timestamp("2022-07-06"), pd.Timestamp("2026-11-12")) == 52


# --- Nelson-Siegel ---------------------------------------------------------------------------------------
def test_nelson_siegel_fit_recovers_a_known_curve():
    maturities = np.array(list(an.GRID), dtype=float)
    truth = dict(level=5.0, slope=-1.5, curvature=2.0, tau=2.5)
    yields = an.nelson_siegel(maturities, **truth)
    fit = an.fit_nelson_siegel(maturities, yields)
    assert fit["rmse_bps"] < 1.0
    fitted = an.nelson_siegel(maturities, fit["level"], fit["slope"], fit["curvature"], fit["tau"])
    assert np.allclose(fitted, yields, atol=0.01)


def test_nelson_siegel_long_run_level():
    # per scadenze molto lunghe il modello tende al livello
    assert an.nelson_siegel([1000.0], 5.0, -1.0, 1.0, 2.0)[0] == pytest.approx(5.0, abs=0.01)


# --- conversione del tasso a 3 mesi ------------------------------------------------------------------------
def test_bond_equivalent_to_discount_roundtrip():
    bey = 4.32
    d = an.bond_equivalent_to_discount(bey) / 100
    back = 365 * d / (360 - d * 91) * 100  # formula inversa
    assert back == pytest.approx(bey, abs=1e-6)
    assert an.bond_equivalent_to_discount(bey) < bey  # il tasso a sconto è sempre più basso


# --- fasce di recessione (indicatore NBER) -----------------------------------------------------------------
def test_recession_bands_from_indicator(monkeypatch):
    months = pd.date_range("2000-01-01", "2002-12-01", freq="MS")
    usrec = pd.Series(0, index=months)
    usrec.loc["2001-03-01":"2001-05-01"] = 1
    monkeypatch.setattr(an, "load_fred", lambda series: usrec)
    assert an.recession_bands(since="1999-01-01") == [("2001-03-01", "2001-05-31")]
