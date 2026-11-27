# Submission checklist

Primary artifact: **MCA CacheLab - 2-Way Set-Associative Cache with LRU Replacement**.

- Cache RTL and equal-capacity direct-mapped baseline: `cache/rtl/`.
- Self-checking cache tests and deterministic trace workloads: `cache/tb/`, `cache/sim/`.
- New mixed-word/writeback stress tests: `cache/tb/tb_cache_word_stress.v`.
- Reproducible measurements: `results/cache.csv`, `docs/results.md`, cache plots.
- Final report: `docs/final_report.pdf`; editable generator: `scripts/report.py`.
- New CPU integration: `integration/`; original baseline: `rtl/`, `tb/`.
- Simulation/structural-synthesis workflow: `.github/workflows/verify.yml`.
- Source revisions and contributor credits: `SOURCES.md`.
- Viva/demo notes: `docs/viva.md`.

## Team roster and contributions

- **Satwik** (Enrollment: `2401020056`): Direct-mapped baseline, cache data RAM, tag RAM, unit testbenches and CI.
- **Aditya Ranjan** (Enrollment: `2401010035`): 2-way cache controller, LRU replacement, top-level integration and benchmark analysis.
- **Ashar Asif Shaikh** (Enrollment: `2401010110`): Backing memory, CPU-cache bridge, memory-mapped I/O, architectural verification and final report.

Run `make test` before packaging. Source history contains meaningful implementation/testing/documentation commits. Generated VVPs, VCDs, tool environments and transient logs are excluded. Historical reports in cache/report and original_* files are not the final submission report.

The upstream cache demonstration is at https://github.com/Ritxshhh/2-Way_Set_Associative_Cache_with_LRU/blob/main/report/MCA_Phase1.mov . It is an upstream demo, not a newly recorded presentation of this integrated repository. Record the final presentation using docs/viva.md's demo sequence if a new video is required by the course.

No external Phase 2 rubric has been supplied. Cache/CPU completion statements describe the listed implementation and verification only. Physical FPGA deployment and place-and-route timing have not been completed.
