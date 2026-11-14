import json, time, pathlib, datetime, urllib.parse, urllib.request

def page(fuel, n):
    url='https://api.apiaberta.pt/v1/fuel/stations?'+urllib.parse.urlencode({'fuel':fuel,'limit':100,'page':n})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MotoQuest/1.0'}),timeout=30) as r:
                result=json.load(r)
            if not isinstance(result.get('data'),list): raise ValueError('Invalid data')
            return result
        except Exception:
            if attempt==3: raise
            time.sleep(2**attempt)

out={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fuels':{}}
for fuel in ('gasoline_95','gasoline_98'):
    first=page(fuel,1)
    pages=int(first.get('meta',{}).get('pages',1))
    if not 1<=pages<=200: raise ValueError('Invalid page count')
    rows=list(first['data'])
    for n in range(2,pages+1): rows.extend(page(fuel,n)['data'])
    if not rows: raise ValueError('Empty fuel data')
    out['fuels'][fuel]=rows
    print(fuel,len(rows))
dest=pathlib.Path('data/fuel-prices.json')
dest.parent.mkdir(exist_ok=True)
dest.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
