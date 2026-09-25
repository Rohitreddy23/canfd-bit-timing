[![CI](https://github.com/Rohitreddy23/canfd-bit-timing/actions/workflows/ci.yml/badge.svg)](https://github.com/Rohitreddy23/canfd-bit-timing/actions)

# CAN-FD Bit Timing Calculator

Finds valid CAN-FD **nominal (arbitration)** and **data-phase** bit timing
configurations for a given CAN controller clock: prescaler (BRP), TSEG1,
TSEG2, resulting bit rate and sample point.

This is the same math you do when bringing up CAN-FD on a new ECU —
usually buried in a spreadsheet. Here it's a small script you can run
from the terminal.

## Usage

```bash
python canfd_timing.py --clock 80000000 --nominal 500000 --data 2000000
```

Example output:

```
Nominal phase (target 500,000 bps)
------------------------------------------------------------------------
   BRP  TSEG1  TSEG2      bitrate    err %  sample pt
    10     13      2      500,000    0.00%      87.5%

Data phase (target 2,000,000 bps)
------------------------------------------------------------------------
   BRP  TSEG1  TSEG2      bitrate    err %  sample pt
     4      7      2    2,000,000    0.00%      80.0%
```

Results are ranked by closeness to an 87.5% sample point, then by bitrate
error. Only configurations with a sample point between 75% and 90% and a
bitrate error under 0.5% are listed.

## Tests

```bash
python test_canfd.py
```

## Notes

- Bit timing model: `tq = BRP / f_clock`,
  `bitrate = 1 / ((1 + TSEG1 + TSEG2) * tq)`,
  `sample point = (1 + TSEG1) / (1 + TSEG1 + TSEG2)`.
- TSEG search ranges default to values common on Bosch-style controllers;
  adjust `tseg1_max` / `tseg2_max` / `brp_max` for your hardware.

Personal learning project — written to keep CAN-FD timing math handy.
