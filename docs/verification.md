# Verification and acceptance evidence

Run `make test`. The root runner compiles from source, rejects process failures and test diagnostics, checks expected result records and writes CSVs only from successful suites.

| Layer | What is checked | Result |
|---|---|---|
| CPU components | PC increment/hold/branch/wrap/reset; R0 protection; R1-R7; every decoder address | PASS |
| CPU baseline | Four programs on Harvard/shared; registers, output, invalid accesses and exact cycles | 8/8 PASS |
| Cache units/smoke | RAM words/tags, valid/LRU, tag hits, allocations, dirty writeback | PASS |
| Memory | Request latching and exact ready behavior at latency 1/3/6 | PASS |
| Cache traces | Random/locality/conflict; 2,000 operations each, each cache | Zero golden read mismatches |
| New word stress | 786 operations x 3 latencies, each cache; four word offsets, conflicts, writebacks, capacity readback | 2,358/2,358 PASS per cache |
| CPU-cache | 6 programs x 2 caches x latency 1/3/6; per-retirement architectural reference | 36/36 PASS |

A trace operation is presented to both caches. Counts describe workload operations, not the sum of both cache instances. The 6,000 trace operations and 2,358 stress operations are separate suites. Zero mismatches refers to reads checked against a golden memory; it is not an exhaustive proof for all possible input sequences.

The golden CPU interpreter loads program/data files independently, executes the ISA, and compares each retired instruction plus all eight registers, PC, I/O and HALT. It checks invalid-access flags and exact dynamic instruction count. Request/response totals must match and no requests/retirements may occur after HALT. A 10,000-cycle timeout catches deadlock.

Directed workload details:

- prog1: load 5 and 7, add and store 12.
- prog2: output 5, ignore an unmapped write and flag the error.
- prog3: no data access, baseline control case.
- prog4: subtraction, immediates, a countdown loop and branch/jump; 23 retired instructions.
- prog5: store then load, taken BEQ, output readback, invalid read/write and R0 protection; 12 retired instructions.
- prog6: overwrite a future instruction with HALT and jump to it; 4 retired instructions.

Original Harvard/shared benches cover programs 1-4. Programs 5-6 are cached-CPU directed tests. No claim is made that reset-during-dirty-writeback or all arbitrary geometry configurations are verified.

The GitHub workflow also checks that measured CSVs regenerate without differences and injects a compiler failure (`IVERILOG=false`) to ensure failures propagate. Structural synthesis logs are separate from simulation evidence and are not timing closure reports.

## Structural synthesis

All five top modules passed Yosys 0.52 hierarchy/proc/opt/check/stat in GitHub CI. The complete raw logs and scripts are committed under results/synthesis/. The two-way hierarchy reports four data/tag memories totaling 19,200 bits; these are generic RTL storage statistics, not technology-mapped FPGA LUT/BRAM counts. No place-and-route frequency or power claim is made.
