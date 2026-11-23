#!/usr/bin/env python3
"""Generate cache-first report and figures from measured CSV files."""
from pathlib import Path
import csv,json,os
os.environ.setdefault("MPLCONFIGDIR",str(Path(__file__).resolve().parents[1]/"sim/matplotlib"))
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
ROOT=Path(__file__).resolve().parents[1];DOC=ROOT/'docs';RES=ROOT/'results'
DOC.mkdir(exist_ok=True)
def read(name,count):
 with (RES/f'{name}.csv').open() as f: rows=list(csv.DictReader(f))
 if len(rows)!=count:raise SystemExit(f'Run make test first: expected {count} {name} records')
 return rows
cpu=read('cpu',8);cache=read('cache',6);integration=read('integration',36)
blue='#2563eb';green='#0d9488';ink='#15253b'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(8,3.3))
traces=['random','locality','conflict'];x=range(3)
for idx,(arch,label,color) in enumerate([('direct_mapped','Direct mapped',blue),('two_way_lru','2-way LRU',green)]):
 rates=[100*int(next(r for r in cache if r['trace']==t and r['architecture']==arch)['hits'])/2000 for t in traces]
 bars=ax.bar([v+(idx-.5)*.34 for v in x],rates,.34,label=label,color=color)
 ax.bar_label(bars,fmt='%.2f%%',padding=3,fontsize=9)
ax.set_xticks(list(x),['Random','Locality','Conflict']);ax.set_ylabel('Hit rate (%)');ax.set_ylim(0,114);ax.legend(frameon=False);fig.tight_layout();fig.savefig(DOC/'cache_hit_rates.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.3))
for idx,(arch,label,color) in enumerate([('direct_mapped','Direct mapped',blue),('two_way_lru','2-way LRU',green)]):
 values=[int(next(r for r in cache if r['trace']==t and r['architecture']==arch)['cycles'])/2000 for t in traces]
 bars=ax.bar([v+(idx-.5)*.34 for v in x],values,.34,label=label,color=color);ax.bar_label(bars,fmt='%.2f',padding=3)
ax.set_xticks(list(x),['Random','Locality','Conflict']);ax.set_ylabel('Measured cycles / access');ax.set_ylim(0,13);ax.legend(frameon=False);fig.tight_layout();fig.savefig(DOC/'cache_access_cycles.png',dpi=180);plt.close(fig)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleMCA',fontName='Helvetica-Bold',fontSize=28,leading=33,textColor=colors.HexColor(ink),spaceAfter=18))
styles['Heading1'].textColor=colors.HexColor(blue);styles['Heading1'].spaceAfter=14
styles['Heading2'].textColor=colors.HexColor(ink)
styles['BodyText'].fontSize=10;styles['BodyText'].leading=15;styles['BodyText'].spaceAfter=9
story=[]
def p(s,style='BodyText'):story.append(Paragraph(s,styles[style]))
def title(s):p(s,'Heading1')
def table(rows,widths=None):
 data=[[Paragraph(str(c),styles['BodyText']) for c in row] for row in rows]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8effa')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.8,colors.HexColor(blue)),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d8e0eb')),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t);story.append(Spacer(1,12))
