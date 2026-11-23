#!/usr/bin/env python3
"""Live demonstration using actual verification and generated measurements."""
import csv,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
print('MCA CacheLab | live cache demonstration',flush=True)
print('1. Verify cache data integrity, replacement and dirty writeback.',flush=True)
subprocess.run([sys.executable,str(root/'scripts/verify.py'),'cache'],cwd=root,check=True)
print('\n2. Compare identical 2,000-access workloads.\n')
with (root/'results/cache.csv').open() as f:rows=list(csv.DictReader(f))
for trace in ['random','locality','conflict']:
 print(trace.upper())
 for row in rows:
  if row['trace']==trace:
   print(f'  {row["architecture"]}: hits={row["hits"]}/{row["accesses"]}; hit rate={100*int(row["hits"])/int(row["accesses"]):.2f}%; cycles/access={int(row["cycles"])/int(row["accesses"]):.2f}')
print('\n3. Conflict explanation: blocks 0 and 0x800 repeatedly collide in direct mapped,')
print('   while two ways hold both after two cold misses.')
print('\n4. Optional CPU demonstration: make test-integration')
print('   Report: docs/final_report.pdf | Design: docs/architecture.md')
