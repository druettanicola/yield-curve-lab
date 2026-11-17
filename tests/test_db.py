"""Test dell'aggiornamento in secondo piano: lavora su un database finto, senza rete."""
import sqlite3

import pytest

import db


def make_db(path):
    with sqlite3.connect(path) as con:
        con.execute("CREATE TABLE yields (date TEXT, maturity TEXT, years REAL, yield_pct REAL)")
        con.execute("INSERT INTO yields VALUES ('2026-11-12', '10 Yr', 10, 5.10)")


def rows(path):
    with sqlite3.connect(path) as con:
        return con.execute("SELECT date FROM yields ORDER BY date").fetchall()


@pytest.fixture
def fake_db(tmp_path, monkeypatch):
    path = tmp_path / "yields.db"
    make_db(path)
    monkeypatch.setattr(db, "DB_PATH", path)
    return path


def test_refresh_swaps_in_the_new_data(fake_db, monkeypatch):
    def fake_update(path=None):
        with sqlite3.connect(path) as con:
            con.execute("INSERT INTO yields VALUES ('2026-11-16', '10 Yr', 10, 5.12)")

    monkeypatch.setattr(db, "update", fake_update)
    monkeypatch.setattr(db, "update_macro", lambda path=None: None)
    assert db._refresh_copy() is True
    assert rows(fake_db) == [("2026-11-12",), ("2026-11-16",)]
    assert not fake_db.with_name("yields.db.refresh").exists()  # la copia temporanea è sparita


def test_failed_refresh_leaves_the_database_untouched(fake_db, monkeypatch):
    def broken_update(path=None):
        with sqlite3.connect(path) as con:
            con.execute("INSERT INTO yields VALUES ('2026-11-16', '10 Yr', 10, 5.12)")
        raise ConnectionError("sito non raggiungibile")

    monkeypatch.setattr(db, "update", broken_update)
    monkeypatch.setattr(db, "update_macro", lambda path=None: None)
    assert db._refresh_copy() is False
    assert rows(fake_db) == [("2026-11-12",)]  # i dati originali sono intatti
    assert not fake_db.with_name("yields.db.refresh").exists()


def test_only_one_refresh_runs_at_a_time(fake_db, monkeypatch):
    called = []
    monkeypatch.setattr(db, "update", lambda path=None: called.append("update"))
    monkeypatch.setattr(db, "update_macro", lambda path=None: None)
    assert db._refresh_lock.acquire(blocking=False)  # simula un aggiornamento già in corso
    try:
        assert db._refresh_copy() is False
        assert called == []
    finally:
        db._refresh_lock.release()
