#!/usr/bin/env python3
"""
CAN-FD bit timing calculator.

Given a CAN controller clock, find valid nominal (arbitration) and
data-phase bit timing configurations: prescaler (BRP), TSEG1, TSEG2,
resulting bit rate and sample point.

Bit timing model (generic, bxCAN / M_CAN style):
    tq          = BRP / f_clock
    bit_time    = (1 [SyncSeg] + TSEG1 + TSEG2) * tq
    bitrate     = 1 / bit_time
    sample_pt   = (1 + TSEG1) / (1 + TSEG1 + TSEG2) * 100 %

Note: TSEG ranges differ per controller — adjust ``tseg1_max`` /
``tseg2_max`` to match your hardware (defaults fit many Bosch-style
controllers).
"""

import argparse

SYNC_SEG = 1
TARGET_SAMPLE_POINT = 87.5  # %, common design target


def timing_for(f_clock_hz, brp, tseg1, tseg2):
    """Return (bitrate_hz, sample_point_pct) for a timing configuration."""
    if brp < 1 or tseg1 < 1 or tseg2 < 1:
        raise ValueError("BRP, TSEG1 and TSEG2 must be >= 1")
    total_tq = SYNC_SEG + tseg1 + tseg2
    tq = brp / f_clock_hz
    bitrate = 1.0 / (total_tq * tq)
    sample_point = (SYNC_SEG + tseg1) / total_tq * 100.0
    return bitrate, sample_point


def find_configs(f_clock_hz, target_bps, brp_max=64,
                 tseg1_max=16, tseg2_max=8,
                 tol=0.005, sp_min=75.0, sp_max=90.0, limit=10):
    """Search timing configs hitting ``target_bps`` within ``tol`` (fraction).

    Returns a list of dicts sorted by closeness to the target sample
    point, then by bitrate error.
    """
    hits = []
    for brp in range(1, brp_max + 1):
        for tseg1 in range(1, tseg1_max + 1):
            for tseg2 in range(1, tseg2_max + 1):
                bitrate, sp = timing_for(f_clock_hz, brp, tseg1, tseg2)
                err = abs(bitrate - target_bps) / target_bps
                if err <= tol and sp_min <= sp <= sp_max:
                    hits.append({
                        "brp": brp,
                        "tseg1": tseg1,
                        "tseg2": tseg2,
                        "bitrate": bitrate,
                        "error_pct": err * 100.0,
                        "sample_point": sp,
                    })
    hits.sort(key=lambda h: (abs(h["sample_point"] - TARGET_SAMPLE_POINT),
                             h["error_pct"]))
    return hits[:limit]


def _parse_hz(text):
    return float(text.replace("_", ""))


def _print_table(title, target, configs):
    print(f"\n{title} (target {target:,.0f} bps)")
    print("-" * 72)
    if not configs:
        print("  no valid configuration found")
        return
    print(f"  {'BRP':>4} {'TSEG1':>6} {'TSEG2':>6} {'bitrate':>12} "
          f"{'err %':>8} {'sample pt':>10}")
    for c in configs:
        print(f"  {c['brp']:>4} {c['tseg1']:>6} {c['tseg2']:>6} "
              f"{c['bitrate']:>12,.0f} {c['error_pct']:>7.2f}% "
              f"{c['sample_point']:>9.1f}%")


def main():
    ap = argparse.ArgumentParser(
        description="Find CAN-FD nominal/data-phase bit timing configurations.")
    ap.add_argument("--clock", required=True,
                    help="CAN controller clock in Hz, e.g. 80000000")
    ap.add_argument("--nominal", required=True,
                    help="target nominal (arbitration) bitrate, e.g. 500000")
    ap.add_argument("--data", required=True,
                    help="target data-phase bitrate, e.g. 2000000")
    ap.add_argument("--limit", type=int, default=5,
                    help="configs to show per phase (default 5)")
    args = ap.parse_args()

    f_clock = _parse_hz(args.clock)
    nominal = _parse_hz(args.nominal)
    data = _parse_hz(args.data)

    _print_table("Nominal phase", nominal,
                 find_configs(f_clock, nominal, limit=args.limit))
    _print_table("Data phase", data,
                 find_configs(f_clock, data, limit=args.limit))


if __name__ == "__main__":
    main()
