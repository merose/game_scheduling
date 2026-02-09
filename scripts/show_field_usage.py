"""Show field usage by day from a combined schedule."""

from argparse import ArgumentParser

from scheduling import GamesForDay, parse_schedule


def main():
    parser = ArgumentParser(description="Show field usage")
    parser.add_argument("file", help="Exported CSV schedule file")
    args = parser.parse_args()

    games = parse_schedule(args.file)
    games.sort(key=lambda game: game.duration.start)

    fields = list({game.field for game in games})
    fields.sort()

    dates = list({game.duration.start.strftime("%Y-%m-%d") for game in games})
    dates.sort()

    games_by_date = {}
    for game in games:
        date = game.date_str()
        if date not in games_by_date:
            games_by_date[date] = GamesForDay(date, fields)
        games_by_date[date].add_game(game)

    for date in dates:
        games_by_date[date].show()


if __name__ == "__main__":
    main()
