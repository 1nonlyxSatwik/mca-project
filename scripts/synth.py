#!/usr/bin/env python3
"""Structural synthesis only; never manufacture FPGA timing or utilization."""
from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'results/synthesis';DEST.mkdir(parents=True,exist_ok=True)
tool=os.environ.get('YOSYS') or shutil.which('yosys') or str(ROOT/'sim/tools/bin/yowasp-yosys')
if not Path(tool).exists():raise SystemExit('Install yosys, or set YOSYS to a yowasp-yosys executable.')
env=dict(os.environ,YOWASP_CACHE_DIR=str(ROOT/'sim/toolcache'))
version=subprocess.check_output([tool,'-V'],text=True,env=env).strip()
rows=[]
for top,paths in [('harvard_top',['rtl/*.v']),('shared_top',['rtl/*.v']),('direct_mapped_cache',['cache/rtl/*.v']),('cache_2way_top',['cache/rtl/*.v']),('cpu_cached_top',['rtl/*.v','cache/rtl/*.v','integration/rtl/*.v'])]:
 sources=' '.join(str(p.relative_to(ROOT)) for pattern in paths for p in sorted(ROOT.glob(pattern)) if p.name != 'mem_model.v')
 script=f'read_verilog {sources}; hierarchy -check -top {top}; proc; opt; check -assert; stat;'
 script_path=DEST/f'{top}.ys';script_path.write_text(script+'\n')
 result=subprocess.run([tool,'-s',str(script_path)],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,timeout=180)
 (DEST/f'{top}.log').write_text(result.stdout)
 if result.returncode:raise RuntimeError(result.stdout)
 rows.append({'top':top,'status':'PASS','tool':version,'flow':'hierarchy/proc/opt/check/stat'})
 print(f'{top}: structural synthesis PASS',flush=True)
(DEST/'summary.json').write_text(json.dumps(rows,indent=2)+'\n')
