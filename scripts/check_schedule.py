"""Check a schedule exported as CSV."""

import csv
from argparse import ArgumentParser
from datetime import datetime, timedelta


class Game:

    def __init__(self, division, away, home, date, start, stop, field):
        self.division = division
        self.away = away
        self.home = home
        self.duration = Duration(self.to_datetime(date, start),
                                 self.to_datetime(date, stop))
        self.field = field
        self.home_mgr = self.manager(home)
        self.away_mgr = self.manager(away)

    def manager(self, team):
        if team == 'TBD':
            return None
        first, second = team.split('-')
        if self.division.lower().startswith(first.lower()):
            return second
        else:
            return first

    def game_id(self):
        return f'{self.field}/{self.duration.ident()}/{self.division}'

    def to_datetime(self, date, tod):
        date_str = f'{datetime.now().year}-{date}'
        return datetime.strptime(f'{date_str} {tod}', '%Y-%a, %b %d %H:%M')


class Duration:

    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def ident(self):
        return self.start.isoformat()

    def overlaps(self, duration, delta=timedelta()):
        return self.start - delta <= duration.stop \
            and self.stop + delta >= duration.start


def make_duration(start, stop):
    return Duration(datetime.utcfromtimestamp(start),
                    datetime.utcfromtimestamp(stop))


def test_duration():
    dbig = make_duration(10, 20)
    dsmall = make_duration(12, 14)
    doverlap = make_duration(15, 25)
    dnone = make_duration(30, 40)
    assert dbig.overlaps(dsmall)
    assert dbig.overlaps(doverlap)
    assert not dbig.overlaps(dnone)
    assert dsmall.overlaps(dbig)
    assert not dsmall.overlaps(doverlap)
    assert not dsmall.overlaps(dnone)
    assert doverlap.overlaps(dbig)
    assert not doverlap.overlaps(dsmall)
    assert not doverlap.overlaps(dnone)
    assert not dnone.overlaps(dbig)
    assert not dnone.overlaps(dsmall)
    assert not dnone.overlaps(doverlap)


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


DIVISION_HDR = 'Division'
AWAY_HDR = 'AwayTeam'
HOME_HDR = 'HomeTeam'
DATE_HDR = 'MatchDate'
START_HDR = 'StartTime'
STOP_HDR = 'EndTime'
FIELD_HDR = 'Field'

