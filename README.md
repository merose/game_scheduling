# Game scheduling software

This repository includes scripts and software to help with game
scheduling and analysis of schedules.

## Prerequisites

- Python 3.x. Tested with Python 3.13.0.

## Installation

There is no need to install the package at this time. The supplied
analysis script does not have any dependencies.

## Schedule analysis script

The main script so far is `scripts/check_schedule.py`. It expects a
CSV file containing the schedule to check containing these headings in
the first row.

| Column heading | Contents                            |
| -------------- | --------                            |
| Division       | The division name                   |
| AwayTeam       | The away team name                  |
| HomeTeam       | The home team name                  |
| MatchDate      | The game date, like `Sat, Mar 2`    |
| StartTime      | The game start time, in 24hr format |
| EndTime        | The game end time, in 24hr format   |
| Field          | The field designation               |

The script expects the manager names to be embedded within the team names.

## Running the script

Run the script like this:

    $ python scripts/check_schedule.py <path-to-CSV-file>

It writes a report to the standard output containing any conflicts found,
followed by a summary for each division.

## Checks performed

- Game overlaps on the same field
- Game overlaps for same manager in different divisions
- Shows home/away for teams in each division
