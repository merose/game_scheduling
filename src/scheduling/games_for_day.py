"""Implement a holder of games for a single day."""


class GamesForDay:
    """Represent all the games for a single day, for all fields."""

    def __init__(self, date, fields):
        """Create an instance to hold games for a specified day and fields."""
        self.date = date
        self.fields = fields
        self.games_for_field = {}
        for field in fields:
            self.games_for_field[field] = []

    def add_game(self, game):
        """Add a game for the day."""
        self.games_for_field[game.field].append(game)

    def row_count(self):
        """Get the number of rows necessary to show games for the day."""
        return max([len(games) for games in self.games_for_field.values()])

    def get_game(self, field, index):
        games = self.games_for_field[field]
        return None if index >= len(games) else games[index]

    def show(self):
        """Display the games for all fields."""
        self.print_hdr()
        for i in range(self.row_count()):
            for field in self.fields:
                game = self.get_game(field, i)
                if game is None:
                    print(f"{' ' * 19}  ", end="")  # noqa: T201
                else:
                    print(f"{game.time_str()} {game.division:<13s}  ", end="")  # noqa: T201
            print()  # noqa: T201
        print()  # noqa: T201

    def print_hdr(self):
        print(f"{self.date}")  # noqa: T201
        for field in self.fields:
            print(f"{field:<19s}  ", end="")  # noqa: T201
        print()  # noqa: T201
        for _ in self.fields:
            print(f"{'-' * 19}  ", end="")  # noqa: T201
        print()  # noqa: T201
