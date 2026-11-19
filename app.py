"""Yield Curve Lab - nota di ricerca interattiva, in inglese e in italiano.

Struttura del file:
  1. lingua, impostazioni e stile (CSS)
  2. funzioni di formato (numeri, date) e caricamento dati
  3. una funzione per ogni parte della pagina
  4. la pagina vera e propria (in fondo)

I testi non sono scritti qui dentro: stanno in i18n.py, nelle due lingue.
"""
import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import about
import analysis as an
import db
from i18n import MONTHS, MONTHS_FULL, language_from_header, translator

st.set_page_config(page_title="Yield Curve Lab", page_icon="📈", layout="wide")


# ------------------------------------------------------------- lingua -----
def pick_language() -> str:
    """Lingua iniziale: ?lang=it o ?lang=en nell'indirizzo, altrimenti quella del browser."""
    if "lang" not in st.session_state:
        chosen = str(st.query_params.get("lang", "")).lower()
        if chosen not in ("it", "en"):
            try:
                header = st.context.headers.get("Accept-Language", "")
            except Exception:
                header = ""
            chosen = language_from_header(header)
        st.session_state["lang"] = chosen.upper()
    return st.session_state["lang"].lower()


LANG = pick_language()
t = translator(LANG)

# ---------------------------------------------------------------- stile ---
BG = "#0b0c0e"
TEXT = "#e1e1dc"
SOFT = "#b4b7ba"
MUTED = "#85888c"
RULE = "#25272b"
AMBER = "#e8a33d"
RED = "#e5534b"
BLUE = "#6fa8dc"
PURPLE = "#b58be0"
STATE_COLOR = {"Normal": TEXT, "Flat": AMBER, "Inverted": RED}
MONO = "IBM Plex Mono, ui-monospace, Menlo, monospace"
SANS = "IBM Plex Sans, system-ui, -apple-system, sans-serif"
SERIF = "Newsreader, Georgia, 'Times New Roman', serif"
GRID = dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.22)",
            color=MUTED, linecolor="rgba(255,255,255,0.15)")

# Superficie: blu notte (tassi vicini a zero) -> grigio-verde -> sabbia -> ambra (tassi alti)
SURFACE_SCALE = [
    [0.00, "#0f2a3d"], [0.22, "#2d5f7a"], [0.48, "#8aa5a6"],
    [0.74, "#e3c58a"], [1.00, "#f0a53a"],
]

