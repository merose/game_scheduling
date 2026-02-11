"""Implement a parser for reading a combined schedule."""

import csv
import io
from urllib.request import urlopen

from scheduling import Game

DIVISION_HDR = "Division"
AWAY_HDR = "AwayTeam"
HOME_HDR = "HomeTeam"
DATE_HDR = "MatchDate"
START_HDR = "StartTime"
STOP_HDR = "EndTime"
FIELD_HDR = "Field"


def parse_schedule(file):
    if _is_http_url(file):
        with urlopen(file) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            text = io.TextIOWrapper(response, encoding=charset, newline="")
            return _parse_rows(csv.reader(text))

    with open(file, encoding="utf-8-sig", newline="") as infile:
        return _parse_rows(csv.reader(infile))


def _is_http_url(file):
    return isinstance(file, str) and file.startswith(("http://", "https://"))


def _parse_rows(reader):
    games = []
    first_row = True
    for row in reader:
        if first_row:
            first_row = False
            division_col = row.index("Division")
            away_col = row.index("AwayTeam")
            home_col = row.index("HomeTeam")
            date_col = row.index("MatchDate")
            start_col = row.index("StartTime")
            stop_col = row.index("EndTime")
            field_col = row.index("Field")
        elif row[home_col] not in ("", "#N/A"):
            game = Game(
                division=row[division_col],
                away=row[away_col],
                home=row[home_col],
                date=row[date_col],
                start=row[start_col],
                stop=row[stop_col],
                field=row[field_col],
            )
            games.append(game)
    return games
