"""Import public Google Sheets or local XLSX catalogs. Never evaluate formulas."""
import argparse,base64,hashlib,json,posixpath,re,sys,urllib.request,urllib.error,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
import openpyxl
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os,tempfile,gzip
from catalog_media import cache_products,identity
ROOT=Path(__file__).resolve().parent.parent
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','d':'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
RID='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
LINK_LABEL=re.compile(r'^(link|buy|shop|product|kaufen|zu usfans|qc|mulebuy|kakobuy|cnfans|weidian|taobao|pikobuy|litbuy|acbuy|usfans|w2c|click|here|purchase|open)',re.I)
def url_ok(v):return isinstance(v,str) and urllib.parse.urlsplit(v).scheme in ('https','http')
def rels(z,path):
 rp=posixpath.join(posixpath.dirname(path),'_rels',posixpath.basename(path)+'.rels')
 if rp not in z.namelist():return {}
 return {r.get('Id'):r.get('Target') if r.get('TargetMode')=='External' else posixpath.normpath(posixpath.join(posixpath.dirname(path),r.get('Target',''))).lstrip('/') for r in ET.fromstring(z.read(rp))}
def embedded_images(z,sheet_path,out):
 result={};tree=ET.fromstring(z.read(sheet_path));rs=rels(z,sheet_path)
 for drawing in tree.findall('m:drawing',NS):
  dp=rs.get(drawing.get(RID+'id'))
  if not dp or dp not in z.namelist():continue
  dr=rels(z,dp)
  for anchor in ET.fromstring(z.read(dp)):
   start=anchor.find('d:from',NS);blip=anchor.find('.//a:blip',NS)
   if start is None or blip is None:continue
   target=dr.get(blip.get(RID+'embed'))
   if target not in z.namelist():continue
   ext=Path(target).suffix.lower()
   if ext not in ('.png','.jpg','.jpeg','.webp','.gif'):continue
   b=z.read(target)
   if len(b)>12_000_000:continue
   filename=hashlib.sha256(b).hexdigest()[:24]+ext
   assets=out/'assets';assets.mkdir(exist_ok=True);(assets/filename).write_bytes(b)
   result[(int(start.find('d:row',NS).text)+1,int(start.find('d:col',NS).text)+1)]='imports/assets/'+filename
 return result

def product_name(v):
 if isinstance(v,str) and re.fullmatch(r'\s*(?:(?:EUR|USD|CNY|RMB|GBP)\s*)?[\d\s.,€$¥￥£|/–-]+(?:\s*(?:EUR|USD|CNY|RMB|GBP))?\s*',v,re.I):return False
 return isinstance(v,str) and 2<len(v.strip())<240 and not v.startswith('=') and not url_ok(v) and not LINK_LABEL.match(v.strip()) and re.search(r'[A-Za-zÀ-ÿ]',v) and not re.fullmatch(r'[\d\s.,€$¥￥£|/–-]+',v)
def number_value(text):
 text=str(text).strip()
 if ',' in text and '.' in text:
  decimal=',' if text.rfind(',')>text.rfind('.') else '.';other='.' if decimal==',' else ','
  return float(text.replace(other,'').replace(decimal,'.'))
 return float(text.replace(',','.'))
def price_of(cells,cached,headers):
 for c in cells:
  raw=str(c.value or '');m=re.search(r'(\d[\d.,]*)\s*(€|EUR)|(?:€|EUR)\s*(\d[\d.,]*)',raw,re.I)
  if m:return number_value(m[1] or m[3]),'EUR',raw
 for c in cells:
  raw=str(c.value or '');v=cached.get(c.coordinate,c.value)
  if not isinstance(v,(str,int,float)):continue
  if isinstance(v,str) and (v.startswith('=') or product_name(v)):continue
  t=str(v);n=re.search(r'\d[\d.,]*',t)
  if not n:continue
  # Use explicit currency and cell formatting; never infer currency from the brand or price magnitude.
  hint=raw+' '+str(c.number_format)+' '+headers.get(c.column,'')
  currency='EUR' if re.search(r'€|\bEUR\b',hint,re.I) else 'CNY' if re.search(r'¥|￥|\bCNY\b|RMB|人民币',hint,re.I) else 'USD' if re.search(r'\$|\bUSD\b',hint,re.I) else 'GBP' if re.search(r'£|\bGBP\b',hint,re.I) else None
  return number_value(n[0]),currency,raw
 return None,None,''

