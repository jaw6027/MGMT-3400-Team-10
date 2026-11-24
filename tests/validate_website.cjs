const {chromium}=require('playwright');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const previewURL=process.env.TECH2GO_PREVIEW_URL || 'http://127.0.0.1:4173/';
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1100}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(previewURL);await page.evaluate(()=>document.fonts.ready);
 await page.screenshot({path:path.join(root,'output/tech2go-desktop.png'),fullPage:true});
 await page.getByRole('button',{name:'Tomorrow',exact:true}).click();
 if(await page.locator('#stop-city').textContent()!=='Palmdale')throw Error('Stop did not change');
 if(await page.locator('#booking-city').inputValue()!=='Palmdale')throw Error('City selection did not follow stop');
 await page.locator('#call-link').click();
 if(!(await page.locator('#contact-note').textContent()).includes('aren’t connected'))throw Error('Demo call guard failed');
 await page.locator('[name=customer]').fill('Test Customer');await page.locator('[name=phone]').fill('bad');
 await page.locator('#device').selectOption('Computer');await page.locator('[name=model]').fill('Test Laptop');
 await page.locator('[name=date]').fill(await page.locator('[name=date]').getAttribute('min'));await page.locator('[name=time]').selectOption({index:1});
 await page.locator('[name=issue]').fill('Sample damaged screen');await page.locator('[name=consent]').check();
 await page.locator('button[type=submit]').click();
 if(!await page.locator('#form-error').isVisible())throw Error('Invalid phone accepted');
 await page.locator('[name=phone]').fill('(661) 555-0123');await page.locator('button[type=submit]').click();
 if(!await page.locator('#request-result').isVisible())throw Error('Preview not displayed');
 if(!(await page.locator('#request-result').textContent()).includes('Nothing was sent'))throw Error('Missing demo confirmation');
 await page.locator('#edit-request').click();
 if(await page.locator('[name=customer]').inputValue()!=='Test Customer')throw Error('Edits not preserved');
 await page.locator('[name=customer]').fill('<img src=x onerror=alert(1)>');await page.locator('button[type=submit]').click();
 if(await page.locator('#request-summary img').count())throw Error('Unsafe user content');
 await page.reload();
 if(await page.locator('[name=customer]').inputValue())throw Error('Personal info persisted');
 for(const width of [320,390,768,1440]){
  await page.setViewportSize({width,height:900});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Overflow at '+width);
 }
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(root,'output/tech2go-mobile.png'),fullPage:true});
 if(errors.length)throw Error(errors.join('\n'));
 console.log('PASS: daily stop changes, city sync, placeholder call guard, invalid phone rejection, request preview, edit flow, safe content, no personal data persistence, no page errors, responsive layout at 320/390/768/1440px.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
