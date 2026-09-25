"""Self-tests for canfd_timing.py (no third-party dependencies)."""

from canfd_timing import timing_for, find_configs


def test_timing_for_known_values():
    # 80 MHz clock, BRP=8 -> tq = 100 ns; 16 TQ/bit -> 625 kbit/s
    bitrate, sp = timing_for(80_000_000, brp=8, tseg1=13, tseg2=2)
    assert abs(bitrate - 625_000) < 1.0, bitrate
    assert abs(sp - 87.5) < 1e-9, sp


def test_timing_for_rejects_bad_params():
    for kwargs in ({"brp": 0}, {"tseg1": 0}, {"tseg2": 0}):
        try:
            timing_for(80_000_000, **{"brp": 1, "tseg1": 1, "tseg2": 1,
                                      **kwargs})
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {kwargs}")


def test_find_configs_hits_target():
    cfgs = find_configs(80_000_000, 500_000)
    assert cfgs, "expected at least one 500 kbit/s configuration"
    best = cfgs[0]
    assert best["error_pct"] <= 0.5, best
    assert 75.0 <= best["sample_point"] <= 90.0, best
    # sanity: recompute from the returned parameters
    bitrate, sp = timing_for(80_000_000, best["brp"],
                             best["tseg1"], best["tseg2"])
    assert abs(bitrate - best["bitrate"]) < 1.0
    assert abs(sp - best["sample_point"]) < 1e-9


def test_find_configs_data_phase():
    cfgs = find_configs(80_000_000, 2_000_000)
    assert cfgs, "expected at least one 2 Mbit/s configuration"
    assert cfgs[0]["error_pct"] <= 0.5


def test_find_configs_impossible_target():
    assert find_configs(80_000_000, 123_456_789) == []


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print("All tests passed.")
