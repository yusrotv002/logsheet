# Per series (kategori, gi, nama, elemen) for P and Q: if the 1-7 Okt total is negative, multiply the whole series by -1.
import csv,glob,collections
files=sorted(glob.glob('/home/claude/dash/kat2/kategori_*.csv'))
tot=collections.defaultdict(float)
data={}
for f in files:
    rows=list(csv.reader(open(f))); data[f]=rows
    for r in rows[1:]:
        if r[5] in('P','Q'): tot[(r[0],r[1],r[3],r[5])]+=sum(float(x) for x in r[6:] if x)
neg={k for k,v in tot.items() if v<0}
cnt=collections.Counter(k[0]+' '+k[3] for k in neg)
print(len(tot),len(neg),cnt)
def fl(x):
    if x=="": return x
    v=-float(x); return ('%.3f'%v).rstrip('0').rstrip('.') if v!=0 else '0'
for f,rows in data.items():
    for r in rows[1:]:
        if (r[0],r[1],r[3],r[5]) in neg: r[6:]=[fl(x) for x in r[6:]]
    w=csv.writer(open(f,'w'),lineterminator="\n"); w.writerows(rows)
# mixed-sign check after flip
mix=0
for f,rows in data.items():
    for r in rows[1:]:
        if r[5] in('P','Q'):
            v=[float(x) for x in r[6:] if x]
            if v and min(v)<0: mix+=1
print('baris masih ada nilai minus (arah aliran berbalik di sebagian jam):',mix)
for r in data[files[-1]][1:]:
    if r[1]=='2SRGI4' and r[0]=='IBT150': v=[float(x) for x in r[6:] if x]; print(r[3],r[5],min(v),max(v))
