from pulse.breaker import Breaker


def test_opens_after_threshold():
    b = Breaker(threshold=2, cooldown_s=1000)
    b.record(False)
    assert b.allow()
    b.record(False)
    assert not b.allow()
