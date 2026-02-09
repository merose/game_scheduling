"""Implement test fixtures for unit tests."""

from datetime import datetime, timezone

import pytest

from scheduling import Game


@pytest.fixture
def game_datetime():
    """Return the current timestamp."""
    return datetime.now(tz=timezone.utc)


@pytest.fixture
def game_date(game_datetime):
    """Return today's date as a game date in dayname, month, day format."""
    return game_datetime.strftime("%a, %b %d")


@pytest.fixture
def game(game_date):
    return Game(
        "Majors",
        "Washington-Majors",
        "Majors - Jefferson",
        game_date,
        "09:30",
        "11:30",
        "Field 1",
    )
