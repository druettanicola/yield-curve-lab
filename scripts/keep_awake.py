"""Apre l'app Streamlit in un browser vero e, se dorme, clicca "svegliala".

Una semplice richiesta HTTP non basta: Streamlit Cloud considera attivita'
solo una sessione vera (websocket). Per questo usiamo Playwright.
"""
import sys
import time

from playwright.sync_api import sync_playwright

URL = "https://yield-curve-lab-druetta.streamlit.app/"
WAKE_TEXT = "get this app back up"   # "Yes, get this app back up!"
OK_TEXT = "Yield Curve Lab"          # compare solo quando l'app e' sveglia


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
        deadline = time.time() + 240
        woke = False
        while time.time() < deadline:
            # l'app vive dentro un iframe: controlliamo pagina e frame
            for frame in page.frames:
                try:
                    btn = frame.get_by_text(WAKE_TEXT, exact=False)
                    if btn.count():
                        btn.first.click()
                        woke = True
                        print("App addormentata: cliccato il pulsante di risveglio")
                        time.sleep(15)
                        break
                    if frame.get_by_text(OK_TEXT, exact=False).count():
                        print("App attiva" + (" (risvegliata)" if woke else ""))
                        browser.close()
                        return 0
                except Exception:
                    pass
            time.sleep(5)
        print("ERRORE: l'app non e' risultata attiva entro 4 minuti")
        page.screenshot(path="keep_awake_failed.png")
        browser.close()
        return 1


if __name__ == "__main__":
    sys.exit(main())
