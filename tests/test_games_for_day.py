"""Implement unit tests for GamesForDay."""

from scheduling import GamesForDay


def test_add_one_game(game):
    fields = [game.field, "another"]
    games_for_day = GamesForDay(game.date_str(), fields)
    games_for_day.add_game(game)
    assert games_for_day.get_game(game.field, 0).game_id() == game.game_id()
    assert games_for_day.get_game("another", 0) is None
