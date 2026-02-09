"""Implement unit tests of the duration class."""

from datetime import datetime, timezone

from scheduling import Duration


def make_duration(start, stop):
    """Create a duration from a start and stop timestamp."""
    return Duration(
        datetime.fromtimestamp(start, tz=timezone.utc),
        datetime.fromtimestamp(stop, tz=timezone.utc),
    )


def test_duration():
    """Create sample durations and test checking for overlaps."""
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