def page():story.append(PageBreak())
p('MCA CacheLab','TitleMCA')
p('2-Way Set-Associative Cache with LRU Replacement','Heading1')
p('Direct-mapped baseline comparison, write-back verification and 16-bit CPU integration.','Heading2')
p('Final integrated repository | Maintainer: Aditya Ranjan (kvianAR)')
p('Abstract','Heading2')
p('This project implements and verifies a 2 KB, two-way set-associative cache with least-recently-used replacement. An equal-capacity direct-mapped cache is the baseline. Both process identical memory traces against an independent golden model. Additional mixed-word tests exercise dirty writeback at three memory latencies. A new bridge connects the original 16-bit CPU to either cache and checks every retired instruction against a software-style architectural interpreter.')
table([['Parameter','Direct mapped','2-way LRU'],['Address / data','32 / 32 bits','32 / 32 bits'],['Block size','16 bytes (4 words)','16 bytes (4 words)'],['Data capacity','2 KB','2 KB'],['Organization','128 lines','64 sets x 2 ways'],['Tag / index / offset','21 / 7 / 4 bits','22 / 6 / 4 bits'],['Writes','Write-back, write-allocate','Write-back, write-allocate']],[150,180,180])
p('The cache study is the primary deliverable. Harvard/shared-memory CPU comparison and CPU-cache integration are supporting experiments. Repository phase labels are organizational; no external course rubric is assumed.')
page();title('1. Architecture and control')
p('The CPU-side interface accepts a word-aligned address, read/write request and 32-bit store data. A blocking controller latches the request. Both ways are indexed in parallel; valid tags determine hit and selected way. A hit returns the selected 32-bit word or updates it and sets the dirty bit.')
p('2-way address decomposition','Heading2')
p('tag = address[31:10]; set = address[9:4]; word = address[3:2]. Bits [1:0] must be zero. Byte writes and unaligned accesses are outside the interface contract.')
table([['State','Responsibility'],['IDLE','Latch request address, direction and data.'],['TAG_CHECK','Compare both valid tags.'],['HIT','Return/update word, assert ready, update LRU.'],['SELECT_VICTIM','Select the way indicated by the per-set LRU state.'],['WRITE_BACK','If valid and dirty, write the old 128-bit block to memory.'],['FETCH_BLOCK','Read the requested 128-bit block and wait for memory ready.'],['FILL_WAY','Install block and tag, set valid, update LRU; retry request.']],[130,380])
p('LRU: one bit per set identifies the next victim. Touching way W sets the bit to 1-W. Reset invalidates both ways; under the normal fill/touch protocol, cold allocation fills the two ways before eviction. Dirty data is written back before replacement. Cache reset invalidates state and does not flush dirty lines; persistent warm-reset semantics are not provided.')
p('Backing memory supports 64 KB of byte addresses with configurable latency. The interface is blocking: no second outstanding request, prefetcher, coherent multicore protocol or nonblocking miss queue is implemented.')
page();title('2. Measured cache performance')
rows=[['Trace','DM hits','2-way hits','DM cyc/access','2-way cyc/access']]
md=['# Measured results\n','Results generated from results/*.csv by scripts/report.py.\n','## Cache benchmark\n','| Trace | DM hit rate | 2-way hit rate | DM cycles/access | 2-way cycles/access |\n|---|---:|---:|---:|---:|']
for t in traces:
 d=next(r for r in cache if r['trace']==t and r['architecture']=='direct_mapped');s=next(r for r in cache if r['trace']==t and r['architecture']=='two_way_lru')
 dh=100*int(d['hits'])/2000;sh=100*int(s['hits'])/2000;dc=int(d['cycles'])/2000;sc=int(s['cycles'])/2000
 rows.append([t,f'{dh:.2f}%',f'{sh:.2f}%',f'{dc:.2f}',f'{sc:.2f}']);md.append(f'| {t} | {dh:.2f}% | {sh:.2f}% | {dc:.2f} | {sc:.2f} |')
table(rows,[80,100,110,110,110]);story.append(Image(str(DOC/'cache_hit_rates.png'),width=510,height=210))
p('Three workloads contain 2,000 accesses each. The conflict trace alternates blocks 0x00000000 and 0x00000800. They evict each other in the direct-mapped cache; two ways retain both after two compulsory misses. Random accesses exceed cache capacity, so associativity offers no hit-rate advantage. Locality reuses a small working set with occasional random references.')
p('Cycle measurements use the inherited trace driver: request acceptance and inter-request idle gaps are excluded. The controllers differ in ready/output timing; cycles/access differences include those implementation choices. These measurements do not isolate associativity alone and are not maximum-clock-frequency claims.')
page();title('3. Verification evidence')
table([['Layer','Evidence'],['Cache unit and smoke tests','Way RAM/tag RAM, valid bits, LRU, comparators, baseline and two-way controllers.'],['Memory latency checks','Memory request latching and ready behavior at 1, 3 and 6 cycles.'],['Golden-model traces','6,000 operations presented to each cache; every read compared to an independent 64 KB model. Zero mismatches.'],['New mixed-word stress','786 operations per latency, 2,358 total per cache: all four word offsets, read-after-write, three conflicting tags, dirty eviction and capacity-pressure readback.'],['CPU baseline','8 configurations: four programs on Harvard and shared-memory systems.'],['CPU components','PC reset/enable/branch/wrap, R0 write protection, R1-R7 ports and all 64 decoded addresses.'],['New CPU-cache integration','36 configurations: 6 programs x 2 cache variants x memory latency 1/3/6. Every retirement checks instruction, eight registers, PC, HALT, I/O and error flag.']],[145,365])
p('Programs 5 and 6 are new directed tests. Program 5 verifies store/load readback, a taken branch, output-port readback, invalid read/write handling and R0 protection. Program 6 overwrites a future instruction with HALT and branches to it, demonstrating unified-cache instruction/data consistency.')
p('The runner rejects compiler/simulator errors, missing PASS records, incomplete trace logs, empty traces, golden-model mismatches and timeouts. Original CPU benches also terminate with a failing exit status on mismatches. Generated VCDs and logs are kept under ignored build directories; measured CSVs are committed.')
page();title('4. CPU integration and baseline')
p('The existing CPU ISA is unchanged: HALT, ADD, LOAD, STORE, SUB, ADDI, BEQ and JMP. The new unified-cache bridge sequences instruction fetch, optional data access and architectural commit. CPU state is stalled while cache requests are outstanding. A STORE request is decoded from the saved instruction rather than the stall-gated CPU write output, avoiding a combinational dependency.')
p('Each 16-bit CPU word occupies the low half of a 32-bit cache word: cache byte address = CPU word address x 4. Output address 0x3F and invalid addresses 0x30-0x3E bypass the cache. The backing model contains 64 such slots. Stored values may remain dirty in cache at HALT; backing RAM is not claimed to be flushed.')
rows=[['Program','Harvard cycles','Shared cycles','Data operations']]
for n in range(1,5):
 h=next(r for r in cpu if r['architecture']=='harvard' and r['program']==f'prog{n}');s=next(r for r in cpu if r['architecture']=='shared' and r['program']==f'prog{n}')
 rows.append([f'prog{n}',h['cycles'],s['cycles'],h['memory_ops']])