def main():
    parser = ArgumentParser(description='Check schedule')
    parser.add_argument('file', help='Exported CSV schedule file')
    args = parser.parse_args()

    games = []
    with open(args.file, 'r') as infile:
        reader = csv.reader(infile)
        first_row = True
        for row in reader:
            if first_row:
                first_row = False
                division_col = row.index('Division')
                away_col = row.index('AwayTeam')
                home_col = row.index('HomeTeam')
                date_col = row.index('MatchDate')
                start_col = row.index('StartTime')
                stop_col = row.index('EndTime')
                field_col = row.index('Field')
            else:
                game = Game(division=row[division_col],
                            away=row[away_col],
                            home=row[home_col],
                            date=row[date_col],
                            start=row[start_col],
                            stop=row[stop_col],
                            field=row[field_col])
                games.append(game)

    print(f'Schedule file: {args.file}\n')

    divisions = set([g.division for g in games if g.division.find('playoffs') < 0])
    if not check_capitalization(divisions):
        print(f'ERROR: Some divisions vary in capitalization: {divisions}')
    managers = set([game.home_mgr for game in games if game.home_mgr]
                   + [game.away_mgr for game in games if game.away_mgr])
    if not check_capitalization(managers):
        print(f'ERROR: Some managers vary in capitalization: {managers}')
    fields = set([game.field for game in games])
    if not check_capitalization(fields):
        print(f'ERROR: Some fields vary in capitalization: {fields}')
    
    print(f'Games: {len(games)}')
    print(f'Divisions: {len(divisions)}')
    print(f'Managers: {len(managers)}')

    # Check for overlapping games
    field_conflicts = 0
    for field in sorted(fields):
        games_for_field = [game for game in games if game.field==field]
        games_for_field.sort(key=lambda game: game.duration.start)
        print(f'Games for field {field}: {len(games_for_field)}')

        if len(games_for_field) > 1:
            last = games_for_field[0]
            for game in games_for_field[1:]:
                if last.duration.overlaps(game.duration):
                    field_conflicts += 1
                    print(f'Game conflict: {last.game_id()} and {game.game_id()}')
    print(f'{field_conflicts} field conflicts')

    # Check for manager conflicts
    manager_conflicts = []
    for manager in sorted(managers):
        games_for_mgr = [game for game in games if game.home_mgr == manager \
                         or game.away_mgr == manager]
        games_for_mgr.sort(key=lambda game: game.duration.start)
        for i in range(len(games_for_mgr) - 1):
            prev = games_for_mgr[i]
            cur = games_for_mgr[i+1]
            if prev.duration.overlaps(
                    cur.duration, delta=timedelta(minutes=30)):
                manager_conflicts.append((manager, prev, cur))
    manager_conflicts.sort(key=lambda conflict: conflict[1].duration.start)
    for conflict in manager_conflicts:
        manager, prev, cur = conflict
        print(f'Manager conflict: {manager}: {prev.game_id()} and {cur.game_id()}')
    print(f'{len(manager_conflicts)} manager conflicts')

    # Check for Sunday games
    sun_games = [g for g in games if g.duration.start.weekday()==6]
    if sun_games:
        print(f'ERROR: {len(sun_games)} Sunday games')

    # Show date range and # games for each Saturday and M-F.
    dates = sorted(set(
        [day_start(g.duration.start) for g in games if g.duration.start.weekday()>=5]
        + [week_start(g.duration.start) for g in games if g.duration.start.weekday() < 5]))
    date_ranges = []
    for date in dates:
        if date.weekday() >= 5:
            date_ranges.append(days_duration(date, 1))
        else:
            date_ranges.append(days_duration(date, 5))
    print('\nGames by week')
    total_games_by_week = 0
    for date_range in date_ranges:
        date = date_range.start
        line = date.strftime('%a') if date.weekday()>=5 else 'M-F'
        line += f' {date.strftime("%m/%d")}:'
        range_games = [g for g in games if g.duration.overlaps(date_range)]
        line += f' {len(range_games):2d}'
        total_games_by_week += len(range_games)
        print(line)
    print(f'Total games by week: {total_games_by_week}')

    # Check for unreasonable game times.

    # Show home/away and round-robin for all divisions
    for division in sorted(divisions):
        print(f'\n---{division}---')
        games_for_division = [game for game in games if game.division==division]
        teams_for_division = sorted(set(
            [g.away for g in games_for_division]
            + [g.home for g in games_for_division]))
        matchups = [':'.join([g.home, g.away]) for g in games_for_division]
        plays = [':'.join(sorted([g.home, g.away])) for g in games_for_division]
        home_away = {k: 0 for k in matchups}
        total = {k: 0 for k in plays}
        home = {k: 0 for k in teams_for_division}
        away = {k: 0 for k in teams_for_division}
        sat_home = {k: 0 for k in teams_for_division}
        sat_away = {k: 0 for k in teams_for_division}
        for game in games_for_division:
            home[game.home] += 1
            away[game.away] += 1
            if game.duration.start.weekday() == 5:
                sat_home[game.home] += 1
                sat_away[game.away] += 1
            home_away[f'{game.home}:{game.away}'] += 1
            total[':'.join(sorted([game.home, game.away]))] += 1

        print('\nHome/away')
        for index, team in enumerate(teams_for_division):
            print(f'{index+1:2d}: {home[team]}/{away[team]} {team}')

        print('\nSaturday home/away')
        for index, team in enumerate(teams_for_division):
            print(f'{index+1:2d}: {sat_home[team]}/{sat_away[team]} {team}')

        print('\nMatchups')
        hdr = '    '
        for index, team in enumerate(teams_for_division):
            hdr += f' {index+1:3d}'
        print(hdr)
        bar = '    '
        for index, team in enumerate(teams_for_division):
            bar += f'----'
        print(bar)
        for index, home in enumerate(teams_for_division):
            line = f'{index+1:2d}: '
            for away in teams_for_division:
                k = f'{home}:{away}'
                if k in home_away:
                    line += f' {home_away[k]:3d}'
                else:
                    line += '    '
            print(line)

        print('\nTotal')
        hdr = '    '
        for index, team in enumerate(teams_for_division):
            hdr += f' {index+1:3d}'
        print(hdr)
        bar = '    '
        for index, team in enumerate(teams_for_division):
            bar += f'----'
        print(bar)
        for index, home in enumerate(teams_for_division):
            line = f'{index+1:2d}: '
            for away in teams_for_division:
                k = f'{home}:{away}'
                if k in total:
                    line += f' {total[k]:3d}'
                else:
                    line += '    '
            print(line)


if __name__ == '__main__':
    test_duration()
    main()
