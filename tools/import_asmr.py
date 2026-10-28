"""ASMRHauler public product API; retain source prices and original purchase URLs."""
import hashlib,json,math,urllib.request,urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
BASE='https://asmrhauler.com'
def page(offset):
 url=BASE+'/api/products?'+urllib.parse.urlencode(dict(limit=60,offset=offset,domain='asmrhauler.com'))
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'}),timeout=50) as r:return json.load(r)
def records(items,source):
 products=[];seen=set();now=datetime.now(timezone.utc).date().isoformat()
 for item in items:
  uid=str(item.get('id',''));url=item.get('link');name=item.get('name')
  if not uid or uid in seen or not name or not isinstance(url,str) or urllib.parse.urlsplit(url).scheme not in ('https','http'):continue
  seen.add(uid)
  try:amount=float(item.get('price'));amount=amount if math.isfinite(amount) and amount>=0 else None
  except (ValueError,TypeError):amount=None
  products.append(dict(id=hashlib.sha256((source['id']+uid).encode()).hexdigest()[:20],name=name,brand='Weitere',url=url,originalUrl=url,source=source['id'],sourceUrl=BASE+'/products?'+urllib.parse.urlencode({'search':name})+'#product-'+uid,location='ASMRHauler · '+uid,sourceCategory=item.get('category'),image=urllib.parse.urljoin(BASE,item['image']) if item.get('image') else '',amount=amount,currency='USD',euro=None,raw='$'+str(item.get('price')) if amount is not None else 'Preis fehlt',qcUrl=BASE+'/qc-finder?'+urllib.parse.urlencode({'link':url}),checked=now,status='Importiert · Produktseite nicht geprüft'))
 return products
def parse_asmr(source,out):
 first=page(0);total=int(first['total']);step=int(first.get('pageSize',len(first['products'])));items=list(first['products'])
 if not 0<step<=200 or total>50000:raise ValueError('Unerwartete API-Seitengröße oder Kataloggröße')
 with ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(page,range(step,total,step)):items.extend(result['products'])
 if len(items)!=total or len({i['id'] for i in items})!=total:raise ValueError('Unvollständige API-Seiten; bisherige Daten bleiben erhalten')
 products=records(items,source)
 return products,dict(source_items=total,unmatched_links=total-len(products),missing_prices=sum(p['amount'] is None for p in products),missing_images=sum(not p['image'] for p in products),conflicting_prices=0)