def parse_xlsx(path,source,out):
 z=zipfile.ZipFile(path);w=openpyxl.load_workbook(path,read_only=True,data_only=False);values=openpyxl.load_workbook(path,read_only=True,data_only=True)
 bookrels=rels(z,'xl/workbook.xml');sheets=ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS)
 products=[];seen={};counts={'unmatched_links':0,'missing_prices':0,'missing_images':0,'conflicting_prices':0};now=datetime.now(timezone.utc).date().isoformat()
 for si,s in enumerate(w):
  sp=bookrels.get(sheets[si].get(RID+'id'));tree=ET.fromstring(z.read(sp));rs=rels(z,sp)
  links={h.get('ref').split(':')[0]:rs.get(h.get(RID+'id'),'') for h in tree.findall('m:hyperlinks/m:hyperlink',NS)}
  images=embedded_images(z,sp,out)
  # Prices can be cached formula results. Both worksheets are streamed together.
  headers={}
  for rowno,(row,cv) in enumerate(zip(s,values[s.title]),1):
   row=[c for c in row if hasattr(c,'coordinate')];cache={c.coordinate:c.value for c in cv if hasattr(c,'coordinate')}
   if rowno<=12:
    for c in row:
     if isinstance(c.value,str) and re.fullmatch(r'\s*(price|preis|cost|CNY|USD|EUR|RMB|\$|¥|€)[\s()\w$€¥]*',c.value,re.I):headers[c.column]=c.value
   targets=[]
   for c in row:
    text=str(c.value or '');url=links.get(c.coordinate,'');m=re.match(r'=HYPERLINK\(\s*"([^"]+)"',text,re.I)
    if m:url=m[1]
    elif url_ok(text):url=text
    if url_ok(url):targets.append((c,url))
   for idx,(link,url) in enumerate(targets):
    left=targets[idx-1][0].column if idx else 0;right=targets[idx+1][0].column if idx+1<len(targets) else max([c.column for c in row]+[link.column+4])+1
    candidates=[c for c in row if left<c.column<link.column and link.column-c.column<=4 and product_name(c.value)]
    if not candidates:
     counts['unmatched_links']+=1;continue
    namecell=candidates[-1];name=re.sub(r'\s+',' ',namecell.value).strip()
    # Image and price candidates stay within this product's block.
    block=[c for c in row if namecell.column<=c.column<min(right,link.column+10)]
    pcells=[namecell]+[c for c in block if c is not namecell and c is not link]
    amount,currency,raw=price_of(pcells,cache,headers)
    image=''
    for c in block:
     im=re.match(r'=IMAGE\(\s*"(https?://[^"]+)"',str(c.value or ''),re.I)
     if im:image=im[1];break
    if not image:
     im=next((im for (rr,cc),im in images.items() if rowno<=rr<=rowno+1 and max(1,namecell.column-1)<=cc<min(right,link.column+10)),None);image=im or ''
    euro=amount if currency=='EUR' else None
    record=dict(id=hashlib.sha256((source['id']+url).encode()).hexdigest()[:20],name=name,brand='Sonstige',euro=euro,amount=amount,currency=currency,raw=raw or 'Preis fehlt',image=image,url=url,source=source['id'],location=s.title+'!'+namecell.coordinate,checked=now,status='Importiert · Produktseite nicht geprüft')
    key=(url,name)
    if key in seen:
     old=seen[key]
     if (old['amount'],old['currency'])!=(amount,currency):counts['conflicting_prices']+=1
     else:continue
    seen[key]=record;products.append(record)
    if amount is None:counts['missing_prices']+=1
    if not image:counts['missing_images']+=1
 w.close();values.close();return products,counts

