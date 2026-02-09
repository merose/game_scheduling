"""Represent a duration of time."""

from datetime import timedelta


class Duration:
    """Represent a duration of time."""

    def __init__(self, start, stop):
        """Create a new instance with given start and stop datetimes."""
        self.start = start
        self.stop = stop

    def ident(self):
        """Get the start time in a standard format."""
        return self.start.isoformat()

    def overlaps(self, duration, delta=timedelta()):
        """Tests whether this duration overlaps another."""
        return (
            self.start - delta <= duration.stop
            and self.stop + delta >= duration.start
        )
