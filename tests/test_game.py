"""Implement unit tests of the game class."""

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