def seal(data,out):
 public=serialization.load_pem_public_key((ROOT/'tools/import-public.pem').read_bytes());key=AESGCM.generate_key(bit_length=256);iv=os.urandom(12);b=lambda x:base64.b64encode(x).decode()
 wrapped=public.encrypt(key,padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
 out.write_text(json.dumps(dict(compression='gzip',key=b(wrapped),iv=b(iv),ciphertext=b(AESGCM(key).encrypt(iv,gzip.compress(json.dumps(data,ensure_ascii=False).encode()),None)))))

# Google's readable HTML view retains links/images even when XLSX export is unavailable.
from html.parser import HTMLParser
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor,as_completed
class GridHTML(HTMLParser):
 def __init__(self):
  super().__init__();self.grid={};self.row=0;self.col=0;self.cell=None;self.in_table=0;self.rowcount=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='table':self.in_table+=1
  if not self.in_table:return
  if tag=='tr':self.row+=1;self.col=0
  if tag in ('td','th'):
   if tag=='th':self.cell=None;return
   while (self.row,self.col) in self.grid:self.col+=1
   self.cell={'text':'','links':[],'original_links':{},'images':[],'row':self.row,'col':self.col}
   for rr in range(self.row,self.row+min(int(a.get('rowspan','1')),100)):
    for cc in range(self.col,self.col+min(int(a.get('colspan','1')),100)):self.grid[(rr,cc)]=self.cell
   self.col+=min(int(a.get('colspan','1')),100)
  if self.cell:
   if tag=='a' and url_ok(a.get('href')):
    url=a['href'];parts=urllib.parse.urlsplit(url)
    if parts.hostname in ('www.google.com','google.com'):
     qs=urllib.parse.parse_qs(parts.query);url=qs.get('q',qs.get('url',[url]))[0]
    if url_ok(url):
     self.cell['links'].append(url);self.cell['original_links'][url]=a['href']
   if tag=='img' and url_ok(a.get('src')):self.cell['images'].append(a['src'])
   if tag=='br':self.cell['text']+=' '
 def handle_data(self,text):
  if self.cell:self.cell['text']+=text
 def handle_endtag(self,tag):
  if tag in ('td','th'):self.cell=None
  if tag=='table':self.in_table=max(0,self.in_table-1)

def fetch_text(url):
 import time
 cache=Path(os.environ.get('FINDS_HTTP_CACHE',str(Path(tempfile.gettempdir())/'finds-http-cache')))
 cache.mkdir(exist_ok=True,parents=True);file=cache/(hashlib.sha256(url.encode()).hexdigest()+'.html')
 if os.environ.get('FINDS_USE_HTML_CACHE')=='1' and file.exists() and time.time()-file.stat().st_mtime<1800:return file.read_text()
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'DavesFindsImporter/1.0'}),timeout=50) as response:text=response.read(50_000_000).decode('utf-8')
 file.write_text(text);return text
