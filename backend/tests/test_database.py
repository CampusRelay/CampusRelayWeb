import pytest

from app import database


def test_get_db_returns_session(monkeypatch):
    class FakeSession:
        closed = False

        def close(self):
            self.closed = True

    fake_session = FakeSession()

    monkeypatch.setattr(
        database,
        "SessionLocal",
        lambda: fake_session,
    )

    db_generator = database.get_db()

    session = next(db_generator)

    assert session is fake_session
    assert fake_session.closed is False

    with pytest.raises(StopIteration):
        next(db_generator)

    assert fake_session.closed is True
