from __future__ import annotations
import argparse, datetime as dt, json, re, urllib.error, urllib.parse, urllib.request
from pathlib import Path
from html.parser import HTMLParser

UA='year4-proj-reference-automation/1.0'
DOI_RE=re.compile(r'(?:https?://(?:dx\.)?doi.org/|\bdoi:\s*|\b)(10\.\d{4,9}/[-._;()/:A-Z0-9]+)',re.I)
URL_RE=re.compile(r'https?://[^\s<>]+',re.I)

class MetaParser(HTMLParser):
    def __init__(self): super().__init__(); self.meta={}; self.title=[]; self.intitle=False
    def handle_starttag(self,tag,attrs):
        d={k.lower():(v or '') for k,v in attrs}
        if tag.lower()=='meta':
            k=d.get('name') or d.get('property'); v=d.get('content')
            if k and v: self.meta[k.lower()]=v.strip()
        elif tag.lower()=='title': self.intitle=True
    def handle_endtag(self,tag):
        if tag.lower()=='title': self.intitle=False
    def handle_data(self,data):
        if self.intitle: self.title.append(data)

def request(url):
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json,text/html;q=0.9,*/*;q=0.1'})
    with urllib.request.urlopen(req,timeout=15) as r: return r.read()

def year(v):
    if isinstance(v,dict):
        p=v.get('date-parts'); return str(p[0][0]) if p and p[0] else None
    m=re.search(r'\b(?:19|20)\d{2}\b',str(v or '')); return m.group(0) if m else None

def authors(items):
    out=[]
    for a in items or []:
        n=(' '.join(x for x in (a.get('given'),a.get('family')) if x)).strip() if isinstance(a,dict) else ''
        if n: out.append(n)
    return out

def doi_lookup(doi):
    for api in ('https://api.crossref.org/works/','https://api.datacite.org/dois/'):
        try:
            d=json.loads(request(api+urllib.parse.quote(doi,safe='')))
            if 'message' in d: m=d['message']; return dict(title=(m.get('title') or [None])[0],authors=authors(m.get('author')),publisher=m.get('publisher'),container=(m.get('container-title') or [None])[0],year=year(m.get('published-print') or m.get('published-online') or m.get('issued')),doi=(m.get('DOI') or doi).lower(),url=m.get('URL') or 'https://doi.org/'+doi,source_type='scholarly_work')
            a=d['data']['attributes']; cr=a.get('creators',[]); aa=[]
            for x in cr:
                n=x.get('name') or ' '.join(y for y in (x.get('givenName'),x.get('familyName')) if y)
                if n: aa.append(n)
            return dict(title=(a.get('titles') or [{}])[0].get('title'),authors=aa,publisher=a.get('publisher'),container=None,year=str(a.get('publicationYear')) if a.get('publicationYear') else year(a.get('dates')),doi=(a.get('doi') or doi).lower(),url=a.get('url') or 'https://doi.org/'+doi,source_type='doi_resource')
        except (urllib.error.URLError,TimeoutError,ValueError,KeyError,IndexError): pass
    return None

def url_lookup(url):
    try:
        p=MetaParser(); p.feed(request(url).decode('utf-8','replace')); m=p.meta
        doi=m.get('citation_doi') or m.get('dc.identifier'); doi=re.sub(r'^https?://doi.org/','',doi,flags=re.I).lower() if doi else None
        return dict(title=m.get('citation_title') or m.get('dc.title') or m.get('og:title') or ''.join(p.title).strip() or None,authors=[m[k] for k in ('citation_author','dc.creator','author') if k in m],publisher=m.get('citation_publisher') or m.get('dc.publisher'),container=None,year=year(m.get('citation_date') or m.get('dc.date') or m.get('date')),doi=doi,url=url,source_type='web')
    except (urllib.error.URLError,TimeoutError,ValueError): return None

def entries(text):
    out=[]
    for x in re.split(r'\n\s*\n',text):
        x=x.strip()
        if not x or x.startswith('#') or x.startswith('<!--') or x.startswith('Paste one source entry'): continue
        out.append(x)
    return out
def identify(s):
    m=DOI_RE.search(s)
    if m:return 'doi',m.group(1).rstrip('.,;)')
    m=URL_RE.search(s)
    if m:return 'url',m.group(0).rstrip('.,;)')
    return 'citation',s

def front(path):
    t=path.read_text(encoding='utf8'); out={}
    if t.startswith('---\n') and '\n---' in t[4:]:
        for line in t[4:t.find('\n---',4)].splitlines():
            if ':' in line:
                k,v=line.split(':',1); out[k.strip()]=v.strip().strip('"')
    return out

def normdoi(x): return re.sub(r'^https?://(dx\.)?doi.org/','',x.strip(),flags=re.I).lower() if x else None
def normurl(x): return re.sub(r'/$', '', re.sub(r'#.*$','',re.sub(r'^http://','https://',x.strip().lower()))) if x else None

def duplicate(meta,ref):
    for p in ref.glob('REF-*.md'):
        f=front(p)
        if meta.get('doi') and normdoi(f.get('doi'))==normdoi(meta['doi']): return p,'doi'
        if meta.get('url') and normurl(f.get('url'))==normurl(meta['url']): return p,'url'
        if meta.get('title') and meta['title'].strip().casefold()==f.get('title','').strip().casefold(): return p,'title'

def next_id(ref):
    n=[int(m.group(1)) for p in ref.glob('REF-*.md') if (m:=re.fullmatch(r'REF-(\d+)',p.stem))]; return f'REF-{max(n,default=0)+1:03d}'
def q(v): return 'null' if v is None else '"'+str(v).replace('\\','\\\\').replace('"','\\"')+'"'
def citation(m,date):
    x=[]
    if m.get('authors'): x.append(', '.join(m['authors']))
    x.append('"'+(m.get('title') or '[Title not established]')+',"')
    for k in ('container','publisher','year'):
        if m.get(k): x.append(m[k])
    x.append('doi: '+m['doi']+'.' if m.get('doi') else '[Online]. Available: '+m['url']+', Accessed: '+date+'.')
    return ' '.join(x)
def record(rid,m,date):
    return f'''---\nid: {rid}\ntype: reference\ntitle: {q(m.get('title') or '[Not established]')}\nstatus: Unverified\ncreated: {date}\nupdated: {date}\nsource_type: {m.get('source_type','web')}\ndoi: {q(m.get('doi'))}\nurl: {q(m.get('url'))}\ndate_accessed: {date}\n---\n\n## IEEE Citation\n\n{citation(m,date)}\n\n## Summary\n\n[Not assessed by Reference Automation V1]\n\n## What This Source Establishes\n\n[Not assessed by Reference Automation V1]\n\n## Limitations\n\n[Not assessed by Reference Automation V1]\n\n## Relevant Sections\n\n[Not assessed by Reference Automation V1]\n\n## Used By\n\n[No relationships established by bibliographic processing]\n\n## Verification Status\n\nBibliographic metadata retrieved or parsed by Reference Automation V1. Research claims, limitations, and interpretation have not been assessed.\n\n## Metadata\n\n- Authors: {('; '.join(m.get('authors',[])) or '[Not established]')}\n- Publisher: {m.get('publisher') or '[Not established]'}\n- Container: {m.get('container') or '[Not established]'}\n- Year: {m.get('year') or '[Not established]'}\n'''
def valid_text(t): return all(h in t for h in ('## IEEE Citation','## Summary','## What This Source Establishes','## Limitations','## Relevant Sections','## Used By','## Verification Status'))
def index(ref):
    rows=['# References Index','','This index is maintained by Reference Automation V1.','','| ID | Title | Type | DOI | URL | Status |','|---|---|---|---|---|---|']
    for p in sorted(ref.glob('REF-*.md')):
        f=front(p); rows.append('| '+' | '.join(f.get(k,'') for k in ('id','title','type','doi','url','status'))+' |')
    (ref/'INDEX.md').write_text('\n'.join(rows)+'\n',encoding='utf8')

def process(root,dry=False):
    doc=root/'Documentation-repo' if (root/'Documentation-repo').is_dir() else root; inbox=doc/'references/inbox/REFERENCES.md'; ref=doc/'references'; text=inbox.read_text(encoding='utf8') if inbox.exists() else ''
    rem=[]; created=[]; date=dt.date.today().isoformat()
    for e in entries(text):
        kind,val=identify(e); m=doi_lookup(val) if kind=='doi' else url_lookup(val) if kind=='url' else None
        if not m: rem.append(e); print('UNRESOLVED:',e[:100]); continue
        d=duplicate(m,ref)
        if d: print('DUPLICATE:',d[0].name,d[1]); continue
        rid=next_id(ref); t=record(rid,m,date)
        if not valid_text(t): raise RuntimeError('invalid generated record '+rid)
        if not dry: (ref/(rid+'.md')).write_text(t,encoding='utf8')
        created.append(rid); print('CREATED:',rid)
    if not dry:
        index(ref)
        archive=ref/'archive'; archive.mkdir(exist_ok=True)
        processed=[e for e in entries(text) if e not in rem]
        if processed:
            stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            (archive/(stamp+'-inbox.md')).write_text('\n\n'.join(processed)+'\n',encoding='utf8')
        remaining='\n\n'.join(rem)
        inbox.write_text('# Reference Inbox\n\nPaste one source entry per block. Blank lines separate entries.\n\n<!-- Reference Automation V1 processes this file automatically. -->\n\n'+remaining+('\n' if remaining else ''),encoding='utf8')
    print(f'Created: {len(created)}; unresolved: {len(rem)}')

def main():
    a=argparse.ArgumentParser(); a.add_argument('--root',type=Path,default=Path.cwd()); a.add_argument('--dry-run',action='store_true'); x=a.parse_args(); process(x.root,x.dry_run)
if __name__=='__main__': main()