def parse_html_sheet(html,source,gid):
 parser=GridHTML();parser.feed(html);grid=parser.grid;products=[];seen=set();counts={'unmatched_links':0,'missing_prices':0,'missing_images':0,'conflicting_prices':0};now=datetime.now(timezone.utc).date().isoformat()
 origins={id(c):c for c in grid.values()}.values()
 for linkcell in origins:
  if not linkcell['links']:continue
  rr=linkcell['row'];cc=linkcell['col']
  left=[grid.get((rr,col)) for col in range(max(0,cc-8),cc)]
  names=[c for c in left if c and product_name(c['text'].strip())]
  if not names:counts['unmatched_links']+=len(linkcell['links']);continue
  nc=names[-1];name=re.sub(r'\s+',' ',nc['text']).strip();near=[]
  for col in range(max(0,nc['col']-1),cc+10):
   c=grid.get((rr,col))
   if c and col>cc and product_name(c['text'].strip()):break
   if c and id(c) not in [id(x) for x in near]:near.append(c)
  prices=[nc]+[c for c in near if c is not nc and c is not linkcell]
  cells=[SimpleNamespace(value=c['text'].strip(),coordinate=str(i),number_format='',column=c['col']) for i,c in enumerate(prices)]
  amount,currency,raw=price_of(cells,{},{});image=next((im for c in near for im in c['images']),'')
  if not image:
   image=next((im for col in range(max(0,nc['col']-1),cc+10) for c in [grid.get((rr+1,col))] if c for im in c['images']),'')
  for url in linkcell['links']:
   key=(url,name)
   if key in seen:continue
   seen.add(key)
   products.append(dict(id=hashlib.sha256((source['id']+url+name).encode()).hexdigest()[:20],name=name,brand='Sonstige',euro=amount if currency=='EUR' else None,amount=amount,currency=currency,raw=raw or 'Preis fehlt',image=image,url=url,originalUrl=linkcell.get('original_links',{}).get(url,url),source=source['id'],sourceUrl=source['url'].split('#')[0]+'#gid='+gid,location='gid='+gid+' · Zeile '+str(rr),checked=now,status='Importiert aus lesbarer Google-Ansicht'))
   if amount is None:counts['missing_prices']+=1
   if not image:counts['missing_images']+=1
 return products,counts

def parse_readable(source,out=None):
 match=re.search(r'/spreadsheets/d/([A-Za-z0-9_-]+)',source['url']);base='https://docs.google.com/spreadsheets/d/'+match[1]
 page=fetch_text(base+'/htmlview');gids=list(dict.fromkeys(re.findall(r'gid=(\d+)',page)))
 if not gids:raise ValueError('Google liefert keine lesbaren Tabellenblätter')
 products=[];counts={'unmatched_links':0,'missing_prices':0,'missing_images':0,'conflicting_prices':0,'sheets_failed':0};seen=set()
 def one(gid):
  products,report=parse_html_sheet(fetch_text(base+'/htmlview/sheet?headers=true&gid='+gid),source,gid)
  if out is not None:cache_products(products,out)
  return products,report
 with ThreadPoolExecutor(max_workers=4) as executor:
  jobs={executor.submit(one,gid):gid for gid in gids[:80]}
  for job in as_completed(jobs):
   gid=jobs[job]
   try:
    result,report=job.result()
    for p in result:
     key=(p['url'],p['name'],p['amount'],p['currency'])
     if key not in seen:products.append(p);seen.add(key)
    for k,v in report.items():counts[k]+=v
    print('  Blatt '+gid+': '+str(len(result))+' Produkte',flush=True)
   except Exception:counts['sheets_failed']+=1
 if len(gids)>80:counts['sheets_failed']+=len(gids)-80
 return products,counts

