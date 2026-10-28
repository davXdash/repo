"""Stable product identities and GitHub-hosted thumbnail caching."""
import hashlib,io,os,re,threading,time,urllib.request,urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from PIL import Image,ImageOps
_POOL=ThreadPoolExecutor(max_workers=20);_LOCK=threading.Lock();_TASKS={}
def identity(url):
 for _ in range(5):
  try:
   u=urllib.parse.urlsplit(url);qs=urllib.parse.parse_qs(u.query or u.fragment.partition('?')[2])
   nested=next((qs[k][0] for k in ['url','productUrl','productLink'] if qs.get(k)),None)
   if nested:
    for i in range(3):
     if nested.startswith(('https://','http://')):break
     nested=urllib.parse.unquote(nested)
    url=nested;continue
   platform=(qs.get('platform',qs.get('shop_type',['']))[0]).lower()
   for key in ['itemID','itemId','id']:
    if qs.get(key) and qs[key][0].isdigit():
     site='taobao' if 'taobao' in u.hostname or platform=='taobao' else '1688' if '1688' in u.hostname or platform in ('ali_1688','1688') else 'weidian' if 'weidian' in u.hostname or platform=='weidian' else u.hostname
     return site+':'+qs[key][0]
   m=re.search(r'/(weidian|taobao|1688|3)/(\d+)',u.path)
   if m:return ('weidian' if m[1]=='3' else m[1])+':'+m[2]
   kept=[(k,v) for k,vs in qs.items() if k.lower() not in ('ref','affcode','invitecode','memberid','spm') for v in vs]
   return 'url:'+urllib.parse.urlunsplit((u.scheme,u.netloc,u.path,urllib.parse.urlencode(sorted(kept)),u.fragment if not u.query else ''))
  except:return 'url:'+str(url)
 return 'url:'+str(url)
def download_thumbnail(product,out):
 ident=identity(product['url']);key=hashlib.sha256(ident.encode()).hexdigest()[:24];target=out/'media'/key[:2]/(key+'.webp');target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and target.stat().st_size>100:return 'imports/media/'+key[:2]+'/'+key+'.webp'
 url=product.get('image')
 if not url:return ''
 if url.startswith('imports/assets/'):
  local=out.parent/url
  if not local.exists():return ''
  raw=local.read_bytes()
 else:
  for attempt in range(2):
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Referer':product.get('sourceUrl','https://docs.google.com/')}),timeout=18) as response:
     raw=response.read(10_000_001)
    if len(raw)>10_000_000:return ''
    break
   except Exception:
    if attempt:return ''
    time.sleep(.3)
 try:
  with Image.open(io.BytesIO(raw)) as image:
   image=ImageOps.exif_transpose(image);image.thumbnail((480,480));image=image.convert('RGB');buffer=io.BytesIO();image.save(buffer,format='WEBP',quality=76,method=3)
  temporary=target.with_suffix('.tmp');temporary.write_bytes(buffer.getvalue());temporary.replace(target)
  return 'imports/media/'+key[:2]+'/'+key+'.webp'
 except Exception:return ''
def cache_products(products,out):
 jobs={};completed=0
 for p in products:
  p['productKey']=identity(p['url'])
  if not p.get('image'):continue
  with _LOCK:
   key=(str(out),p['productKey'])
   if key not in _TASKS:_TASKS[key]=_POOL.submit(download_thumbnail,p,out)
   job=_TASKS[key]
  jobs.setdefault(job,[]).append(p)
 for job in as_completed(jobs):
  try:thumbnail=job.result()
  except Exception:thumbnail=''
  for p in jobs[job]:
   p['thumbnail']=thumbnail
   p['imageState']='cached' if thumbnail else 'unavailable'
  completed+=1
  if completed%250==0:print('  Bildcache: '+str(completed)+' / '+str(len(jobs)),flush=True)
 return sum(bool(p.get('thumbnail')) for p in products)
