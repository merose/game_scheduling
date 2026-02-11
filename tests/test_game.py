"""Implement unit tests of the game class."""

from datetime import datetime

from scheduling import Game


def test_manager(game):
    assert game.away_mgr == "washington"
    assert game.home_mgr == "jefferson"


def test_manager_with_division_suffix(game_date):
    """Test that if the division has trailing text the manager is found."""
    game = Game(
        "Farm",
        "Washington-Farms",
        "Farms - Jefferson",
        game_date,
        "09:30",
        "11:30",
        "Field 1",
    )
    assert game.away_mgr == "washington"
    assert game.home_mgr == "jefferson"


def test_game_id(game):
    game_id = game.game_id()
    assert game_id.startswith("Field 1/")
    assert game_id.endswith("/Majors")


def test_date_str(game, game_datetime):
    assert game.date_str() == game_datetime.strftime("%Y-%m-%d")


def test_time_str(game):
    assert game.time_str() == "09:30"


def make_game_on_date(
    date_str,
    start="08:00",
    stop="10:00",
    division="Majors",
    away="TBD",
    home="TBD",
    field="Field 1",
):
    formatted_date = datetime.fromisoformat(date_str).strftime("%a, %b %d")
    return Game(division, away, home, formatted_date, start, stop, field)


def test_week_and_day():
    # 2026-02-09 is Monday
    _, week, _ = datetime.fromisoformat("2026-02-09").isocalendar()

    assert make_game_on_date("2026-02-08").week_and_day() == (week, 0)
    assert make_game_on_date("2026-02-09").week_and_day() == (week, 1)
    assert make_game_on_date("2026-02-10").week_and_day() == (week, 2)
    assert make_game_on_date("2026-02-11").week_and_day() == (week, 3)
    assert make_game_on_date("2026-02-12").week_and_day() == (week, 4)
    assert make_game_on_date("2026-02-13").week_and_day() == (week, 5)
    assert make_game_on_date("2026-02-14").week_and_day() == (week, 6)

    assert make_game_on_date("2026-02-07").week_and_day() == (week - 1, 6)
    assert make_game_on_date("2026-02-15").week_and_day() == (week + 1, 0)