def euro_rates():
 try:
  with urllib.request.urlopen('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml',timeout=20) as r:tree=ET.fromstring(r.read())
  rates={e.get('currency'):float(e.get('rate')) for e in tree.iter() if e.get('currency') and e.get('rate')}
  return {'date':next((e.get('time') for e in tree.iter() if e.get('time')),None),'rates':rates}
 except Exception:return None

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--links',default='');parser.add_argument('--only-source',default='');parser.add_argument('--xlsx',action='append',default=[]);parser.add_argument('--output',default=str(ROOT/'dist/imports'));args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
 sources=json.loads((ROOT/'sources.json').read_text());extra=re.findall(r'https://docs\.google\.com/spreadsheets/d/[A-Za-z0-9_-]+',args.links)
 for url in extra:
  if not any(url in s['url'] for s in sources):sources.append(dict(id=hashlib.sha256(url.encode()).hexdigest()[:12],name='Neue Liste',url=url+'/edit'))
 for path in args.xlsx:sources.append(dict(id='file-'+hashlib.sha256(Path(path).name.encode()).hexdigest()[:12],name=Path(path).name,url='',path=path))
 configured_sources=list(sources)
 if args.only_source:
  sources=[s for s in sources if s['id']==args.only_source]
  if not sources:parser.error('Unbekannte Quell-ID')
 index_path=out/'index.json';index=json.loads(index_path.read_text()) if index_path.exists() else {'files':[],'reports':[]};reports=[];rates=euro_rates()
 import tempfile
 with tempfile.TemporaryDirectory() as temp:
  def process_source(source):
   try:
    if source.get('path'):p=Path(source['path'])
    else:
     match=re.search(r'/spreadsheets/d/([A-Za-z0-9_-]+)',source['url'])
     if not match:raise ValueError('Kein gültiger Google-Sheets-Link')
     try:
      products,counts=parse_readable(source,out)
      if not products:raise ValueError('Keine Produktzeilen in lesbarer Ansicht')
     except Exception:
      print(source['name']+': versuche XLSX-Import',flush=True)
      request=urllib.request.Request('https://docs.google.com/spreadsheets/d/'+match[1]+'/export?format=xlsx',headers={'User-Agent':'DavesFindsImporter/1.0'})
      p=Path(temp)/(source['id']+'.xlsx')
      with urllib.request.urlopen(request,timeout=40) as response:
       with p.open('wb') as f:
        total=0
        while chunk:=response.read(1024*1024):
         total+=len(chunk)
         if total>200_000_000:raise ValueError('Datei größer als 200 MB')
         f.write(chunk)
      products,counts=parse_xlsx(p,source,out)
    if source.get('path'):products,counts=parse_xlsx(p,source,out)
    if not products:raise ValueError('Keine Produktzeilen erkannt; Layout muss geprüft werden')
    for product in products:
     currency=product['currency'];amount=product['amount']
     if amount is not None and currency!='EUR' and rates and currency in rates['rates']:
      product['euro']=round(amount/rates['rates'][currency],2);product['rateDate']=rates['date']
    counts['cached_images']=cache_products(products,out)
    counts['uncached_images']=len(products)-counts['cached_images']
    filename=hashlib.sha256(source['id'].encode()).hexdigest()[:20]+'.json';seal({'source':{k:v for k,v in source.items() if k!='path'},'products':products,'report':counts},out/filename)
    if filename not in index['files']:index['files'].append(filename)
    reports.append(dict(source=source['name'],id=source['id'],status='ok',products=len(products),**counts));print(source['name']+': '+str(len(products))+' Produkte')
   except Exception as e:
    reason='Zugriff verweigert: Freigabe oder Export gesperrt' if isinstance(e,urllib.error.HTTPError) and e.code in (401,403) else str(e)[:200]
    reports.append(dict(source=source['name'],id=source['id'],status='blocked',reason=reason));print(source['name']+': '+reason)
  with ThreadPoolExecutor(max_workers=3) as executor:list(executor.map(process_source,sources))
 changed={r['id'] for r in reports};index['reports']=[r for r in index.get('reports',[]) if r.get('id') not in changed]+reports;index['rates']=rates;index['updated']=datetime.now(timezone.utc).isoformat();index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2))
 (ROOT/'sources.json').write_text(json.dumps([{k:v for k,v in s.items() if k!='path'} for s in configured_sources if not s.get('path')],ensure_ascii=False,indent=2))
 if not any(r['status']=='ok' for r in reports):print('Kein neuer Import. Vorhandene Daten bleiben erhalten.',file=sys.stderr)
if __name__=='__main__':main()
