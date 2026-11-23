# Viva and demonstration guide

## Opening explanation

Our main project is a 2-way set-associative cache with LRU replacement. We compare it with an equal-capacity direct-mapped cache using identical workloads. We verify reads against a golden memory model, stress dirty writeback, and connect a 16-bit CPU to both variants through a new request/commit bridge.

## Questions and concise answers

1. **Why two ways?** A block can occupy either of two positions in its indexed set, reducing conflicts between blocks mapping to the same set.
2. **Why one LRU bit?** With two ways there are only two choices for the least recently used victim. Accessing way W makes the other way least recent.
3. **Why valid bits?** Reset data/tag contents are not sufficient to determine whether a line contains a fetched block. Valid distinguishes installed lines from empty ones.
4. **Why dirty bits?** A store can update cache without immediately updating memory. Dirty marks lines requiring writeback before eviction.
5. **What is write-allocate?** On a store miss, fetch the line, then apply the store to that line. Later eviction writes it back if dirty.
6. **How is the address split?** For two-way: tag 31:10, set 9:4, word 3:2, alignment 1:0. For direct mapped: tag 31:11 and index 10:4.
7. **Why 2 KB for both?** Equal data capacity controls one major comparison variable. Controllers/coding styles still differ, so cycle and area differences are not purely caused by associativity.
8. **Why the conflict result?** Addresses 0 and 0x800 collide in direct mapped but fit together in two ways. Two cold misses are followed by 1,998 hits in the 2,000-access trace.
9. **Is two-way always better?** No. Random traces exceeding cache capacity have poor reuse; ours has 3.00% hits versus 3.35% for direct mapped.
10. **What new verification did we add?** 2,358 mixed-word stress operations per cache at three memory latencies, plus per-instruction CPU reference checking across 36 configurations.
11. **How does a 16-bit CPU use a 32-bit cache?** Each CPU word occupies the low half of a 32-bit cache slot, addressed at CPU word address times four. I/O bypasses cache.
12. **Why not use CPU d_we to initiate a stalled store?** CPU d_we is disabled while stalled. The bridge decodes the saved instruction, avoiding a circular dependency.
13. **What does synthesis prove?** RTL structural checking/lowering verifies hierarchy and structural consistency. It does not prove functional correctness, physical frequency, power or board operation.
14. **Does HALT flush memory?** No. Updated words can remain dirty in cache; architectural readback is verified, but backing memory need not contain all latest stores.
15. **What is reused and what is new?** Source CPU/cache modules are credited in SOURCES.md. New work is the integration bridge/memory, stronger verification, consolidated results, analysis/report tooling and CI.

## Demo sequence

1. Open README and explain equal cache capacity and write-back/LRU.
2. Run `make test-cache`; show zero mismatches and the measured CSVs.
3. Explain the conflict addresses and inspect LRU/cache FSM.
4. Show cache_hit_rates.png and discuss where associativity helps and where it does not.
5. Run `make test-integration`; explain program 5 readback and program 6 self-modifying code.
6. Open final_report.pdf and the CI results. State physical FPGA timing/board implementation limits accurately.
