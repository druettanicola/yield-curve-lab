"""Test della scelta automatica della lingua e dei testi."""
import pytest

from i18n import STR, language_from_header, translator


@pytest.mark.parametrize("header, expected", [
    ("it-IT,it;q=0.9,en;q=0.8", "it"),          # recruiter italiano
    ("it", "it"),
    ("IT-it", "it"),                             # maiuscole e minuscole
    ("en-US,en;q=0.9", "en"),                    # recruiter americano
    ("en-GB,en;q=0.9,it;q=0.8", "en"),           # inglese prima, italiano come seconda lingua
    ("de-CH,de;q=0.9,en;q=0.8", "en"),           # altre lingue: inglese
    ("fr-FR,fr;q=0.9,it;q=0.5", "en"),           # l'italiano non è la lingua preferita
    ("en;q=0.4,it;q=0.9", "it"),                 # conta il peso, non l'ordine
    ("", "en"),                                  # nessuna intestazione
    (None, "en"),
    ("*", "en"),
])
def test_language_from_header(header, expected):
    assert language_from_header(header) == expected


def test_every_text_exists_in_both_languages():
    for key, (en, it) in STR.items():
        assert en.strip(), f"testo inglese vuoto: {key}"
        assert it.strip(), f"testo italiano vuoto: {key}"


def test_placeholders_match_between_languages():
    """Inglese e italiano devono usare gli stessi segnaposto {nome}, altrimenti uno dei due va in errore."""
    import string
    names = lambda text: {f for _, f, _, _ in string.Formatter().parse(text) if f}  # noqa: E731
    for key, (en, it) in STR.items():
        assert names(en) == names(it), f"segnaposto diversi in '{key}': {names(en)} contro {names(it)}"


def test_translator_switches_language():
    assert translator("en")("tk_never") == "never"
    assert translator("it")("tk_never") == "mai"
