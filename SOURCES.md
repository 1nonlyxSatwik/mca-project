# Source provenance and attribution

This repository integrates two existing educational Verilog projects with a new CPU/cache bridge, architectural reference tests, reproducible result generation and final documentation.

| Component | Upstream | Imported revision |
|---|---|---|
| 16-bit CPU, Harvard/shared systems, programs 1-4 | https://github.com/Ashar-Asif-Shaikh/MCA-project | `2538dab238d4c71810c60b9eeecb4800984ec213` |
| Direct-mapped and 2-way LRU caches, submodules, cache tests/traces | https://github.com/Ritxshhh/2-Way_Set_Associative_Cache_with_LRU | `578a9781b88e9aa3fbf29caea0b4270236f9fcc2` |

CPU source author: Ashar Asif Shaikh. Cache upstream credits Punit Yadav, Yash Kumar, Dhruv Kumar, Ritesh and Parul Nehra; see `cache/README.md` for their original roles and profile links.

Integration and final repository maintained by Aditya Ranjan (`kvianAR`). New integration files are in `integration/`; new verification/report tooling is in `scripts/`; programs 5-6 and `tb/tb_components.v` are integration additions. Existing CPU tests gain failure exit codes; cache trace verification now rejects setup errors, empty traces and mismatches.

Original descriptions and reports are retained as historical source material. The root README, `docs/final_report.pdf`, and `results/` describe this combined implementation. Upstream synthesis figures are historical and are not adopted as measurements of this repository.

Neither imported revision includes a LICENSE file. This integration does not assert a new blanket license or change ownership of upstream contributions. Original source links and credits are retained. The upstream demo video remains linked rather than duplicating its large binary.
