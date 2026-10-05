const {chromium}=require('../.ci-runtime/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1});
 const errors=[];
 async function shot(name,url,action){
  try {await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});if(action)await action();await page.waitForTimeout(2000);await page.screenshot({path:`evidence/${name}.png`,fullPage:!name.includes('console') && !name.includes('scm')});}
  catch(e){errors.push(`${name}: ${e.message}`);console.error(errors.at(-1));await page.screenshot({path:`evidence/debug-${name}.png`}).catch(()=>{});fs.writeFileSync(`evidence/debug-${name}.txt`,await page.locator('body').innerText().catch(()=>''));}
 }
 await page.goto('http://127.0.0.1:9090/login');
 await page.locator('input[name="j_username"]').fill('gustavo-a2');
 await page.locator('input[name="j_password"]').fill(process.env.JENKINS_PASSWORD);
 await Promise.all([page.waitForURL(u=>!u.pathname.includes('login')) ,page.locator('button[name="Submit"]').click()]);
 const job='http://127.0.0.1:9090/job/A2_P2_P3_Jogo_Enigma';
 await shot('jenkins-pipeline',job+'/');
 await shot('jenkins-build',job+'/1/');
 await shot('jenkins-junit',job+'/1/testReport/');
 await shot('jenkins-scm',job+'/configure',async()=>{await page.getByText('Pipeline script from SCM',{exact:true}).first().scrollIntoViewIfNeeded().catch(()=>{});});
 // Console tail captured from Jenkins itself, not a recreated results page.
 await shot('jenkins-console',job+'/1/console',async()=>{await page.locator('#footer').scrollIntoViewIfNeeded().catch(()=>{});});
 await shot('aplicacao','http://127.0.0.1:3000');
 await shot('health','http://127.0.0.1:8080/actuator/health');
 await shot('prometheus-targets','http://127.0.0.1:9091/targets');
 await shot('prometheus-up','http://127.0.0.1:9091/query?g0.expr=up%7Bjob%3D%22jogo-enigma-api%22%7D&g0.tab=1');
 try {
  await page.goto('http://127.0.0.1:3001/login');
  await page.locator('input[name="user"]').fill('admin');
  await page.locator('input[name="password"]').fill(process.env.GRAFANA_PASSWORD);
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL(u=>!u.pathname.includes('login'));
  await shot('grafana-dashboard','http://127.0.0.1:3001/d/a2-jogo-enigma-homol?orgId=1&from=now-5m&to=now&refresh=5s',async()=>{await page.getByText('ONLINE',{exact:true}).first().waitFor({timeout:30000});});
  await shot('grafana-datasource','http://127.0.0.1:3001/connections/datasources/edit/prometheus-a2',async()=>{
   await page.getByRole('button',{name:/^(Save & test|Test)$/}).click();
   await page.getByText(/Successfully queried|Data source is working/).first().waitFor({timeout:15000});
  });
  const panes=JSON.stringify({a2:{datasource:'prometheus-a2',queries:[{refId:'A',expr:'up{job="jogo-enigma-api"}',range:true,instant:true,editorMode:'code',datasource:{type:'prometheus',uid:'prometheus-a2'}}],range:{from:'now-5m',to:'now'}}});
  await shot('grafana-explore','http://127.0.0.1:3001/explore?schemaVersion=1&panes='+encodeURIComponent(panes)+'&orgId=1',async()=>{
   await page.getByText('up',{exact:true}).first().waitFor({timeout:15000}).catch(()=>{});
   await page.waitForTimeout(3000);
  });
 }catch(e){errors.push('Grafana: '+e.message);}
 fs.writeFileSync('evidence/capture-errors.json',JSON.stringify(errors,null,2));
 await browser.close();if(errors.length)process.exitCode=1;
})();