st.markdown(
    f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap');
  html, body, .stApp, p, div, span, label, li {{ font-family: {SANS}; }}
  .stApp {{ background: {BG}; color: {TEXT}; }}
  header[data-testid="stHeader"], footer, #MainMenu {{ visibility: hidden; height: 0; }}
  .block-container {{ max-width: 1120px; padding-top: 1.2rem; padding-bottom: 3rem; }}
  .mono, .topbar, .ticker .l, .ticker .v, .ticker .d, .stats, .byline {{ font-family: {MONO}; }}

  .topbar {{ display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap;
             font-size: 12.5px; padding-bottom: 12px; border-bottom: 1px solid {RULE}; }}
  .topbar b {{ font-weight: 600; letter-spacing: .02em; color: #fff; }}
  .topbar span {{ color: {MUTED}; }}

  .nt {{ font-family: {SERIF} !important; font-weight: 500; color: #fff; letter-spacing: -0.012em; line-height: 1.1;
           font-size: clamp(2.05rem, 4.6vw, 3.3rem); max-width: 54rem; margin: 2.2rem 0 1rem 0; padding: 0; }}
  p.sub {{ font-size: 18px; line-height: 1.6; color: {SOFT}; max-width: 50rem; margin: 0; }}
  .byline {{ font-size: 12px; color: {MUTED}; margin-top: 16px; }}

  .ticker {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0; margin-top: 1.6rem;
             border-top: 1px solid {RULE}; }}
  .ticker .t {{ padding: 18px 20px 16px 0; margin-right: 20px; border-right: 1px solid {RULE}; }}
  .ticker .t:last-child {{ border-right: 0; }}
  .ticker .l {{ font-size: 11.5px; color: {MUTED}; }}
  .ticker .v {{ font-size: 25px; font-weight: 500; margin-top: 3px; font-feature-settings: 'tnum'; color: #fff; }}
  .ticker .d {{ font-size: 11.5px; color: {MUTED}; margin-top: 1px; }}
  .ticker svg {{ display: block; margin-top: 8px; max-width: 100%; }}
  .ticker .v small {{ font-size: 12.5px; font-weight: 400; color: {MUTED}; }}
  [data-testid="stHeaderActionElements"] {{ display: none !important; }}

  .keys {{ margin-top: 1.4rem; border-top: 1px solid {RULE}; padding-top: 1.1rem; }}
  .keys .h3 {{ font-family: {SERIF} !important; font-weight: 500; font-size: 24px; color: #fff; margin: 0 0 .6rem 0; padding: 0; }}
  .kp {{ display: grid; grid-template-columns: 250px 1fr; gap: 28px; padding: 14px 0; border-top: 1px solid {RULE}; }}
  .kp .lead {{ font-family: {SERIF}; font-size: 18px; line-height: 1.35; color: #fff; }}
  .kp .body {{ font-size: 15px; line-height: 1.65; color: {TEXT}; }}

  .sec {{ margin-top: 4.2rem; padding-top: 16px; border-top: 1px solid {RULE}; }}
  .sec .h2 {{ font-family: {SERIF} !important; font-weight: 500; font-size: 31px; line-height: 1.2; letter-spacing: -.01em;
             margin: 0; padding: 0; color: #fff; }}
  .subh {{ font-family: {SERIF} !important; font-weight: 500; font-size: 22px; color: #fff; margin: 2.4rem 0 .2rem 0; }}
  p.cap {{ color: {SOFT}; font-size: 15.5px; line-height: 1.7; max-width: 52rem; margin: .7rem 0 1rem 0; }}
  p.cap b {{ color: #fff; font-weight: 500; }}
  .figt {{ font-size: 14px; font-weight: 600; color: #fff; margin: 1.6rem 0 .3rem 0; }}
  .src {{ font-size: 12px; font-style: italic; color: {MUTED}; margin: .1rem 0 .5rem 0; }}
  p.note {{ color: {MUTED}; font-size: 13px; line-height: 1.6; max-width: 56rem; margin: .5rem 0 0 0;
            border-left: 2px solid {RULE}; padding-left: 12px; }}
  p.note b {{ color: {TEXT}; font-weight: 500; }}

  .intro {{ display: grid; grid-template-columns: 1.4fr 1fr; gap: 36px; padding: 6px 0; }}
  .intro p {{ font-size: 15px; line-height: 1.7; color: {TEXT}; margin: 0; }}
  .intro p b {{ color: #fff; font-weight: 600; }}
  .gloss {{ border-left: 1px solid {RULE}; padding-left: 28px; display: grid; gap: 12px; align-content: start; }}
  .gloss dt {{ font-family: {MONO}; font-size: 12px; color: #fff; }}
  .gloss dd {{ margin: 2px 0 0 0; font-size: 13px; line-height: 1.55; color: {MUTED}; }}

  .stats {{ display: flex; flex-wrap: wrap; gap: 0 38px; margin-top: .3rem; font-size: 13px; }}
  .stats div {{ padding: 6px 0; }}
  .stats span {{ color: {MUTED}; margin-right: 8px; }}

  .about p {{ font-size: 16px; line-height: 1.65; max-width: 46rem; color: {TEXT}; margin: .6rem 0 1rem 0; }}
  .about a {{ font-family: {MONO}; font-size: 13px; color: {AMBER}; text-decoration: none;
              border: 1px solid {RULE}; padding: 8px 14px; border-radius: 3px; display: inline-block; }}
  .about a:hover {{ border-color: {AMBER}; }}
  .foot {{ margin-top: 3.4rem; padding-top: 14px; border-top: 1px solid {RULE}; color: {MUTED};
           font-size: 12.5px; line-height: 1.7; }}

  [data-testid="stExpander"] {{ border: 1px solid {RULE}; border-radius: 3px; background: transparent; }}
  [data-testid="stExpander"] summary {{ font-size: 14px; }}
  [data-baseweb="input"], [data-baseweb="base-input"] {{ border-radius: 3px !important; }}
  label, .stDateInput label, [data-testid="stWidgetLabel"] p {{ color: {MUTED} !important; font-size: 12.5px !important; }}
  div[role="radiogroup"] label p {{ font-family: {MONO}; font-size: 12.5px !important; }}

  @media (max-width: 900px) {{
    .ticker {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .ticker .t {{ border-right: 0; border-bottom: 1px solid {RULE}; margin-right: 12px; padding-right: 8px; }}
    .kp {{ grid-template-columns: 1fr; gap: 4px; }}
    .intro {{ grid-template-columns: 1fr; gap: 20px; }}
    .gloss {{ border-left: 0; padding-left: 0; border-top: 1px solid {RULE}; padding-top: 16px; }}
  }}
  @media (max-width: 560px) {{
    .ticker .v {{ font-size: 21px; }}
    p.sub {{ font-size: 16.5px; }}
    .stats {{ gap: 0 22px; }}
  }}
</style>
""",
    unsafe_allow_html=True,
)

# Barra degli strumenti sempre visibile; trascina un riquadro per zoomare, doppio clic per tornare indietro
CHART_CONFIG = dict(
    displayModeBar=True, displaylogo=False, doubleClick="reset+autosize", scrollZoom=False,
    modeBarButtonsToRemove=["lasso2d", "select2d"],
)

# Pulsanti di periodo per i grafici nel tempo
RANGE_SELECTOR = dict(
    buttons=[
        dict(count=1, label="1Y", step="year", stepmode="backward"),
        dict(count=5, label="5Y", step="year", stepmode="backward"),
        dict(count=10, label="10Y", step="year", stepmode="backward"),
        dict(step="all", label="All" if LANG == "en" else "Tutto"),
    ],
    x=0, xanchor="left", y=1.015, yanchor="bottom",
    bgcolor="#14161a", activecolor="#3a3d44", bordercolor="#25272b", borderwidth=1,
    font=dict(color="#85888c", size=11),
)

# Dall'alto verso il basso nei grafici nel tempo: barra degli strumenti (0-30 px), legenda, pulsanti di periodo, grafico.
# Le posizioni sono calcolate in pixel dall'altezza del grafico, così non si sovrappongono mai.
TOP_MARGIN = 84


def time_layout(height: int) -> dict:
    plot_height = height - TOP_MARGIN - 10
    return dict(
        margin=dict(l=10, r=10, t=TOP_MARGIN, b=10),
        legend=dict(orientation="h", y=1 + 31 / plot_height, yanchor="bottom", x=0, font=dict(color="#85888c")),
    )


def selector(height: int) -> dict:
    """Pulsanti di periodo posizionati subito sopra l'area del grafico."""
    return dict(RANGE_SELECTOR, y=1 + 2 / (height - TOP_MARGIN - 10))


def style_time_chart(fig, index, height: int, hoverformat: str, y: dict | None = None) -> None:
    """Stile comune dei grafici nel tempo: legenda, pulsanti di periodo, assi e hover.

    L'altezza serve sia al grafico sia alla posizione di legenda e pulsanti: passarla una volta sola
    evita che i tre valori diventino diversi.
    """
    fig.update_layout(
        **base_layout(height=height, hovermode="x unified", **time_layout(height)),
        **xy_axes(x=dict(rangeselector=selector(height), range=[index.min(), index.max()],
                         hoverformat=hoverformat), y=y or {}),
    )


def show(fig, toolbar: bool = True) -> None:
    """Mostra un grafico Plotly con zoom attivo (toolbar=False nasconde la barra degli strumenti)."""
    config = CHART_CONFIG if toolbar else dict(CHART_CONFIG, displayModeBar=False)
    st.plotly_chart(fig, config=config)  # larghezza piena: è il comportamento predefinito


def base_layout(**kwargs) -> dict:
    """Impostazioni grafiche comuni a tutti i grafici (sfondo trasparente, font, legenda, separatori)."""
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=MONO, color=TEXT, size=12),
        margin=dict(l=10, r=10, t=28, b=10),
        legend=dict(orientation="h", y=1.1, x=0, font=dict(color=MUTED)),
        separators=",." if LANG == "it" else ".,",  # virgola decimale in italiano
    )
    layout.update(kwargs)
    return layout


def xy_axes(**extra) -> dict:
    """Assi 2D con griglia sottile e senza decorazioni."""
    return dict(xaxis=dict(**GRID, **extra.pop("x", {})), yaxis=dict(**GRID, **extra.pop("y", {})))


# ------------------------------------------------- formato numeri e date --
def n(value: float, decimals: int = 2) -> str:
    """Numero con la virgola decimale in italiano."""
    text = f"{float(value):.{decimals}f}"
    return text.replace(".", ",") if LANG == "it" else text


def signed(value: float, decimals: int = 2) -> str:
    """Numero con segno (+1.20 / -0.50); gli zeri non mostrano mai un segno ('-0.00' -> '0.00')."""
    value = round(float(value), decimals) + 0.0
    return n(value, decimals) if value == 0 else ("+" if value > 0 else "") + n(value, decimals)


def fd(date, fmt: str = "%B %Y") -> str:
    """Data con i nomi dei mesi nella lingua scelta: %B = mese intero (nelle frasi), %b = abbreviato (nei grafici)."""
    date = pd.Timestamp(date)
    fmt = fmt.replace("%B", MONTHS_FULL[LANG][date.month - 1]).replace("%b", MONTHS[LANG][date.month - 1])
    return date.strftime(fmt)


def state_label(state: str) -> str:
    return t(f"state_{state}")


# ---------------------------------------------------------------- dati ----
@st.cache_resource(ttl=6 * 3600)
def prepare_database() -> None:
    """Prepara il database.

    - Primo avvio (database assente): lo costruisce e aspetta, perché senza dati non c'è pagina.
    - Avvii successivi: parte subito con i dati già salvati e, se hanno 2 o più giorni, li aggiorna
      in secondo piano. Chi apre la pagina non aspetta il download.
    """
    latest = db.latest_date()
    if latest is None:
        db.build()
    if not db.macro_exists():
        try:
            db.build_macro()
        except Exception:
            pass  # i dati macro sono un extra: la pagina funziona anche senza
    elif not db.fred_complete():
        try:
            db.update_fred()  # database creato prima delle serie sul credito: le aggiunge una volta sola
        except Exception:
            pass
    if db.macro_exists() and latest is not None and (pd.Timestamp.today().normalize() - latest).days >= 2:
        db.refresh_in_background()


@st.cache_data(ttl=3600)
def load_all():
    prepare_database()
    wide, spread = an.load_wide(), an.load_spread()
    macro = None
    if db.macro_exists():
        macro = dict(
            policy=an.load_policy(), breakeven=an.load_breakeven(wide),
            probit=an.recession_probit(wide), bands=an.recession_bands(),
            bands_long=an.recession_bands("1959-01-01"),
        )
        try:
            macro["europe"] = an.load_europe()
        except Exception:
            macro["europe"] = None  # database creato prima delle serie europee
        try:
            macro["credit"] = an.credit_models()
            macro["high_yield"] = an.load_high_yield(wide)
        except Exception:
            macro["credit"] = None  # database creato prima delle serie sul credito
    return wide, spread, macro


def row_on(wide: pd.DataFrame, date) -> tuple[pd.Timestamp, pd.Series]:
    """Curva del giorno di mercato più vicino (precedente o uguale) alla data scelta."""
    date = pd.Timestamp(date)
    idx = max(wide.index.searchsorted(date, side="right") - 1, 0)
    return wide.index[idx], wide.iloc[idx]


def sparkline(values, color: str, width: int = 150, height: int = 34, zero_line: bool = False) -> str:
    """Mini grafico a linea in SVG (nessuna libreria): ultimi due anni, un punto a settimana."""
    v = np.asarray(values, dtype=float)
    lo, hi = float(v.min()), float(v.max())
    span = (hi - lo) or 1.0
    pad = 4
    xs = np.linspace(pad, width - pad, len(v))
    ys = height - pad - (v - lo) / span * (height - 2 * pad)
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    zero = ""
    if zero_line and lo < 0 < hi:
        y0 = height - pad - (0 - lo) / span * (height - 2 * pad)
        zero = f'<line x1="0" x2="{width}" y1="{y0:.1f}" y2="{y0:.1f}" stroke="#555a60" stroke-dasharray="2 3"/>'
    return (f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}">{zero}'
            f'<polyline fill="none" stroke="{color}" stroke-width="1.6" points="{points}"/>'
            f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="2.6" fill="{color}"/></svg>')


def add_bands(fig, bands, **kwargs):
    """Fasce grigie per le recessioni NBER."""
    for start, end in bands:
        fig.add_vrect(x0=start, x1=end, fillcolor="rgba(255,255,255,0.10)", line_width=0, layer="below", **kwargs)


def section(title: str, caption: str = ""):
    cap = f'<p class="cap">{caption}</p>' if caption else ""
    st.markdown(f'<div class="sec"><div class="h2" role="heading" aria-level="2">{title}</div></div>{cap}', unsafe_allow_html=True)


def subheading(title: str):
    st.markdown(f'<div class="subh">{title}</div>', unsafe_allow_html=True)


def figure_title(key: str):
    st.markdown(f'<div class="figt">{t(key)}</div>', unsafe_allow_html=True)


def source(key: str):
    st.markdown(f'<div class="src">{t(key)}</div>', unsafe_allow_html=True)


def stats_row(items: list[tuple[str, str]]):
    html = '<div class="stats">' + "".join(f"<div><span>{k}</span>{v}</div>" for k, v in items) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ------------------------------------------------------------ testata -----
def language_switch():
    """Selettore EN / IT in alto a destra; scrive anche ?lang= nell'indirizzo per poterlo condividere."""
    _, right = st.columns([8, 1.4])
    with right:
        st.radio("Language", ["EN", "IT"], horizontal=True, key="lang", label_visibility="collapsed")
    st.query_params["lang"] = LANG


def masthead(wide, spread, macro, bands):
    """Titolo con la tesi, sottotitolo e firma."""
    s = spread["spread"]
    latest = wide.index[-1]
    last = spread.iloc[-1]
    state = an.curve_state(last["spread"])
    since = an.days_since_inversion(s)
    episodes = an.inversion_episodes(s)
    clusters = an.inversion_clusters(s)
    rec_start, rec_end = pd.Timestamp(bands[-1][0]), pd.Timestamp(bands[-1][1])
    longest = episodes.loc[episodes["days"].idxmax()] if not episodes.empty else None
    years = latest.year - wide.index[0].year
    p = n(macro["probit"]["prob_now"] * 100, 0) if macro else None

    # La tesi si mostra solo se i dati la sostengono: l'ultima inversione è la più lunga, è finita
    # e da allora non c'è stata nessuna recessione. Altrimenti titolo generico.
    thesis = bool(macro and since is not None and clusters and longest is not None
                  and longest["start"] >= clusters[-1]["start"]
                  and rec_start < clusters[-1]["start"])
    if thesis:
        title = t("head_thesis", years=years)
        sub = t("sub_thesis", days=int(longest["days"]), start=fd(longest["start"]), end=fd(longest["end"]),
                rec_end=fd(rec_end), state=state_label(state).lower(), sp=signed(last["spread"] * 100, 0), p=p)
    else:
        title = t("head_generic")
        sub = t("sub_generic", last=fd(latest, "%d %B %Y"), state=state_label(state).lower(),
                sp=signed(last["spread"] * 100, 0), p=p if p else "n/a")

    byline = (t("byline", name=html.escape(about.NAME), last=fd(latest, "%d %B %Y")) if about.NAME
              else t("byline_plain", last=fd(latest, "%d %B %Y")))
    st.markdown(
        f"""
<div class="topbar"><b>Yield Curve Lab</b><span>{t('topbar', last=f'{latest:%Y-%m-%d}')}</span></div>
<div class="nt" role="heading" aria-level="1">{title}</div>
<p class="sub">{sub}</p>
<div class="byline">{byline}</div>
""",
        unsafe_allow_html=True,
    )


def ticker(wide, spread):
    latest = wide.index[-1]
    last = spread.iloc[-1]
    state = an.curve_state(last["spread"])
    since = an.days_since_inversion(spread["spread"])
    since_txt = t("tk_days_ago", n=since) if since is not None else t("tk_never")
    ago = row_on(wide, latest - pd.DateOffset(years=1))[1]
    recent = spread.tail(520).iloc[::5]  # circa due anni, un punto a settimana

    def delta(now, before):
        return t("tk_delta", v=signed((now - before) * 100, 0))

    st.markdown(
        f"""
<div class="ticker">
  <div class="t"><div class="l">{t('tk_10y')}</div><div class="v">{n(last['y10'])}%</div>
    <div class="d">{delta(last['y10'], ago[10])}</div>{sparkline(recent['y10'], TEXT)}</div>
  <div class="t"><div class="l">{t('tk_2y')}</div><div class="v">{n(last['y2'])}%</div>
    <div class="d">{delta(last['y2'], ago[2])}</div>{sparkline(recent['y2'], TEXT)}</div>
  <div class="t"><div class="l">{t('tk_spread')}</div><div class="v">{signed(last['spread'] * 100, 0)} bp</div>
    <div class="d">{t('tk_two_years')}</div>{sparkline(recent['spread'], STATE_COLOR[state], zero_line=True)}</div>
  <div class="t"><div class="l">{t('tk_curve')}</div>
    <div class="v" style="color:{STATE_COLOR[state]}">{state_label(state).upper()}</div>
    <div class="d">{t('tk_thresholds')}</div></div>
  <div class="t"><div class="l">{t('tk_last_inv')}</div><div class="v">{since_txt}</div>
    <div class="d">{t('tk_below_zero')}</div></div>
</div>
""",
        unsafe_allow_html=True,
    )


def key_points(wide, spread, macro, bands):
    """Le conclusioni in cima alla pagina. Ogni numero è calcolato dai dati; le frasi cambiano se i dati cambiano."""
    s = spread["spread"]
    latest = wide.index[-1]
    episodes = an.inversion_episodes(s)
    clusters = an.inversion_clusters(s)
    rec_start, rec_end = pd.Timestamp(bands[-1][0]), pd.Timestamp(bands[-1][1])
    leads = an.inversion_lead_times(s, [b[0] for b in bands])
    rows = []

    if episodes.empty:
        pass  # nessuna inversione nei dati: la prima conclusione non ha senso
    elif len(leads) >= 2 and clusters and rec_start < clusters[-1]["start"]:
        ep = episodes.iloc[-1]  # inversione più recente
        rows.append((t("kp1_k"), t("kp1_v", days=int(ep["days"]), start=fd(ep["start"]), end=fd(ep["end"]),
                                   low=signed(ep["low"] * 100, 0), n=len(leads), mn=min(leads), mx=max(leads),
                                   now=an.months_between(clusters[-1]["start"], latest), rec_end=fd(rec_end))))
    else:
        longest = episodes.loc[episodes["days"].idxmax()]
        rows.append((t("kp1_k"), t("kp1_alt", days=int(longest["days"]), start=fd(longest["start"]),
                                   end=fd(longest["end"]), low=signed(longest["low"] * 100, 0))))

    if macro:
        pr, pol, be = macro["probit"], macro["policy"].iloc[-1], macro["breakeven"].iloc[-1]
        rows.append((t("kp2_k"), t("kp2_v", peak=n(pr["recent_peak"] * 100, 0), date=fd(pr["recent_peak_date"]),
                                   p=n(pr["prob_now"] * 100, 0))))
        real = pol["real_rate"]
        stance = t("stance_restrictive") if real > 0.5 else t("stance_accommodative") if real < -0.5 else t("stance_neutral")
        rows.append((t("kp3_k"), t("kp3_v", ff=n(pol["fed_funds"]), cpi=n(pol["inflation"], 1), real=signed(real),
                                   stance=stance, sahm=n(pol["sahm"]),
                                   sahm_status=t("sahm_on") if pol["sahm"] >= 0.5 else t("sahm_off"))))
        fwd = be["fwd_5y5y"]
        anchor = t("anchor_ok") if abs(fwd - 2) <= 0.4 else t("anchor_above") if fwd > 2 else t("anchor_below")
        rows.append((t("kp4_k"), t("kp4_v", fwd=n(fwd), be10=n(be["be_10"]), anchor=anchor)))
        if macro.get("europe") is not None:
            it = macro["europe"]["it_de"].dropna()
            pre, post = it[it.index < "1999-01-01"], it[it.index >= "1999-01-01"]
            rows.append((t("kp5_k"), t("kp5_v", now=n(it.iloc[-1]), last_date=fd(it.index[-1]),
                                       pre_peak=n(pre.max()), pre_date=fd(pre.idxmax()),
                                       post_peak=n(post.max()), post_date=fd(post.idxmax()))))

    body = "".join(f'<div class="kp"><div class="lead">{k}</div><div class="body">{v}</div></div>' for k, v in rows)
    st.markdown(f'<div class="keys"><div class="h3" role="heading" aria-level="3">{t("kp_title")}</div>{body}</div>', unsafe_allow_html=True)


def reading_guide(last_y10: float):
    """Spiegazione per chi parte da zero, in un riquadro che si apre."""
    with st.expander(t("guide_title")):
        st.markdown(
            f"""<div class="intro">
  <p>{t('intro_p')}</p>
  <dl class="gloss">
    <div><dt>{t('gl_yield_k')}</dt><dd>{t('gl_yield_v', y10=n(last_y10))}</dd></div>
    <div><dt>{t('gl_spread_k')}</dt><dd>{t('gl_spread_v')}</dd></div>
    <div><dt>{t('gl_bp_k')}</dt><dd>{t('gl_bp_v')}</dd></div>
    <div><dt>{t('gl_inv_k')}</dt><dd>{t('gl_inv_v')}</dd></div>
  </dl>
</div>""",
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------ sezioni -----
@st.fragment
def surface_figure(wide, low_date):
    """Figura 1 (superficie 3D) con il selettore di vista.

    È un "frammento": cambiare vista ridisegna solo questo blocco, non tutta la pagina.
    """
    view_names = {"landscape": t("view_landscape"), "top": t("view_top"), "side": t("view_side")}
    choice = st.radio(t("view"), list(view_names.values()), horizontal=True, key=f"view_{LANG}")
    view = next(key for key, label in view_names.items() if label == choice)

    monthly = wide.resample("MS").mean().dropna()  # una curva al mese: superficie più liscia
    positions = list(range(len(an.GRID)))
    labels = list(an.GRID.values())
    idx10 = list(an.GRID).index(10)

    def as_year(ts: pd.Timestamp) -> float:
        """Data -> anno con decimali (es. 2023-07-03 -> 2023.50): asse numerico, più stabile in 3D."""
        return ts.year + (ts.dayofyear - 1) / 365.25

    fig = go.Figure()
    fig.add_trace(go.Surface(
        x=[as_year(d) for d in monthly.index], y=positions, z=monthly.values.T,
        colorscale=SURFACE_SCALE, cmin=0, showscale=True, opacity=1.0,
        colorbar=dict(title=dict(text=t("cb_yield"), side="right", font=dict(size=11, color=MUTED)),
                      orientation="h", x=0.5, xanchor="center", y=1.0, yanchor="bottom", len=0.6, thickness=8,
                      tickfont=dict(size=10, color=MUTED), ticksuffix="%", outlinewidth=0),
        lighting=dict(ambient=0.68, diffuse=0.7, specular=0.1, roughness=0.85, fresnel=0.1),
        hovertemplate="%{x:.1f}<br>%{z:.2f}%<extra></extra>",
    ))
    for date, color, name in [(low_date, RED, t("deepest")), (wide.index[-1], "#ffffff", t("latest_curve"))]:
        d, row = row_on(wide, date)
        fig.add_trace(go.Scatter3d(
            x=[as_year(d)] * len(positions), y=positions, z=row.values, mode="lines+markers",
            line=dict(color=color, width=8), marker=dict(size=3, color=color),
            name=f"{name} · {fd(d, '%d %b %Y')}",
            hovertemplate=f"{fd(d, '%d %b %Y')}<br>%{{z:.2f}}%<extra></extra>",
        ))

    # Etichette sugli eventi principali (solo nella vista "paesaggio": nelle altre si sovrappongono)
    notes = []
    if view == "landscape":
        for date, key in [("1990-03-01", "ev_1990"), ("2000-06-01", "ev_2000"), ("2006-12-01", "ev_2006"),
                          ("2020-04-01", "ev_2020"), ("2023-07-03", "ev_2023")]:
            d, row = row_on(wide, date)
            notes.append(dict(
                x=as_year(d), y=idx10, z=float(row[10]), text=t(key, z=n(row[10], 1)),
                showarrow=True, arrowhead=0, arrowcolor="#6a6e74", arrowwidth=1, ax=0, ay=-52,
                font=dict(size=11, color=TEXT, family=MONO), bgcolor="rgba(11,12,14,0.85)",
                bordercolor="#3a3d44", borderwidth=1, borderpad=3,
            ))

    views = {  # camera, proporzioni della scatola 3D
        "landscape": (dict(eye=dict(x=0.4, y=-2.15, z=1.15), center=dict(x=0, y=0, z=-0.12)), dict(x=1.7, y=0.9, z=0.55)),
        "top": (dict(eye=dict(x=0.0, y=-0.3, z=2.6), center=dict(x=0, y=0, z=-0.2)), dict(x=1.7, y=0.9, z=0.3)),
        "side": (dict(eye=dict(x=2.7, y=-0.15, z=0.35), center=dict(x=0, y=0, z=-0.1)), dict(x=1.7, y=1.2, z=0.6)),
    }
    camera, aspect = views[view]
    axis = dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.10)",
                zerolinecolor="rgba(255,255,255,0.10)", showspikes=False, color=MUTED,
                tickfont=dict(size=11), title_font=dict(size=12))
    fig.update_layout(
        **base_layout(
            margin=dict(l=0, r=0, t=56, b=0), height=640,
            legend=dict(orientation="h", y=0.0, x=0.0, font=dict(color=TEXT), bgcolor="rgba(11,12,14,0.7)"),
        ),
        scene=dict(
            xaxis=dict(title=t("ax_year"), tickformat=".0f", dtick=5, **axis),
            yaxis=dict(title=t("ax_maturity"), tickmode="array", tickvals=positions, ticktext=labels, **axis),
            zaxis=dict(title=t("ax_yield"), range=[0, float(monthly.values.max()) * 1.05], **axis),
            camera=camera, aspectmode="manual", aspectratio=aspect, bgcolor="rgba(0,0,0,0)",
            annotations=notes,
        ),
    )
    show(fig)
    # Il grafico 3D a volte si disegna troppo piccolo al primo caricamento: un evento di "resize" lo
    # costringe a ridimensionarsi. Sugli schermi stretti (telefono) la vista "paesaggio" passa inoltre a
    # una scena più compatta, altrimenti i lati verrebbero tagliati.
    st.html(
        f"""<script>
        const compact = {str(view == "landscape").lower()};
        const adapt = () => {{
          const w = window.parent;
          w.dispatchEvent(new Event('resize'));
          if (!compact || w.innerWidth >= 700 || !w.Plotly) return;
          const plot = [...w.document.querySelectorAll('.js-plotly-plot')].find(p => p._fullLayout && p._fullLayout.scene);
          if (plot) w.Plotly.relayout(plot, {{'scene.aspectratio': {{x: 1.35, y: 0.95, z: 0.55}},
                                              'scene.camera.eye': {{x: 0.35, y: -2.75, z: 1.4}}}});
        }};
        [400, 1000, 2000, 3500, 6000].forEach(ms => setTimeout(adapt, ms));
        </script>""",
        unsafe_allow_javascript=True,
    )
    source("src_treasury")


def curve_section(wide, spread, bands):
    s = spread["spread"]
    low_date, low = s.idxmin(), s.min()
    episodes = an.inversion_episodes(s)
    longest = episodes.loc[episodes["days"].idxmax()] if not episodes.empty else None
    section(t("h_curve"), t("h_curve_cap"))

    # --- Figura 1: superficie 3D
    figure_title("fig1")
    st.markdown(f'<p class="cap" style="margin-top:.2rem">{t("fig1_read")}</p>', unsafe_allow_html=True)
    surface_figure(wide, low_date)

    # --- Figura 2: spread 10Y-2Y
    if longest is not None:
        st.markdown(
            f'<p class="cap" style="margin-top:2.2rem">'
            f'{t("s2_cap", start=fd(longest["start"]), end=fd(longest["end"]), days=int(longest["days"]))}</p>',
            unsafe_allow_html=True,
        )
    figure_title("fig2")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.index, y=s.clip(lower=0), mode="lines", name=t("spread_pos"),
                             line=dict(color="#a3a6aa", width=1), fill="tozeroy",
                             fillcolor="rgba(163,166,170,0.18)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=s.index, y=s.clip(upper=0), mode="lines", name=t("inverted"),
                             line=dict(color=RED, width=1), fill="tozeroy",
                             fillcolor="rgba(229,83,75,0.5)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=s.index, y=s, mode="lines", line=dict(width=0), showlegend=False,
                             hovertemplate="%{y:+.2f} pp<extra></extra>"))
    add_bands(fig, bands)
    fig.add_annotation(x=low_date, y=low, text=f"{signed(low * 100, 0)} bp · {fd(low_date, '%b %Y')}", showarrow=True,
                       arrowcolor=RED, arrowwidth=1, arrowhead=0, ax=-70, ay=22, font=dict(size=11, color=RED))
    style_time_chart(fig, s.index, 400, "%Y-%m-%d", y=dict(title=t("pp_title")))
    show(fig)
    source("src_treasury")


def probit_section(macro, last_date):
    pr = macro["probit"]
    fitted = pr["fitted"]
    bands = macro["bands_long"]
    horizon_end = pr["recent_peak_date"] + pd.DateOffset(months=12)
    in_recession_then = any(pd.Timestamp(s0) <= horizon_end <= pd.Timestamp(e0) for s0, e0 in bands)
    outcome = ""
    if horizon_end <= pd.Timestamp(last_date) - pd.DateOffset(months=1):
        outcome = t("outcome_yes") if in_recession_then else t("outcome_no")
    section(t("h_model"), t("s3_cap", n=pr["n"], start=pr["start"].year, nrec=len(bands)))
    figure_title("fig3")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fitted.index, y=fitted * 100, mode="lines", name=t("prob_series"),
                             line=dict(color=AMBER, width=2), fill="tozeroy", fillcolor="rgba(232,163,61,0.14)",
                             hovertemplate="%{y:.0f}%<extra></extra>"))
    add_bands(fig, bands)
    fig.add_hline(y=50, line=dict(color="rgba(255,255,255,0.25)", width=1, dash="dot"))
    style_time_chart(fig, fitted.index, 380, "%Y-%m", y=dict(title=t("prob_y"), range=[0, 100]))
    show(fig)
    source("src_probit")
    stats_row([
        (t("st_now"), f"{n(pr['prob_now'] * 100, 0)}%"),
        (t("st_spread_10y3m"), f"{signed(pr['spread_now'] * 100, 0)} bp"),
        ("a", signed(pr["a"])), ("b", signed(pr["b"])),
        ("McFadden R²", n(pr["mcfadden"])), ("AUC", n(pr["auc"])),
    ])
    st.markdown(
        "<p class='note'>" + t("prob_note", peak=n(pr["recent_peak"] * 100, 0), date=fd(pr["recent_peak_date"]),
                               outcome=outcome, nrec=len(bands)) + "</p>",
        unsafe_allow_html=True,
    )


def credit_section(macro):
    cm, hy = macro["credit"], macro["high_yield"]
    data, rows = cm["data"], {r["h"]: r for r in cm["rows"]}
    nrec = len(macro["bands_long"])  # recessioni NBER dal 1960 (non i mesi di recessione)
    # figura 4: i due spread nel tempo
    section(t("h_credit"), t("s_credit_cap", start=data.index[0].year))
    figure_title("fig4")
    fig = go.Figure()
    for col, key, color, width in [("term", "cr_term", BLUE, 1.6), ("credit", "cr_credit", AMBER, 2.0)]:
        fig.add_trace(go.Scatter(x=data.index, y=data[col], name=t(key), line=dict(color=color, width=width),
                                 hovertemplate="%{y:+.2f} pp<extra></extra>"))
    add_bands(fig, macro["bands_long"])
    style_time_chart(fig, data.index, 380, "%Y-%m", y=dict(title=t("pp_title")))
    show(fig)
    source("src_credit")

    # figura 5: AUC dei tre modelli, per orizzonte
    figure_title("fig5")
    horizons = sorted(rows)
    labels = [t("hz_0") if h == 0 else t("hz_n", h=h) for h in horizons]
    fig = go.Figure()
    for model, key, color in [("term", "auc_term", BLUE), ("credit", "auc_credit", AMBER), ("both", "auc_both", "#d7d7d2")]:
        values = [rows[h][model]["auc"] for h in horizons]
        fig.add_trace(go.Bar(x=labels, y=values, name=t(key), marker_color=color, text=[n(v) for v in values],
                             textposition="outside", textfont=dict(color=MUTED, size=11),
                             hovertemplate="%{y:.2f}<extra>" + t(key) + "</extra>"))
    fig.add_hline(y=0.5, line=dict(color="rgba(255,255,255,0.30)", width=1, dash="dot"))
    fig.update_layout(
        **base_layout(height=360, barmode="group", margin=dict(l=10, r=10, t=56, b=10),
                      legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, font=dict(color=MUTED))),
        **xy_axes(y=dict(title=t("auc_y"), range=[0.4, 0.95])),
    )
    show(fig, toolbar=False)
    source("src_credit")
    r12, r0 = rows[12], rows[0]
    stats_row([
        (t("st_credit", date=fd(cm["credit_now_date"], "%b %Y")), t("pp_unit", v=n(cm["credit_now"]))),
        (t("st_credit_avg", year=data.index[0].year), t("pp_unit", v=n(cm["credit_mean"]))),
        (t("st_auc12_term"), n(r12["term"]["auc"])), (t("st_auc12_credit"), n(r12["credit"]["auc"])),
        (t("st_auc12_both"), n(r12["both"]["auc"])),
    ])
    st.markdown("<p class='note'>" + t(
        "credit_note", start=data.index[0].year, nrec=nrec, t12=n(r12["term"]["auc"]), c12=n(r12["credit"]["auc"]),
        b12=n(r12["both"]["auc"]), t0=n(r0["term"]["auc"]), c0=n(r0["credit"]["auc"])) + "</p>",
        unsafe_allow_html=True)

    # figura 6: junk bond contro T-bill a 3 mesi (ultimi 3 anni)
    figure_title("fig6")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hy.index, y=hy, name=t("hy_series"), line=dict(color=AMBER, width=2),
                             hovertemplate="%{y:.2f} pp<extra></extra>"))
    style_time_chart(fig, hy.index, 340, "%Y-%m-%d", y=dict(title=t("pp_title")))
    show(fig)
    source("src_hy")
    stats_row([
        (t("st_hy", date=fd(hy.index[-1], "%d %b %Y")), t("pp_unit", v=n(hy.iloc[-1]))),
        (t("st_hy_range", date=fd(hy.index[0], "%b %Y")), f"{n(hy.min())} - {n(hy.max())} pp"),
    ])
    st.markdown("<p class='note'>" + t("hy_note", start=fd(hy.index[0], "%B %Y"), lo=n(hy.min()), hi=n(hy.max()))
                + "</p>", unsafe_allow_html=True)


def policy_section(macro, bands):
    pol = macro["policy"]
    pol = pol[pol.index >= "1990-01-01"]
    last = pol.iloc[-1]
    sahm_now = last["sahm"]
    section(t("h_fed"), t("s4_cap"))
    figure_title("fig7")
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.42, 0.30, 0.28])
    fig.add_trace(go.Scatter(x=pol.index, y=pol["fed_funds"], name=t("ff_rate"), line=dict(color=AMBER, width=2),
                             hovertemplate="%{y:.2f}%<extra>Fed funds</extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=pol.index, y=pol["inflation"], name=t("cpi_yoy"), line=dict(color=BLUE, width=2),
                             hovertemplate="%{y:.1f}%<extra>CPI</extra>"), row=1, col=1)
    real = pol["real_rate"]
    fig.add_trace(go.Scatter(x=pol.index, y=real.clip(lower=0), name=t("real_pos"), line=dict(width=0),
                             fill="tozeroy", fillcolor="rgba(232,163,61,0.45)", hoverinfo="skip"), row=2, col=1)
    fig.add_trace(go.Scatter(x=pol.index, y=real.clip(upper=0), name=t("real_neg"), line=dict(width=0),
                             fill="tozeroy", fillcolor="rgba(111,168,220,0.45)", hoverinfo="skip"), row=2, col=1)
    fig.add_trace(go.Scatter(x=pol.index, y=real, line=dict(width=0), showlegend=False,
                             hovertemplate="%{y:+.1f}<extra>real</extra>"), row=2, col=1)
    fig.add_trace(go.Scatter(x=pol.index, y=pol["sahm"], name=t("sahm_series"), line=dict(color="#d7d7d2", width=1.6),
                             hovertemplate="%{y:.2f}<extra>Sahm</extra>"), row=3, col=1)
    fig.add_hline(y=0.5, row=3, col=1, line=dict(color=RED, width=1, dash="dot"))
    add_bands(fig, bands, row="all", col=1)
    fig.update_layout(**base_layout(height=690, hovermode="x unified", **time_layout(690)))
    fig.update_xaxes(**GRID, hoverformat="%Y-%m")
    fig.update_yaxes(**GRID)
    fig.update_xaxes(range=[pol.index.min(), pol.index.max()])
    fig.update_xaxes(rangeselector=selector(690), row=1, col=1)
    fig.update_yaxes(title_text="%", row=1, col=1)
    fig.update_yaxes(title_text=t("real_y"), row=2, col=1)
    fig.update_yaxes(title_text=t("sahm_y"), row=3, col=1)
    show(fig)
    source("src_policy")
    stats_row([
        (t("st_ff"), f"{n(last['fed_funds'])}%"),
        (t("st_cpi"), f"{n(last['inflation'], 1)}%"),
        (t("st_real"), t("pp_unit", v=signed(last["real_rate"]))),
        (t("st_unemp"), f"{n(last['unemployment'], 1)}%"),
        (t("st_sahm"), f"{t('pp_unit', v=n(sahm_now))} {t('sahm_triggered') if sahm_now >= 0.5 else t('sahm_below')}"),
    ])


def inflation_section(macro):
    be = macro["breakeven"]
    last = be.iloc[-1]
    low_date = be["be_10"].idxmin()
    section(t("h_infl"), t("s5_cap", low=n(be.loc[low_date, "be_10"]), date=fd(low_date)))
    figure_title("fig8")
    col_left, col_right = st.columns([2.6, 1])
    with col_left:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=be.index, y=be["be_5"], name=t("be5"), line=dict(color="#8c9097", width=1.4),
                                 hovertemplate="%{y:.2f}%<extra>5Y</extra>"))
        fig.add_trace(go.Scatter(x=be.index, y=be["be_10"], name=t("be10"), line=dict(color=TEXT, width=1.8),
                                 hovertemplate="%{y:.2f}%<extra>10Y</extra>"))
        fig.add_trace(go.Scatter(x=be.index, y=be["fwd_5y5y"], name=t("fwd"), line=dict(color=AMBER, width=2.2),
                                 hovertemplate="%{y:.2f}%<extra>5y5y</extra>"))
        fig.add_hline(y=2, line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dot"),
                      annotation_text=t("target2"), annotation_font=dict(size=10, color=MUTED),
                      annotation_position="bottom left")
        style_time_chart(fig, be.index, 400, "%Y-%m-%d", y=dict(title=t("per_year")))
        show(fig)
    with col_right:
        parts = go.Figure()
        parts.add_trace(go.Bar(x=[t("nominal10_x")], y=[last["real_10"]], name=t("real_yield"), marker_color=BLUE,
                               text=[n(last["real_10"])], textposition="inside"))
        parts.add_trace(go.Bar(x=[t("nominal10_x")], y=[last["be_10"]], name=t("exp_infl"), marker_color=AMBER,
                               text=[n(last["be_10"])], textposition="inside", textfont=dict(color="#111")))
        parts.update_layout(**base_layout(height=400, barmode="stack", showlegend=True,
                                          margin=dict(l=10, r=10, t=84, b=10)),
                            **xy_axes(y=dict(title="%")))
        parts.update_xaxes(showgrid=False)
        show(parts, toolbar=False)
    source("src_infl")
    stats_row([
        (t("st_nominal10"), f"{n(last['nominal_10'])}%"), (t("st_real10"), f"{n(last['real_10'])}%"),
        (t("st_be10"), f"{n(last['be_10'])}%"), (t("st_be5"), f"{n(last['be_5'])}%"),
        (t("st_fwd"), f"{n(last['fwd_5y5y'])}%"),
    ])
    st.markdown("<p class='note'>" + t("infl_note", year=be.index.min().year) + "</p>", unsafe_allow_html=True)


def europe_section(macro):
    eu = macro["europe"]
    it = eu["it_de"].dropna()
    pre, post = it[it.index < "1999-01-01"], it[it.index >= "1999-01-01"]
    section(t("h_italy"), t("s6_cap", pre_peak=n(pre.max()), pre_date=fd(pre.idxmax()),
                            post_peak=n(post.max()), post_date=fd(post.idxmax()),
                            last_date=fd(it.index[-1]), now=n(it.iloc[-1])))

    # --- Figura 9: rendimenti a 10 anni
    figure_title("fig9")
    fig = go.Figure()
    for col, name, color, width in [("de10", t("eu_de"), "#f4f4f2", 1.8), ("it10", t("eu_it"), AMBER, 2.2),
                                    ("us10", t("eu_us"), BLUE, 1.6)]:
        s = eu[col].dropna()
        fig.add_trace(go.Scatter(x=s.index, y=s, name=name, line=dict(color=color, width=width),
                                 hovertemplate="%{y:.2f}%<extra></extra>"))
    style_time_chart(fig, eu.index, 400, "%Y-%m", y=dict(title="%"))
    show(fig)
    source("src_europe")

    # --- Figura 10: spread contro il Bund
    figure_title("fig10")
    fig = go.Figure()
    for col, name, color, width in [("fr_de", t("eu_spread_fr"), "#8c9097", 1.2), ("es_de", t("eu_spread_es"), PURPLE, 1.4),
                                    ("it_de", t("eu_spread_it"), AMBER, 2.4)]:
        s = eu[col].dropna()
        fig.add_trace(go.Scatter(x=s.index, y=s, name=name, line=dict(color=color, width=width),
                                 hovertemplate="%{y:.2f} pp<extra></extra>"))
    for date, key in [("1999-01-01", "ev_euro"), ("2012-07-26", "ev_whatever")]:
        fig.add_shape(type="line", x0=date, x1=date, y0=0, y1=1, yref="paper",
                      line=dict(color="rgba(255,255,255,0.35)", width=1, dash="dot"))
        fig.add_annotation(x=date, y=0.99, yref="paper", text=t(key), showarrow=False, xanchor="left",
                           xshift=5, yanchor="top", font=dict(size=10.5, color=MUTED))
    style_time_chart(fig, eu.index, 400, "%Y-%m", y=dict(title=t("eu_spread_y")))
    show(fig)
    source("src_europe")

    # --- Figura 11: pendenza della curva, USA contro Germania / area euro
    figure_title("fig11")
    fig = go.Figure()
    for col, name, color, width in [("term_us", t("eu_term_us"), BLUE, 1.8), ("term_de", t("eu_term_de"), "#f4f4f2", 1.8)]:
        s = eu[col].dropna()
        fig.add_trace(go.Scatter(x=s.index, y=s, name=name, line=dict(color=color, width=width),
                                 hovertemplate="%{y:+.2f} pp<extra></extra>"))
    add_bands(fig, macro["bands"])
    style_time_chart(fig, eu.index, 400, "%Y-%m", y=dict(title=t("eu_slope_y")))
    show(fig)
    source("src_europe")

    latest = lambda col: eu[col].dropna().iloc[-1]  # noqa: E731  ultimo valore disponibile di ogni serie
    stats_row([
        (t("st_it_de"), t("pp_unit", v=n(latest("it_de")))), (t("st_es_de"), t("pp_unit", v=n(latest("es_de")))),
        (t("st_fr_de"), t("pp_unit", v=n(latest("fr_de")))),
        (t("st_term_us"), t("pp_unit", v=signed(latest("term_us")))),
        (t("st_term_de"), t("pp_unit", v=signed(latest("term_de")))),
    ])
    st.markdown("<p class='note'>" + t("eu_note", it_end=fd(it.index[-1])) + "</p>", unsafe_allow_html=True)


@st.fragment
def explore_section(wide, spread):
    section(t("h_explore"))

    # --- confronto tra due giorni
    subheading(t("s7_title"))
    st.markdown(f'<p class="cap" style="margin-top:.2rem">{t("s7_cap")}</p>', unsafe_allow_html=True)
    first, last = wide.index[0].date(), wide.index[-1].date()
    col1, col2 = st.columns(2)
    date_a = col1.date_input(t("date_a"), value=spread["spread"].idxmin().date(),
                             min_value=first, max_value=last, key="date_a")
    date_b = col2.date_input(t("date_b"), value=last, min_value=first, max_value=last, key="date_b")

    maturities = list(an.GRID)
    fig = go.Figure()
    items = []
    for label, date, color in [("A", date_a, "#f4f4f2"), ("B", date_b, AMBER)]:
        d, row = row_on(wide, date)
        sp = row[10] - row[2]
        state = an.curve_state(sp)
        items.append((f"{label} · {d:%Y-%m-%d}",
                      f'{signed(sp * 100, 0)} bp <b style="color:{STATE_COLOR[state]}">{state_label(state).lower()}</b>'))
        fig.add_trace(go.Scatter(
            x=maturities, y=row.values, mode="lines+markers", name=f"{label} · {fd(d, '%d %b %Y')}",
            line=dict(color=color, width=2.5), marker=dict(size=6),
            hovertemplate="%{x}Y<br>%{y:.2f}%<extra></extra>",
        ))
    fig.update_layout(**base_layout(height=380), **xy_axes(
        x=dict(title=t("ax_maturity"), type="log", tickvals=maturities, ticktext=list(an.GRID.values())),
        y=dict(title=t("ax_yield"))))
    show(fig)
    stats_row(items)

    # --- Nelson-Siegel
    subheading(t("s8_title"))
    st.markdown(f'<p class="cap" style="margin-top:.2rem">{t("s8_cap")}</p>', unsafe_allow_html=True)
    date = st.date_input(t("day"), value=last, min_value=first, max_value=last, key="date_ns")
    d, row = row_on(wide, date)
    mats = np.array(list(an.GRID), dtype=float)
    try:
        fit = an.fit_nelson_siegel(mats, row.values)
    except RuntimeError:
        st.warning(t("fit_failed"))
        return

    grid = np.geomspace(0.25, 30, 200)
    fitted = an.nelson_siegel(grid, fit["level"], fit["slope"], fit["curvature"], fit["tau"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grid, y=fitted, mode="lines", name=t("ns_model"), line=dict(color=AMBER, width=2.5)))
    fig.add_trace(go.Scatter(x=mats, y=row.values, mode="markers", name=t("ns_market"),
                             marker=dict(color="#f4f4f2", size=8, line=dict(color=BG, width=2))))
    fig.update_layout(**base_layout(height=360), **xy_axes(
        x=dict(title=t("ax_maturity"), type="log", tickvals=list(an.GRID), ticktext=list(an.GRID.values())),
        y=dict(title=t("ax_yield"))))
    show(fig)
    stats_row([
        (t("st_day"), f"{d:%Y-%m-%d}"), (t("st_level"), f"{n(fit['level'])}%"), (t("st_slope"), signed(fit["slope"])),
        (t("st_curvature"), signed(fit["curvature"])), (t("st_tau"), t("y_unit", v=n(fit["tau"], 1))),
        (t("st_rmse"), f"{n(fit['rmse_bps'], 1)} bp"),
    ])


def method_section():
    section(t("h_method"))
    with st.expander(t("exp_data")):
        st.markdown(t("data_text"))
        st.code(an.SPREAD_SQL.strip(), language="sql")
    with st.expander(t("exp_limits")):
        st.markdown(t("limits_text"))


def about_section():
    """Chi sono: compare solo se in about.py sono compilati nome o link LinkedIn."""
    if not (about.NAME or about.LINKEDIN):
        return
    bio = html.escape(about.BIO.get(LANG, ""))
    name = f"<b>{html.escape(about.NAME)}</b>" if about.NAME else ""
    link = (f'<a href="{html.escape(about.LINKEDIN, quote=True)}" target="_blank" rel="noopener noreferrer">{t("about_link")} →</a>'
            if about.LINKEDIN else "")
    section(t("about_title"))
    st.markdown(f'<div class="about"><p>{name}{" · " if name and bio else ""}{bio}</p>{link}</div>',
                unsafe_allow_html=True)


# ------------------------------------------------------------- pagina -----
language_switch()

with st.spinner(t("loading")):
    wide, spread, macro = load_all()

bands = macro["bands"] if macro else an.RECESSIONS

masthead(wide, spread, macro, bands)
ticker(wide, spread)
key_points(wide, spread, macro, bands)
reading_guide(float(spread.iloc[-1]["y10"]))
curve_section(wide, spread, bands)
if macro:
    probit_section(macro, wide.index[-1])
    if macro.get("credit") is not None:
        credit_section(macro)
    policy_section(macro, bands)
    inflation_section(macro)
    if macro.get("europe") is not None:
        europe_section(macro)
explore_section(wide, spread)
method_section()
about_section()

st.markdown(f'<div class="foot">{t("footer")}</div>', unsafe_allow_html=True)
