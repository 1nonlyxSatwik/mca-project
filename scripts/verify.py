#!/usr/bin/env python3
"""Reproducible verification; fail on tool errors, missing records or test failures."""
import argparse,csv,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'sim'
IV=os.environ.get('IVERILOG','iverilog');VVP=os.environ.get('VVP','vvp')
def run(args,cwd=ROOT):
 r=subprocess.run(list(map(str,args)),cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
 diagnostic=re.sub(r'\b0 FAIL\b','',r.stdout)
 if r.returncode or re.search(r'\b(?:FAIL|FAILED|ERROR|FATAL)\b',diagnostic):raise RuntimeError(f'Command failed: {args}\n{r.stdout}')
 return r.stdout
def cpu(prog=None,architecture=None):
 if not prog and not architecture:
  binary=BUILD/'components.vvp'
  run([IV,'-g2012','-Wall','-s','tb_components','-o',binary,'rtl/program_counter.v','rtl/register_file.v','rtl/address_decoder.v','tb/tb_components.v'])
  log=run([VVP,binary]);(BUILD/'components.log').write_text(log)
  if 'PASS components:' not in log:raise RuntimeError('Missing component verification result')
  print('CPU components: PASS',flush=True)
 rows=[];common=['program_counter','register_file','cpu','address_decoder','rw_control','io_reg']
 for arch in ([architecture] if architecture else ['harvard','shared']):
  extras=['instruction_memory','data_memory','harvard_top'] if arch=='harvard' else ['shared_memory','shared_mem_controller','shared_top']
  for n in ([int(prog[4:])] if prog else range(1,5)):
   out=BUILD/f'{arch}_prog{n}.vvp'
   run([IV,'-g2001','-Wall','-s',f'tb_{arch}',f'-Ptb_{arch}.PROG_NUM={n}','-o',out,*[f'rtl/{m}.v' for m in common+extras],f'tb/tb_{arch}.v'])
   log=run([VVP,'-n',out]);(BUILD/f'{arch}_prog{n}.log').write_text(log)
   m=re.search(r'RESULT (\w+) (prog\d+) PASS (\d+) (\d+)',log)
   if not m:raise RuntimeError('Missing CPU PASS record\n'+log)
   a,p,ops,cycles=m.groups();rows.append(dict(architecture=a,program=p,memory_ops=int(ops),cycles=int(cycles)))
   print(f'{a} {p}: PASS cycles={cycles}',flush=True)
 if not prog and not architecture:
  for n in range(1,5):
   h=next(r for r in rows if r['architecture']=='harvard' and r['program']==f'prog{n}')
   s=next(r for r in rows if r['architecture']=='shared' and r['program']==f'prog{n}')
   if s['cycles']!=h['cycles']+h['memory_ops']:raise RuntimeError('Cycle model mismatch')
 return rows
def cache():
 log=run(['make','test'],ROOT/'cache');(BUILD/'cache_suite.log').write_text(log);rows=[]
 for trace in ['random','locality','conflict']:
  for architecture,filename in [('direct_mapped','direct'),('two_way_lru','2way')]:
   records=[x.split() for x in (ROOT/f'cache/sim/results_{filename}_{trace}.log').read_text().splitlines() if x.strip()]
   if len(records)!=2000:raise RuntimeError('Incomplete trace')
   rows.append(dict(trace=trace,architecture=architecture,accesses=len(records),hits=sum(x[1]=='HIT' for x in records),cycles=sum(int(x[2]) for x in records)))
 if len(re.findall(r'Mismatches:\s+0',log))!=6:raise RuntimeError('Missing golden model confirmation')
 for latency in [1,3,6]:
  binary=BUILD/f'cache_words_{latency}.vvp'
  run([IV,'-g2012','-Wall','-s','tb_cache_word_stress',f'-Ptb_cache_word_stress.LATENCY={latency}','-o',binary,*sorted(ROOT.glob('cache/rtl/*.v')),ROOT/'cache/tb/tb_cache_word_stress.v'])
  stress=run([VVP,binary]);(BUILD/f'cache_words_{latency}.log').write_text(stress)
  if 'PASS cache_word_stress' not in stress:raise RuntimeError('Missing cache stress result')
 print('Cache suite: 6000 trace operations + 2358 mixed-word stress operations PASS',flush=True)
 return rows
def integrated():
 rows=[];sources=[*sorted(ROOT.glob('rtl/*.v')),*sorted(ROOT.glob('cache/rtl/*.v')),*sorted(ROOT.glob('integration/rtl/*.v')),ROOT/'integration/tb/tb_cpu_cached.v']
 for latency in [1,3,6]:
  for kind in [0,1]:
   for n in range(1,7):
    binary=BUILD/f'integrated_{kind}_{n}_{latency}.vvp'
    run([IV,'-g2012','-Wall','-s','tb_cpu_cached',f'-Ptb_cpu_cached.CACHE_KIND={kind}',f'-Ptb_cpu_cached.PROG_NUM={n}',f'-Ptb_cpu_cached.MEM_LATENCY={latency}','-o',binary,*sources])
    log=run([VVP,binary]);(BUILD/f'integrated_{kind}_{n}_{latency}.log').write_text(log)
    m=re.search(r'RESULT integrated (\d+) (prog\d+) latency=(\d+) cycles=(\d+) retired=(\d+) requests=(\d+) PASS',log)
    if not m:raise RuntimeError('Missing integrated PASS record\n'+log)
    _,p,lat,cycles,retired,requests=m.groups()
    rows.append(dict(architecture='direct_mapped' if kind==0 else 'two_way_lru',program=p,latency=int(lat),cycles=int(cycles),retired=int(retired),requests=int(requests)))
 print(f'CPU-cache integration: {len(rows)} configurations PASS (every retirement checked)',flush=True)
 return rows
def save(name,rows):
 dest=ROOT/'results';dest.mkdir(exist_ok=True)
 with (dest/f'{name}.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 p=argparse.ArgumentParser();p.add_argument('suite',choices=['all','cpu','cache','integration']);p.add_argument('--program',choices=['prog1','prog2','prog3','prog4']);p.add_argument('--architecture',choices=['harvard','shared']);a=p.parse_args();BUILD.mkdir(exist_ok=True);results={}
 if a.suite in ['all','cpu']:results['cpu']=cpu(a.program,a.architecture)
 if a.suite in ['all','cache']:results['cache']=cache()
 if a.suite in ['all','integration']:results['integration']=integrated()
 if not a.program and not a.architecture:
  for name,rows in results.items():save(name,rows)
 print('Verification complete: all requested checks PASS')
if __name__=='__main__':main()
