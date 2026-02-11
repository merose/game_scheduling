"""Check a schedule exported as CSV."""

from argparse import ArgumentParser
from datetime import timedelta

from scheduling import Duration, parse_schedule


def check_capitalization(items):
    """Checks that no items in a list differ only in capitalization."""
    lower_items = [item.lower() for item in items]
    return len(items) == len(lower_items)


def day_start(d):
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def days_duration(d, days):
    """Get a duration of an integral number of days around a timestamp."""
    return Duration(day_start(d), day_start(d) + timedelta(days=days))


def week_start(d):
    return day_start(d) - timedelta(days=d.weekday())


def main():
    """Analyze the combined schedule."""
    parser = ArgumentParser(description="Check schedule")
    parser.add_argument("file", help="Exported CSV schedule file")
    args = parser.parse_args()

    print(f"Schedule file: {args.file}\n")
    games = parse_schedule(args.file)

    divisions = {g.division for g in games if g.division.find("playoffs") < 0}
    if not check_capitalization(divisions):
        print(f"ERROR: Some divisions vary in capitalization: {divisions}")
    managers = set(
        [game.home_mgr for game in games if game.home_mgr]
        + [game.away_mgr for game in games if game.away_mgr]
    )
    if not check_capitalization(managers):
        print(f"ERROR: Some managers vary in capitalization: {managers}")
    # print("Managers:")
    # for manager in managers:
    #     print(f"  {manager}")

    fields = {game.field for game in games}
    if not check_capitalization(fields):
        print(f"ERROR: Some fields vary in capitalization: {fields}")

    print(f"Games: {len(games)}")
    print(f"Divisions: {len(divisions)}")
    print(f"Managers: {len(managers)}")

    # Check for overlapping games
    field_conflicts = 0
    for field in sorted(fields):
        games_for_field = [game for game in games if game.field == field]
        games_for_field.sort(key=lambda game: game.duration.start)
        print(f"Games for field {field}: {len(games_for_field)}")

        if len(games_for_field) > 1:
            last = games_for_field[0]
            for game in games_for_field[1:]:
                if last.duration.overlaps(game.duration):
                    field_conflicts += 1
                    print(
                        f"Game conflict: {last.game_id()} and {game.game_id()}"
                    )
                last = game
    print(f"{field_conflicts} field conflicts")

    # Check for manager conflicts
    manager_conflicts = []
    for manager in sorted(managers):
        games_for_mgr = [
            game for game in games if manager in (game.home_mgr, game.away_mgr)
        ]
        games_for_mgr.sort(key=lambda game: game.duration.start)
        for i in range(len(games_for_mgr) - 1):
            prev = games_for_mgr[i]
            cur = games_for_mgr[i + 1]
            if prev.duration.overlaps(
                cur.duration, delta=timedelta(minutes=30)
            ):
                manager_conflicts.append((manager, prev, cur))
    manager_conflicts.sort(key=lambda conflict: conflict[1].duration.start)
    for conflict in manager_conflicts:
        manager, prev, cur = conflict
        print(
            f"Manager conflict: {manager}: {prev.game_id()} and {cur.game_id()}"
        )
    print(f"{len(manager_conflicts)} manager conflicts")

    # Check for Sunday games
    sun_games = [g for g in games if g.duration.start.weekday() == 6]  # noqa: PLR2004
    if sun_games:
        print(f"ERROR: {len(sun_games)} Sunday games")
        for g in sun_games:
            print(g)

    # Check for any team with 3 games in one Sun-Sat week. (Local rules may
    # further limit pitch count by calendar week.)
    games_by_div_mgr_week = {}
    for game in games:
        week, _ = game.week_and_day()
        if game.home_mgr is not None:
            key_home = (game.division, game.home_mgr, week)
            games_for_week = games_by_div_mgr_week.get(key_home, [])
            games_for_week.append(game)
            games_by_div_mgr_week[key_home] = games_for_week

        if game.away_mgr is not None:
            key_away = (game.division, game.away_mgr, week)
            games_for_week = games_by_div_mgr_week.get(key_away, [])
            games_for_week.append(game)
            games_by_div_mgr_week[key_away] = games_for_week
    mgrs_with_too_many_games = set()
    for key, game_list in games_by_div_mgr_week.items():
        if len(game_list) > 2:  # noqa: PLR2004
            mgrs_with_too_many_games.add(key[1])
            print(
                f"Too many games per week for {key[1]}:"
                f" {[g.game_id() for g in game_list]}"
            )
    print(f"{len(mgrs_with_too_many_games)} manager have >2 games per week")

    # Show date range and # games for each Saturday and M-F.
    dates = sorted(
        set(
            [
                day_start(g.duration.start)
                for g in games
                if g.duration.start.weekday() >= 5  # noqa: PLR2004
            ]
            + [
                week_start(g.duration.start)
                for g in games
                if g.duration.start.weekday() < 5  # noqa: PLR2004
            ]
        )
    )
    date_ranges = []
    for date in dates:
        if date.weekday() >= 5:  # noqa: PLR2004
            date_ranges.append(days_duration(date, 1))
        else:
            date_ranges.append(days_duration(date, 5))
    print("\nGames by week")
    total_games_by_week = 0
    for date_range in date_ranges:
        date = date_range.start
        line = date.strftime("%a") if date.weekday() >= 5 else "M-F"  # noqa: PLR2004
        line += f" {date.strftime('%m/%d')}:"
        range_games = [g for g in games if g.duration.overlaps(date_range)]
        line += f" {len(range_games):2d}"
        total_games_by_week += len(range_games)
        print(line)
    print(f"Total games by week: {total_games_by_week}")

    # Check for unreasonable game times.

    # Show home/away and round-robin for all divisions
    for division in sorted(divisions):
        print(f"\n---{division}---")
        games_for_division = [
            game for game in games if game.division == division
        ]
        print(f"Games for division: {len(games_for_division)}")
        teams_for_division = sorted(
            set(
                [g.away for g in games_for_division]
                + [g.home for g in games_for_division]
            )
        )
        matchups = [f"{g.home}:{g.away}" for g in games_for_division]
        plays = [
            ":".join(sorted([g.home, g.away])) for g in games_for_division
        ]
        home_away = dict.fromkeys(matchups, 0)
        total = dict.fromkeys(plays, 0)
        home = dict.fromkeys(teams_for_division, 0)
        away = dict.fromkeys(teams_for_division, 0)
        sat_home = dict.fromkeys(teams_for_division, 0)
        sat_away = dict.fromkeys(teams_for_division, 0)
        for game in games_for_division:
            home[game.home] += 1
            away[game.away] += 1
            if game.duration.start.weekday() == 5:  # noqa: PLR2004
                sat_home[game.home] += 1
                sat_away[game.away] += 1
            home_away[f"{game.home}:{game.away}"] += 1
            total[":".join(sorted([game.home, game.away]))] += 1

        print("\nHome/away")
        for index, team in enumerate(teams_for_division):
            print(f"{index + 1:2d}: {home[team]}/{away[team]} {team}")

        print("\nSaturday home/away")
        for index, team in enumerate(teams_for_division):
            print(f"{index + 1:2d}: {sat_home[team]}/{sat_away[team]} {team}")

        print("\nMatchups")
        hdr = "    "
        for index, _ in enumerate(teams_for_division):
            hdr += f" {index + 1:3d}"
        print(hdr)
        print("    " + ("----" * len(teams_for_division)))
        for index, home in enumerate(teams_for_division):
            line = f"{index + 1:2d}: "
            for away in teams_for_division:
                k = f"{home}:{away}"
                if k in home_away:
                    line += f" {home_away[k]:3d}"
                else:
                    line += "    "
            print(line)

        print("\nTotal")
        hdr = "    "
        for index, _ in enumerate(teams_for_division):
            hdr += f" {index + 1:3d}"
        print(hdr)
        print("    " + ("----" * len(teams_for_division)))
        for index, home in enumerate(teams_for_division):
            line = f"{index + 1:2d}: "
            for away in teams_for_division:
                k = f"{home}:{away}"
                if k in total:
                    line += f" {total[k]:3d}"
                else:
                    line += "    "
            print(line)


if __name__ == "__main__":
    main()
