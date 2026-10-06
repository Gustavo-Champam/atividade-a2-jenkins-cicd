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
 const job='http://127.0.0.1:9090/job/A2_P1_AC1_Equipe';
 await shot('job-ac1',job+'/');
 await shot('junit-ac1',job+'/1/testReport/');
 await shot('jacoco-ac1','file://'+process.cwd()+'/.ci-runtime/home/workspace/A2_P1_AC1_Equipe/target/site/jacoco/index.html');
 await shot('console-ac1',job+'/1/console',async()=>{await page.locator('#footer').scrollIntoViewIfNeeded().catch(()=>{});});
 fs.writeFileSync('evidence/capture-errors.json',JSON.stringify(errors,null,2));
 await browser.close();if(errors.length)process.exitCode=1;
})();

