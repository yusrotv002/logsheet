import gzip,base64,json,re,glob,os,csv
S='/tmp/claude-0/-home-claude/9436a84a-e5a2-532c-ba01-e61969e1c9cb/scratchpad'
page=open('/home/claude/dash/index.html').read()
style=re.search(r'<style>(.*?)</style>',page,re.S).group(1)
body=re.search(r'</style>(.*?)<script>',page,re.S).group(1)
script=re.search(r'<script>(.*?)</script>',page,re.S).group(1)
d3=open(f'{S}/d3pkg/package/dist/d3.min.js').read()
daftar=list(csv.DictReader(open('/home/claude/dash/okt/daftar_tanggal.csv')))
blobs={}
for r in daftar:
    raw=open(f"/home/claude/dash/kat2/kategori_{r['tanggal']}.csv",'rb').read()
    blobs[r['dataset']]=base64.b64encode(gzip.compress(raw,9)).decode()
tokens='''
:root{--font-anthropic-sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;--font-anthropic-serif:Georgia,"Times New Roman",serif;
--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:12px;--cds-gap-lg:24px;--cds-pad-xs:6px;--cds-pad-sm:10px;--cds-pad-md:14px;--cds-pad-lg:20px;
--cds-radius:8px;--cds-font-size-caption:13px;--cds-font-size-title:30px;--cds-dur-slow:.3s;
--color-bg:#f8f8f6;--color-panel:#fff;--color-fg:#1a1a18;--color-fg-muted:#6b6a65;--color-border-line:#e3e2dc;--color-bad:#c4402f;
--cds-border:#e3e2dc;--cds-surface-popover:#fff;--cds-text-secondary:#6b6a65;--cds-shadow-popover:0 4px 14px rgba(0,0,0,.12);
--cds-chart-axis:#9b9a94;--cds-chart-grid:#ecebe6;--cds-chart-reference:#9b9a94;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--color-bg:#1c1c1a;--color-panel:#262624;--color-fg:#f0efea;--color-fg-muted:#a3a29c;--color-border-line:#3a3936;
--cds-border:#3a3936;--cds-surface-popover:#2e2e2b;--cds-text-secondary:#a3a29c;--cds-shadow-popover:0 4px 14px rgba(0,0,0,.5);--cds-chart-axis:#7a7974;--cds-chart-grid:#33322f;--cds-chart-reference:#7a7974;color-scheme:dark}}
:root[data-theme="dark"]{--color-bg:#1c1c1a;--color-panel:#262624;--color-fg:#f0efea;--color-fg-muted:#a3a29c;--color-border-line:#3a3936;--cds-border:#3a3936;--cds-surface-popover:#2e2e2b;--cds-text-secondary:#a3a29c;--cds-chart-axis:#7a7974;--cds-chart-grid:#33322f;color-scheme:dark}
[hidden]{display:none!important}
body{margin:0;padding:24px 16px;background:var(--color-bg);color:var(--color-fg);font-family:var(--font-anthropic-sans);font-size:15px}
'''
shim='''
(() => {
  const DAFTAR = %s;
  const BLOBS = %s;
  const KEY = 'dashboard-logsheet-params';
  let params = {};
  try { params = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) {}
  const cache = {}, subs = [];
  const parseCSV = (t) => {
    const out = []; let row = [], f = '', q = false;
    for (let i = 0; i < t.length; i++) {
      const c = t[i];
      if (q) { if (c === '"') { if (t[i + 1] === '"') { f += '"'; i++; } else q = false; } else f += c; }
      else if (c === '"') q = true;
      else if (c === ',') { row.push(f); f = ''; }
      else if (c === '\\n') { row.push(f); out.push(row); row = []; f = ''; }
      else if (c !== '\\r') f += c;
    }
    if (f !== '' || row.length) { row.push(f); out.push(row); }
    const h = out.shift();
    return out.map((r) => Object.fromEntries(h.map((k, j) => [k, r[j] ?? ''])));
  };
  const run = () => subs.forEach((fn) => fn());
  const load = async (id) => {
    cache[id] = { status: 'loading' };
    try {
      const bin = Uint8Array.from(atob(BLOBS[id]), (c) => c.charCodeAt(0));
      const txt = await new Response(new Blob([bin]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
      cache[id] = { status: 'ok', data: parseCSV(txt) };
    } catch (e) { cache[id] = { status: 'error', error: String(e) }; }
    run();
  };
  window.dash = {
    colors: ['var(--s1)', 'var(--s2)', 'var(--s3)', 'var(--s4)', 'var(--s5)', 'var(--s6)', 'var(--s7)', 'var(--s8)'],
    params: () => ({ ...params }),
    setParams: (p) => { params = { ...params, ...p }; try { localStorage.setItem(KEY, JSON.stringify(params)); } catch (e) {} run(); },
    data: (id) => {
      if (id === 'daftar_tanggal') return { status: 'ok', data: DAFTAR };
      if (!(id in BLOBS)) return { status: 'error' };
      if (!cache[id]) load(id);
      return cache[id];
    },
    onData: (fn) => { subs.push(fn); queueMicrotask(fn); },
  };
})();
''' % (json.dumps(daftar), json.dumps(blobs))
F=S+'/fonts'
def ff(fam,w,path): return "@font-face{font-family:'%s';font-weight:%d;font-style:normal;font-display:swap;src:url(data:font/woff2;base64,%s) format('woff2')}" % (fam,w,base64.b64encode(open(path,'rb').read()).decode())
FONTS=''.join([ff('Inter',w,f'{F}/i/package/files/inter-latin-{w}-normal.woff2') for w in (400,600,700)]+[ff('Montserrat',800,f'{F}/m/package/files/montserrat-latin-800-normal.woff2')])
html=f'''<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard Logsheet</title>
<style>{FONTS}{style}</style></head>
<body>{body}
<script>{d3}</script>
<script>{shim}</script>
<script>{script}</script>
</body></html>'''
out='/mnt/project-files/dashboard/Dashboard_Logsheet.html'
open(out,'w').write(html); print(os.path.getsize(out))
