import os,json,time,subprocess,secrets,urllib.request,urllib.error,http.cookiejar,base64,shutil
from pathlib import Path
root=Path.cwd();runtime=root/'.ci-runtime';out=root/'evidence';out.mkdir(exist_ok=True)
env=os.environ.copy()
for key in ['JENKINS_PASSWORD','POSTGRES_PASSWORD','PGADMIN_PASSWORD','GRAFANA_PASSWORD']:
 env[key]=secrets.token_hex(20)
 print('::add-mask::'+env[key],flush=True)
env.update(JENKINS_HOME=str(runtime/'home'),A2_REPO_URL='https://github.com/'+env['GITHUB_REPOSITORY']+'.git',COMPOSE_PROJECT_NAME='a2homol',IMAGE_TAG='1',DOCKER_IMAGE='jogo-enigma-api')
auth=base64.b64encode(('gustavo-a2:'+env['JENKINS_PASSWORD']).encode()).decode()
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def get(path,data=None):
 req=urllib.request.Request('http://127.0.0.1:9090/'+path,data=data,headers={'Authorization':'Basic '+auth})
 if data is not None:
  crumb=json.loads(get('crumbIssuer/api/json'));req.add_header(crumb['crumbRequestField'],crumb['crumb'])
 return opener.open(req,timeout=30).read()
log=open(out/'jenkins-startup.log','w')
proc=subprocess.Popen(['java','-Djenkins.install.runSetupWizard=false','-jar',str(runtime/'jenkins.war'),'--httpPort=9090','--httpListenAddress=127.0.0.1'],env=env,stdout=log,stderr=subprocess.STDOUT)
result='FAILURE'
try:
 for n in range(120):
  try:
   get('job/A2_P2_P3_Jogo_Enigma/api/json');break
  except Exception:
   if proc.poll() is not None:raise RuntimeError('Jenkins terminou durante inicializacao')
   time.sleep(3)
 else:raise RuntimeError('Jenkins nao ficou pronto em 6 minutos')
 get('job/A2_P2_P3_Jogo_Enigma/build',b'')
 for n in range(450):
  try:
   data=json.loads(get('job/A2_P2_P3_Jogo_Enigma/lastBuild/api/json'))
   if not data['building']:
    result=data['result'];break
   if n%6==0: print('Jenkins build',data['number'],'em execucao',flush=True)
  except urllib.error.HTTPError as e:
   if e.code!=404:raise
  time.sleep(5)
 else:raise RuntimeError('Pipeline excedeu tempo limite')
 print('Resultado real Jenkins:',result,flush=True)
finally:
 for path,name in [('job/A2_P2_P3_Jogo_Enigma/1/consoleText','jenkins-console.txt'),('job/A2_P2_P3_Jogo_Enigma/1/api/json','jenkins-build.json'),('job/A2_P2_P3_Jogo_Enigma/config.xml','jenkins-job.xml'),('job/A2_P2_P3_Jogo_Enigma/1/wfapi/describe','stages.json'),('job/A2_P2_P3_Jogo_Enigma/1/testReport/api/json','junit.json')]:
  try:(out/name).write_bytes(get(path))
  except Exception as e:print('Coleta',name,str(e))
 ws=runtime/'home/workspace/A2_P2_P3_Jogo_Enigma'
 if ws.exists():
  for folder,name in [('target/site','reports'),('target/surefire-reports','surefire'),('frontend/cypress','cypress'),('evidence','verificacoes')]:
   if (ws/folder).exists():shutil.copytree(ws/folder,out/name,dirs_exist_ok=True)
  for args,name in [(['ps','--format','json'],'containers.json'),(['logs','--no-color'],'compose.log')]:
   p=subprocess.run(['docker','compose','-f','docker-compose.homol.yml']+args,cwd=ws,env=env,capture_output=True,text=True)
   (out/name).write_text(p.stdout+'\n'+p.stderr)
 capture=subprocess.run(['node','ci/capture.cjs'],env=env)
 if capture.returncode and result=='SUCCESS':result='EVIDENCE_FAILURE'
 (out/'provenance.json').write_text(json.dumps({'repository':env['GITHUB_REPOSITORY'],'commit':env['GITHUB_SHA'],'run_url':f"https://github.com/{env['GITHUB_REPOSITORY']}/actions/runs/{env['GITHUB_RUN_ID']}",'jenkins_result':result,'captured_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())},indent=2))
 # Remove any generated password from text logs before upload, without altering results.
 for f in out.rglob('*'):
  if f.is_file() and f.suffix in ['.txt','.log','.json','.xml']:
   text=f.read_text(errors='replace')
   for key in ['JENKINS_PASSWORD','POSTGRES_PASSWORD','PGADMIN_PASSWORD','GRAFANA_PASSWORD']:text=text.replace(env[key],'[REDACTED]')
   f.write_text(text)
 proc.terminate();log.close()
raise SystemExit(0 if result=='SUCCESS' else 1)
