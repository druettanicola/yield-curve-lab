"""Genera la copertina per LinkedIn (1200x627, salvata al doppio della risoluzione) con Chromium senza interfaccia (Playwright).

Uso, dalla cartella del progetto:   python docs/make_cover.py
I numeri e il grafico 3D vengono calcolati dagli stessi dati della pagina.
"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import plotly.graph_objects as go  # noqa: E402

import analysis as an  # noqa: E402

OUT = ROOT / "docs" / "linkedin-cover.png"
URL = "yield-curve-lab-druetta.streamlit.app"
SCALE = [[0.00, "#0f2a3d"], [0.22, "#2d5f7a"], [0.48, "#8aa5a6"], [0.74, "#e3c58a"], [1.00, "#f0a53a"]]

# ---- dati ------------------------------------------------------------------------------------
wide, spread = an.load_wide(), an.load_spread()
s = spread["spread"]
episodes = an.inversion_episodes(s)
longest = episodes.loc[episodes["days"].idxmax()]
cluster = an.inversion_clusters(s)[-1]
months_since = an.months_between(cluster["start"], wide.index[-1])
prob_now = an.recession_probit(wide)["prob_now"]
years = wide.index[-1].year - wide.index[0].year
month = lambda d: d.strftime("%b %Y")  # noqa: E731
low_date = s.idxmin()

# ---- grafico 3D ------------------------------------------------------------------------------
monthly = wide.resample("MS").mean().dropna()
year_of = lambda ts: ts.year + (ts.day_of_year - 1) / 365.25  # noqa: E731
positions = list(range(len(an.GRID)))

fig = go.Figure(go.Surface(
    x=[year_of(d) for d in monthly.index], y=positions, z=monthly.values.T,
    colorscale=SCALE, cmin=0, showscale=False,
    lighting=dict(ambient=0.68, diffuse=0.7, specular=0.1, roughness=0.85, fresnel=0.1),
))
for date, color, width in [(s.idxmin(), "#e5534b", 9), (wide.index[-1], "#ffffff", 9)]:
    row = wide.loc[:date].iloc[-1]
    fig.add_trace(go.Scatter3d(x=[year_of(date)] * len(positions), y=positions, z=row.values,
                               mode="lines", line=dict(color=color, width=width), showlegend=False))
hidden = dict(visible=False, showbackground=False)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=0, b=0), width=640, height=520,
    scene=dict(xaxis=hidden, yaxis=hidden, zaxis=dict(visible=False, showbackground=False, range=[0, 9.6]),
               camera=dict(eye=dict(x=0.35, y=-1.85, z=1.0), center=dict(x=0, y=0, z=-0.18)),
               aspectmode="manual", aspectratio=dict(x=1.7, y=0.95, z=0.55), bgcolor="rgba(0,0,0,0)"),
)
plot_html = fig.to_html(full_html=False, include_plotlyjs="inline",
                        config=dict(displayModeBar=False, scrollZoom=False))

# ---- pagina della copertina ---------------------------------------------------------------------
html = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500&family=Newsreader:opsz,wght@6..72,500&display=swap" rel="stylesheet">
<style>
  html, body {{ margin: 0; width: 1200px; height: 627px; background: #0b0c0e; overflow: hidden; }}
  .cover {{ position: relative; width: 1200px; height: 627px; color: #e1e1dc; font-family: 'IBM Plex Sans', sans-serif; }}
  .left {{ position: absolute; left: 60px; top: 52px; width: 500px; }}
  .brand {{ font: 500 14px 'IBM Plex Mono', monospace; color: #fff; letter-spacing: .02em; }}
  h1 {{ font: 500 44px/1.08 'Newsreader', Georgia, serif; color: #fff; letter-spacing: -.012em; margin: 26px 0 14px; }}
  .it {{ font: 400 19px/1.38 'Newsreader', Georgia, serif; color: #8e9196; font-style: italic; margin: 0; max-width: 440px; }}
  .facts {{ position: absolute; left: 60px; bottom: 62px; display: flex; gap: 40px; }}
  .fact {{ width: 205px; }}
  .fact b {{ display: block; font: 500 33px 'IBM Plex Mono', monospace; color: #fff; }}
  .fact span {{ display: block; margin-top: 5px; font: 400 12.5px/1.35 'IBM Plex Sans', sans-serif; color: #b4b7ba; }}
  .fact i {{ display: block; margin-top: 2px; font: italic 400 12px/1.35 'Newsreader', Georgia, serif; color: #7d8085; }}
  .plot {{ position: absolute; right: -12px; top: 36px; width: 640px; height: 520px; }}
  .legend {{ position: absolute; right: 60px; bottom: 62px; font: 400 11.5px 'IBM Plex Mono', monospace; color: #8a8d91; text-align: right; line-height: 1.7; }}
  .legend em {{ display: inline-block; width: 18px; height: 3px; margin-right: 7px; vertical-align: middle; }}
  .foot {{ position: absolute; left: 60px; right: 60px; bottom: 22px; display: flex; justify-content: space-between;
           font: 400 12px 'IBM Plex Mono', monospace; color: #6c6f73; }}
  .rule {{ position: absolute; left: 60px; right: 60px; bottom: 46px; border-top: 1px solid #25272b; }}
</style></head><body><div class="cover">
  <div class="left">
    <div class="brand">Yield Curve Lab</div>
    <h1>The longest yield-curve inversion in {years} years ended without a recession.</h1>
    <p class="it">La più lunga inversione della curva in {years} anni è finita senza una recessione.</p>
  </div>
  <div class="plot">{plot_html}</div>
  <div class="facts">
    <div class="fact"><b>{int(longest['days'])}</b><span>days inverted, {month(longest['start'])} to {month(longest['end'])}</span><i>giorni di inversione</i></div>
    <div class="fact"><b>{months_since}</b><span>months since the first inversion, still no recession</span><i>mesi dalla prima inversione, nessuna recessione</i></div>
    <div class="fact"><b>{prob_now * 100:.0f}%</b><span>probability of a recession in 12 months</span><i>probabilità di recessione a 12 mesi</i></div>
  </div>
  <div class="legend"><div><em style="background:#e5534b"></em>deepest inversion, {month(low_date)}</div><div><em style="background:#fff"></em>latest curve, {month(wide.index[-1])}</div><div>1990 → {wide.index[-1].year} · amber high rates, blue low</div></div>
  <div class="rule"></div>
  <div class="foot"><span>Nicola Druetta</span><span>{URL}</span></div>
</div></body></html>"""

from playwright.sync_api import sync_playwright  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    page_file = Path(tmp) / "cover.html"
    page_file.write_text(html, encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader",
                                           "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        page = browser.new_page(viewport={"width": 1200, "height": 627}, device_scale_factor=2)
        page.goto(page_file.as_uri(), wait_until="networkidle")
        page.wait_for_selector(".gl-container canvas", state="attached", timeout=30000)  # il grafico 3D è disegnato
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(2500)  # lascia finire il disegno
        page.screenshot(path=str(OUT))
        browser.close()
print("Salvata:", OUT)
