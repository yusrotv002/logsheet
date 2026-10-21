import csv, re, glob, os, collections, json
SRC="/home/claude/dash/hari"; OUT="/home/claude/dash/kat2"
SLOTS=[f"j{(h*30)//60:02d}{(h*30)%60:02d}" for h in range(1,49)]
SUM_EL={"P","Q","I","S"}
EXCL=("BSBAR","TRF","KTRF","KTT","SST","KUNIT","5IBT","IBT","UNIT")
def kategori(r):
    gi,kv,b=r['gi'],r['kv'],r['peralatan']
    if not re.fullmatch(r'[\d.]+',kv): return None
    if re.fullmatch(r'(5IBT7|TRF57)-\d+',b): return 'IBT500'
    if re.fullmatch(r'TRF54-\d+',b): return 'IBT150'
    if re.match(r'K?TRF',b): return 'TRAFO'
    if kv in('150','70') and not b.startswith(EXCL): return 'SUTT'+kv
    return None
def fmt(v):
    if v is None: return ""
    s=f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in("-0","") else s
stat=collections.Counter()
for f in sorted(glob.glob(f"{SRC}/mapping_2026-10-0[1-7].csv")):
    rows=list(csv.DictReader(open(f)))
    groups=collections.defaultdict(lambda: collections.defaultdict(list))  # (kat,gi,kv,label_base) -> el -> [(unit,row)]
    trf=set((r['gi'],r['peralatan']) for r in rows if r['peralatan'].startswith('TRF'))
    out=[]
    for r in rows:
        # IBT-4 0CBAT7: P only exists in a "JCC-KWH2" row with the opposite sign
        if r['gi']=='JCC-KWH2' and r['kv']=='0CBAT7' and r['peralatan']=='5IBT7-4':
            r=dict(r, gi='0CBAT7', kv='150')
            for s_ in SLOTS:
                if r[s_]!='': r[s_]=fmt(-float(r[s_]))
        k=kategori(r)
        if not k: continue
        b=r['peralatan']
        if k=='TRAFO':
            if b.startswith('KTRF') and (r['gi'],b[1:]) in trf: continue
            out.append([k,r['gi'],r['kv'],b,b,r['elemen']]+[r[s] for s in SLOTS]); continue
        m=re.fullmatch(r'(.+?)-(\d+)',b)
        base,num=(m.group(1),m.group(2)) if m else (b,None)
        if k.startswith('IBT'):
            base='IBT'
            if num: base='IBT#'+num  # IBT units shown individually (hendrik, 2026-10-21 08:11)
        groups[(k,r['gi'],r['kv'],base)][r['elemen']].append((num,b,r))
    for (k,gi,kv,base),els in groups.items():
        units=sorted({n for e in els.values() for n,_,_ in e if n}, key=int)
        nama=f"{base.split('#')[0]}-{','.join(units)}" if units else base
        for el,lst in els.items():
            if el not in SUM_EL: continue
            ang=" + ".join(sorted(b for _,b,_ in lst))
            vals=[]
            for s in SLOTS:
                xs=[r[s] for _,_,r in lst]
                sign=-1 if (k=='IBT500' and el in('P','Q') and gi not in('0CBAT7','2MRTW5')) else 1
                vals.append("" if any(x=="" for x in xs) else fmt(sign*sum(float(x) for x in xs)))
            out.append([k,gi,kv,nama,ang,el]+vals)
    name=os.path.basename(f).replace('mapping_','kategori_')
    with open(f"{OUT}/{name}","w") as fh:
        w=csv.writer(fh,lineterminator="\n"); w.writerow(["kategori","gi","kv","nama","anggota","elemen"]+SLOTS); w.writerows(out)
    if f.endswith('10-07.csv'):
        for o in out: stat[o[0]]+=1
        ex=[o[:6] for o in out if o[0]!='TRAFO']
print(stat)
import random; random.seed(1)
for o in ex:
    if o[1]=='2SRGI4': print(o)
