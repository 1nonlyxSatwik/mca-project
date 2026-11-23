# Measured results

Results generated from results/*.csv by scripts/report.py.

## Cache benchmark

| Trace | DM hit rate | 2-way hit rate | DM cycles/access | 2-way cycles/access |
|---|---:|---:|---:|---:|
| random | 3.35% | 3.00% | 10.83 | 9.69 |
| locality | 88.35% | 89.40% | 3.06 | 1.90 |
| conflict | 0.00% | 99.90% | 10.00 | 1.01 |

## CPU baseline

| Program | Harvard cycles | Shared cycles |
|---|---:|---:|
| prog1 | 5 | 8 |
| prog2 | 4 | 7 |
| prog3 | 4 | 4 |
| prog4 | 23 | 27 |

## Verification summary

- 8 baseline CPU configurations PASS.
- CPU component checks PASS.
- 6,000 trace operations per cache; zero read mismatches.
- 2,358 additional mixed-word operations per cache across memory latencies 1/3/6.
- 36 CPU-cache configurations PASS; every retired architectural state checked.

Raw CSVs are in results/. Timing is simulation timing; no final FPGA Fmax claim is made.
