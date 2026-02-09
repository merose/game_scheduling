"""Implement an object representation of games."""

import re
from datetime import datetime

from scheduling import Duration


class Game:
    def __init__(self, division, away, home, date, start, stop, field):
        self.division = division
        self.away = away
        self.home = home
        self.duration = Duration(
            self.to_datetime(date, start), self.to_datetime(date, stop)
        )
        self.field = field
        self.home_mgr = self.manager(home)
        self.away_mgr = self.manager(away)

    def manager(self, team):
        if team == "TBD":
            return None
        first, second = re.split(" *- *", team)
        if first.lower().startswith(self.division.lower()):
            return second.lower()
        return first.lower()

    def game_id(self):
        return f"{self.field}/{self.duration.ident()}/{self.division}"

    def to_datetime(self, date, tod):
        date_str = f"{datetime.now().year}-{date}"  # noqa: DTZ005
        return datetime.strptime(f"{date_str} {tod}", "%Y-%a, %b %d %H:%M")  # noqa: DTZ007

    def date_str(self):
        """Get the game date as a string."""
        return self.duration.start.strftime("%Y-%m-%d")

    def time_str(self):
        """Get the game start time as a string."""
        return self.duration.start.strftime("%H:%M")

    def __repr__(self):
        return f"{self.duration.start.isoformat()} {self.away}@{self.home}"
