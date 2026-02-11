"""Implement unit tests of the parser."""

import io
from email.message import Message

from scheduling import parse_schedule

CSV_DATA = (
    "Division,AwayTeam,HomeTeam,MatchDate,StartTime,EndTime,Field\n"
    'Majors,Washington-Majors,Majors - Jefferson,"Sat, Feb 14",09:30,11:30,Field 1\n'
)


class FakeResponse(io.BytesIO):
    def __init__(self, data):
        super().__init__(data)
        self.headers = Message()
        self.headers.add_header("Content-Type", "text/csv; charset=utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def test_parse_schedule_from_file(tmp_path):
    schedule = tmp_path / "schedule.csv"
    schedule.write_text(CSV_DATA, encoding="utf-8")

    games = parse_schedule(schedule)

    assert len(games) == 1
    assert games[0].division == "Majors"
    assert games[0].field == "Field 1"


def test_parse_schedule_from_url(monkeypatch):
    url = "https://example.com/schedule.csv"

    def fake_urlopen(requested_url):
        assert requested_url == url
        return FakeResponse(CSV_DATA.encode("utf-8"))

    monkeypatch.setattr("scheduling.parser.urlopen", fake_urlopen)

    games = parse_schedule(url)

    assert len(games) == 1
    assert games[0].division == "Majors"
    assert games[0].field == "Field 1"
