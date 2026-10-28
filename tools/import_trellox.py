"""Read Trellox's public catalog API, retaining all supplied purchase URLs."""
import hashlib,json,urllib.request,urllib.parse,math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
BASE='https://trellox.de'
def fetch_page(offset):
 url=BASE+'/api/v1/rd/items?'+urllib.parse.urlencode(dict(limit=200,offset=offset,agent='pikobuy'))
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'DavesFindsImporter/1.0','Accept':'application/json'}),timeout=50) as r:payload=json.load(r)
 return payload.get('data',payload)
def records(items,source):
 products=[];now=datetime.now(timezone.utc).date().isoformat()
 for item in items:
  name=item.get('name') or item.get('title');key=item.get('key');category=item.get('categoryFull') or item.get('category') or 'random'
  if item.get('type')=='shoe':category='shoes'
  if not name or not key:continue
  route=category.replace('gymstuff-','gymstuff/').replace('women-','women/')
  if route=='electronics':route='electronic'
  source_url=f"{BASE}/{route}/{item['id']}"
  image=urllib.parse.urljoin(BASE,item.get('imageUrl') or item.get('image') or '')
  offers=[('batch',item.get('bestBatchLink') or item.get('links',{}).get('batch'),item.get('bestBatchPrice',item.get('price')),item.get('bestBatchRaw')),('budget',item.get('budgetBatchLink') or item.get('links',{}).get('budgetBatch') or item.get('links',{}).get('budget'),item.get('bestBudgetPrice',item.get('priceBudget')),item.get('budgetBatchRaw'))]
  for kind,url,price,seller in offers:
   if not url or not url.startswith(('https://','http://')):continue
   try:amount=float(price);amount=amount if math.isfinite(amount) and amount>0 else None
   except (TypeError,ValueError):amount=None
   products.append(dict(id=hashlib.sha256((source['id']+key+kind+url).encode()).hexdigest()[:20],name=name,brand=item.get('brand') or item.get('mk') or 'Weitere',url=url,originalUrl=url,sellerUrl=seller,source=source['id'],sourceUrl=source_url,location=key+' · '+kind,image=image if image!=BASE+'/' else '',amount=amount,currency='USD',euro=None,raw=('$'+str(price)) if amount else 'Preis fehlt',checked=now,status='Importiert · Produktseite nicht geprüft'))
 return products
def parse_trellox(source,out):
 first=fetch_page(0);total=int(first['total']);items=list(first['items'])
 if total>30000:raise ValueError('Unerwartet großer Katalog')
 with ThreadPoolExecutor(max_workers=4) as pool:
  for page in pool.map(fetch_page,range(200,total,200)):items.extend(page['items'])
 keys=[x.get('key') for x in items]
 if len(keys)!=total or len(set(keys))!=total:raise ValueError('Unvollständige oder doppelte API-Seiten; bisheriger Import bleibt erhalten')
 products=records(items,source)
 return products,dict(unmatched_links=sum(not (i.get('bestBatchLink') or i.get('budgetBatchLink')) for i in items),missing_prices=sum(p['amount'] is None for p in products),missing_images=sum(not p['image'] for p in products),conflicting_prices=0,source_items=total)