table(rows,[110,130,130,140]);p('For the original idealized asynchronous-memory baseline: shared cycles = Harvard cycles + executed LOAD/STORE count. HALT is counted. This equation does not apply to the new multicycle cached bridge.')
rows=[['Program','DM CPU cycles','2-way CPU cycles','Retired instructions']]
for n in range(1,7):
 d=next(r for r in integration if r['architecture']=='direct_mapped' and r['program']==f'prog{n}' and r['latency']=='3');s=next(r for r in integration if r['architecture']=='two_way_lru' and r['program']==f'prog{n}' and r['latency']=='3')
 rows.append([f'prog{n}',d['cycles'],s['cycles'],d['retired']])
table(rows,[110,130,130,140]);p('The 64-word CPU address space is much smaller than a 2 KB cache. These CPU programs validate connectivity and architectural correctness, not an associativity speedup. Large cache-only traces exercise actual conflicts and replacement.')
page();title('5. Reproduction, provenance and limits')
p('Run make test from the repository root with Python 3.9+, GNU Make and Icarus Verilog installed. Run make report after installing requirements-report.txt. Measured CSVs, plots and this PDF are reproducible. make synth invokes Yosys hierarchy checking, process lowering, optimization, structural checking and statistics for five top modules.')
summary=RES/'synthesis/summary.json'
if summary.exists():
 synth=json.loads(summary.read_text());p(f'Structural synthesis: {len(synth)} top modules PASS using {synth[0]["tool"]}. See results/synthesis for raw logs and scripts. This is RTL structural validation, not FPGA placement/routing or timing closure.')
else:p('Structural synthesis scripts are supplied; this environment has not produced a successful structural synthesis run. No new FPGA utilization, timing or Fmax measurements are claimed.')
p('No validated final FPGA place-and-route, physical board demo, power measurement or Fmax is included. Upstream Vivado figures are retained only as historical material; their two-way storage accounting is explicitly marked as needing a rerun. They are not adopted as combined-project results.')
p('Source provenance','Heading2')
p('CPU baseline: Ashar-Asif-Shaikh/MCA-project, revision 2538dab238d4c71810c60b9eeecb4800984ec213. Cache baseline: Ritxshhh/2-Way_Set_Associative_Cache_with_LRU, revision 578a9781b88e9aa3fbf29caea0b4270236f9fcc2. Full links, upstream author credits and integration changes are recorded in SOURCES.md. Neither imported snapshot contains a license file; original ownership is preserved.')
p('New work includes CPU/cache width adaptation, latency-controlled CPU line memory, per-retirement architectural reference verification, mixed-word cache stress tests, reproducible validation/report tooling, consolidated results, documentation and continuous integration. The project is maintained by Aditya Ranjan (kvianAR).')
p('Submission package','Heading2')
p('Primary: cache RTL, direct-mapped baseline, cache verification, performance tables, figures and final report. Supporting: CPU baseline, cached CPU experiments, implementation notes and viva guide. Original reports are historical references. Official Phase 2 compliance must be assessed against the course requirement sheet, which was not supplied.')
def footer(canvas,doc):
 canvas.setStrokeColor(colors.HexColor('#d8e0eb'));canvas.line(42,39,553,39);canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#607086'));canvas.drawString(42,25,'MCA CacheLab | Verified cache study and CPU integration');canvas.drawRightString(553,25,str(doc.page))
SimpleDocTemplate(str(DOC/'final_report.pdf'),pagesize=(595,842),rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=51,title='MCA CacheLab - Final Technical Report',author='Aditya Ranjan (kvianAR)').build(story,onFirstPage=footer,onLaterPages=footer)
md+=['\n## CPU baseline\n','| Program | Harvard cycles | Shared cycles |\n|---|---:|---:|']
for n in range(1,5):
 h=next(r for r in cpu if r['architecture']=='harvard' and r['program']==f'prog{n}');s=next(r for r in cpu if r['architecture']=='shared' and r['program']==f'prog{n}');md.append(f'| prog{n} | {h["cycles"]} | {s["cycles"]} |')
md+=['\n## Verification summary\n','- 8 baseline CPU configurations PASS.','- CPU component checks PASS.','- 6,000 trace operations per cache; zero read mismatches.','- 2,358 additional mixed-word operations per cache across memory latencies 1/3/6.','- 36 CPU-cache configurations PASS; every retired architectural state checked.','\nRaw CSVs are in results/. Timing is simulation timing; no final FPGA Fmax claim is made.']
(DOC/'results.md').write_text('\n'.join(md)+'\n')
print('Generated docs/final_report.pdf, docs/results.md and cache performance plots')
