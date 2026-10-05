import json,time,urllib.request,urllib.parse,sys
from pathlib import Path
out=Path('evidence');out.mkdir(exist_ok=True)
def get(url):
 with urllib.request.urlopen(url,timeout=10) as r:return json.load(r)
if sys.argv[1]=='health':
 for n in range(60):
  try:
   data=get('http://127.0.0.1:8080/actuator/health')
   if data['status']=='UP':break
  except Exception:pass
  time.sleep(3)
 else:raise SystemExit('API nao ficou UP em 180 segundos')
 (out/'health.json').write_text(json.dumps(data,indent=2));print(data)
else:
 queries=['up{job="jogo-enigma-api"}','sum(rate(http_server_requests_seconds_count[1m]))','sum(rate(http_server_requests_seconds_sum[1m]))/sum(rate(http_server_requests_seconds_count[1m]))','sum(jvm_memory_used_bytes{area="heap"})']
 # Generate real requests over enough scrapes for rate[1m].
 for n in range(35):
  get('http://127.0.0.1:8080/actuator/health');get('http://127.0.0.1:3000/bff/participantes');time.sleep(2)
 results={}
 for q in queries:
  data=get('http://127.0.0.1:9091/api/v1/query?'+urllib.parse.urlencode({'query':q}))
  assert data['status']=='success' and data['data']['result'],data
  value=data['data']['result'][0]['value'][1]
  assert value not in ('NaN','+Inf','-Inf'),data
  if q.startswith('up{'):assert value=='1',data
  results[q]=data;print(q,value)
 (out/'metrics.json').write_text(json.dumps(results,indent=2))
 (out/'targets.json').write_text(json.dumps(get('http://127.0.0.1:9091/api/v1/targets'),indent=2))
