"""Cattura due immagini nitide della pagina vera (parte alta e grafico 3D), in inglese e in italiano.

Uso: con la pagina in esecuzione in locale (streamlit run app.py), dalla cartella del progetto:
    python docs/make_page_screenshots.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8501/"
OUT = Path(__file__).resolve().parent
ARGS = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]

with sync_playwright() as pw:
    browser = pw.chromium.launch(args=ARGS)
    for lang in ("en", "it"):
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page.goto(f"{BASE}?lang={lang}", wait_until="networkidle")
        page.wait_for_selector(".gl-container canvas", state="attached", timeout=60000)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(8000)  # il grafico 3D si assesta
        scroll = lambda y: page.evaluate(f"document.querySelector('[data-testid=\"stMain\"]').scrollTo(0, {y})")  # noqa: E731

        scroll(0)
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / f"page-top-{lang}.png"))

        # il grafico 3D: scorri fino al titolo della Figura 1
        page.evaluate("""() => { const el = [...document.querySelectorAll('.figt')][0];
                                 el.scrollIntoView({block: 'start'}); }""")
        page.wait_for_timeout(3500)
        page.screenshot(path=str(OUT / f"page-3d-{lang}.png"))
        page.close()
    browser.close()
print("Salvate:", sorted(p.name for p in OUT.glob("page-*.png")))
