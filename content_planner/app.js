'use strict';
const STAGES=['Idea','Planned','Filmed','Editing','Review','Ready','Published'];
const SEED=window.TECH2GO_CONTENT_SEED;
const FIELDS=Object.keys(SEED[0]);
const METRICS=['views','saves','shares','inquiries','bookings'];
const CHECKS=['privacy_checked','technical_checked','cta_checked'];
const STORAGE='tech2go-content-planner-v1';
const $=id=>document.getElementById(id);
const today=()=>new Intl.DateTimeFormat('en-CA',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function validDate(s){return /^\d{4}-\d{2}-\d{2}$/.test(s)&&!Number.isNaN(Date.parse(s+'T12:00:00Z'))&&new Date(s+'T12:00:00Z').toISOString().slice(0,10)===s;}
function validate(row){
 if(!row||typeof row!=='object'||Array.isArray(row))throw Error('Each story must be an object.');
 const clean={};for(const field of FIELDS){if(typeof row[field]!=='string'||row[field].length>12000)throw Error(`Invalid or missing ${field}.`);clean[field]=row[field];}
 if(!/^[A-Za-z0-9_-]{1,40}$/.test(clean.id)||!clean.title.trim())throw Error('A story needs a valid ID and a title.');
 if(!STAGES.includes(clean.stage))throw Error('Choose a valid pipeline stage.');
 if(!['pending','own_demo','customer_approved'].includes(clean.footage_permission))throw Error('Choose a permission basis.');
 for(const key of CHECKS)if(!['true','false'].includes(clean[key]))throw Error('Invalid review check.');
 for(const key of ['planned_date','published_date','measurement_date'])if(clean[key]&&!validDate(clean[key]))throw Error('Use valid calendar dates.');
 for(const key of METRICS)if(clean[key]&&!/^\d{1,12}$/.test(clean[key]))throw Error('Metrics must be blank or whole nonnegative numbers.');
 if(clean.post_url){let url;try{url=new URL(clean.post_url);}catch{throw Error('Enter a complete http(s) post URL.');}if(!['http:','https:'].includes(url.protocol))throw Error('Post links must use http(s).');}
 if(['Ready','Published'].includes(clean.stage)&&(clean.footage_permission==='pending'||CHECKS.some(k=>clean[k]!=='true')))throw Error('Before Ready or Published, establish footage permission and complete all three review checks.');
 if(clean.stage==='Published'&&(!clean.post_url||!clean.published_date))throw Error('Published stories require the actual post URL and publication date.');
 if(clean.published_date&&clean.published_date>today())throw Error('An actual publication date cannot be in the future. Use planned date for suggestions.');
 if(clean.measurement_date&&(!clean.published_date||clean.measurement_date<clean.published_date||clean.measurement_date>today()))throw Error('Measurement date must be between the actual publication date and today.');
 if(METRICS.some(k=>clean[k]!=='' )&&!clean.measurement_date)throw Error('Add a measurement date when recording results.');
 return clean;
}
function validatePlan(value){if(!Array.isArray(value)||value.length>2000)throw Error('Import an array of up to 2,000 stories.');const rows=value.map(validate);if(new Set(rows.map(r=>r.id)).size!==rows.length)throw Error('Duplicate story IDs.');return rows;}
let plan=structuredClone(SEED),view='board',editing=null;
try{const saved=localStorage.getItem(STORAGE);if(saved)plan=validatePlan(JSON.parse(saved));}catch(e){$('notice').textContent='Saved data could not be loaded. Starter plan shown; export your work and avoid storing customer data here.';}
function persist(){try{localStorage.setItem(STORAGE,JSON.stringify(plan));return true;}catch(e){return false;}}
function filtered(){const query=$('search').value.toLowerCase();return plan.filter(r=>(!$('pillar').value||r.pillar===$('pillar').value)&&(!$('channel').value||r.platform===$('channel').value)&&[r.id,r.title,r.device_group,r.hook].join(' ').toLowerCase().includes(query));}
function card(row){const b=el('button',undefined,'story');b.type='button';b.append(el('span',row.pillar,'badge'),el('strong',row.title),el('small',`${row.id} · ${row.platform}`),el('small',`${row.planned_date||'Unscheduled'} · ${row.city||'AV'}`),el('small',row.stage==='Published'?'Published · results can be recorded':row.footage_permission==='pending'?'Footage permission not yet established':`Footage: ${row.footage_permission==='own_demo'?'shop demo':'customer approved'}`));b.setAttribute('aria-label',`Edit ${row.id}: ${row.title}`);b.addEventListener('click',()=>openStory(row.id));return b;}
function render(){
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
 const rows=filtered();$('summary').textContent=`${rows.length} of ${plan.length} stories · ${plan.filter(r=>r.stage==='Ready').length} ready · ${plan.filter(r=>r.stage==='Published').length} published · Starter dates: Nov 30–Dec 25, 2026; adjust to actual repair opportunities.`;
 const root=$('view');root.replaceChildren();
 if(view==='board'){
  const board=el('div',undefined,'board');
  STAGES.forEach(stage=>{const lane=el('section',undefined,'lane');const head=el('div',undefined,'lane-head');const selected=rows.filter(r=>r.stage===stage);head.append(el('span',stage),el('span',String(selected.length),'count'));lane.append(head);selected.forEach(r=>lane.append(card(r)));if(!selected.length)lane.append(el('p','No stories here yet.','empty'));board.append(lane);});root.append(board);
 }else if(view==='calendar'){
  const calendar=el('div',undefined,'calendar');const dates=[...new Set(rows.map(r=>r.planned_date))].sort((a,b)=>(a||'9999').localeCompare(b||'9999'));
  dates.forEach(date=>{const group=el('section',undefined,'calendar-day');group.append(el('h3',date?new Intl.DateTimeFormat('en-US',{timeZone:'UTC',weekday:'short',month:'short',day:'numeric',year:'numeric'}).format(new Date(date+'T12:00:00Z')):'Unscheduled'));rows.filter(r=>r.planned_date===date).forEach(r=>group.append(card(r)));calendar.append(group);});root.append(calendar);if(!dates.length)root.append(el('p','No matching stories.'));
 }else{
  root.append(el('p','Record results per story’s primary-channel post, ideally seven days after publication. Blank means unmeasured. Inquiries are attributed repair inquiries; bookings are confirmed appointments. Do not count proposed bookings or sum overlapping audiences.','results-note'));
  const wrap=el('div',undefined,'table-wrap'),table=el('table'),head=el('thead'),tr=el('tr');['Story / primary channel','Published','Measured','Views','Saves','Shares','Inquiries','Bookings','Inquiry rate','Edit'].forEach(s=>tr.append(el('th',s)));head.append(tr);table.append(head);const body=el('tbody');
  rows.forEach(r=>{const tr=el('tr');const rate=r.views!==''&&Number(r.views)>0&&r.inquiries!==''?`${(Number(r.inquiries)/Number(r.views)*100).toFixed(2)}%`:'—';[r.title+' · '+r.platform,r.published_date||'—',r.measurement_date||'—',...METRICS.map(k=>r[k]===''?'—':r[k]),rate].forEach(s=>tr.append(el('td',s)));const td=el('td'),b=el('button','Edit');b.addEventListener('click',()=>openStory(r.id));td.append(b);tr.append(td);body.append(tr);});table.append(body);wrap.append(table);root.append(wrap);
 }
}
const EDIT_FIELDS=[
 ['title','Story title','text'],['stage','Stage',STAGES],['planned_date','Suggested post date','date'],['owner','Owner','text'],
 ['device_group','Device group',['Cellphones','Laptops','Desktops','Data access','The van']],['pillar','Content pillar',['Trust / education','Repair process','Buying decisions','Local awareness','Booking education']],
 ['platform','Primary channel',['Instagram Reels','TikTok','YouTube Shorts']],['city','Local audience',['Lancaster','Palmdale','Quartz Hill','Antelope Valley']],
 ['service_ids','Related repair IDs (semicolon separated)','text'],['hook','Opening hook','textarea'],['story_outline','Story outline','textarea'],['shot_list','Shot list','textarea'],['review_notes','Claims / footage notes to check','textarea'],['cta','Call to action','textarea'],
 ['post_url','Actual primary-channel post URL','url'],['published_date','Actual publication date','date'],['measurement_date','Results measurement date','date'],
 ...METRICS.map(k=>[k,k[0].toUpperCase()+k.slice(1),'number']),['learning','What did we learn?','textarea'],['next_test','One change to try next','textarea']];
const form=$('story-form');
EDIT_FIELDS.forEach(([name,title,type])=>{const label=el('label',title);if(['hook','story_outline','shot_list','review_notes','cta','learning','next_test','post_url'].includes(name))label.className='wide';let input;
 if(Array.isArray(type)){input=el('select');type.forEach(v=>{const o=el('option',v);o.value=v;input.append(o);});}else{input=el(type==='textarea'?'textarea':'input');if(type!=='textarea')input.type=type;if(type==='number'){input.min='0';input.max='999999999999';input.step='1';}else input.maxLength=12000;}
 input.name=name;if(name==='title')input.required=true;label.append(input);$('fields').append(label);
});
function openStory(id){editing=id;const row=id?plan.find(r=>r.id===id):Object.fromEntries(FIELDS.map(k=>[k,'']));
 if(!id)Object.assign(row,{id:'C'+String(Math.max(0,...plan.map(r=>Number(r.id.replace(/^C/,''))||0))+1).padStart(3,'0'),stage:'Idea',device_group:'Cellphones',pillar:'Trust / education',platform:'Instagram Reels',city:'Antelope Valley',owner:'Unassigned',footage_permission:'pending',privacy_checked:'false',technical_checked:'false',cta_checked:'false'});
 $('editor-id').textContent=row.id;$('editor-title').textContent=id?'Build the story.':'Start with a useful idea.';
 for(const field of FIELDS){const input=form.elements.namedItem(field);if(input){if(input.type==='checkbox')input.checked=row[field]==='true';else input.value=row[field];}}
 $('edit-error').hidden=true;$('delete').hidden=!id;$('editor').showModal();}
$('close').addEventListener('click',()=>$('editor').close());$('new').addEventListener('click',()=>openStory(null));
form.addEventListener('submit',event=>{event.preventDefault();const row={id:$('editor-id').textContent};for(const field of FIELDS){if(field==='id')continue;const input=form.elements.namedItem(field);row[field]=input.type==='checkbox'?String(input.checked):input.value.trim();}
 try{const valid=validate(row);if(editing)plan=plan.map(r=>r.id===editing?valid:r);else{if(plan.some(r=>r.id===valid.id))throw Error('Story ID already exists.');plan.push(valid);}const saved=persist();$('editor').close();$('notice').textContent=saved?'Saved in this browser. No post was scheduled or published.':'Changed in memory only; browser storage is unavailable. Download a JSON backup before closing.';render();}catch(e){$('edit-error').textContent=e.message;$('edit-error').hidden=false;}
});
$('delete').addEventListener('click',()=>{if(confirm('Delete this story from this local planner? Export a backup first if needed.')){plan=plan.filter(r=>r.id!==editing);const saved=persist();$('editor').close();$('notice').textContent=saved?'Story removed from this browser.':'Removed in memory only; download a JSON backup.';render();}});
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{view=b.dataset.view;render();}));
for(const id of ['search','pillar','channel'])$(id).addEventListener('input',render);
function download(name,content,type){const url=URL.createObjectURL(new Blob([content],{type}));const a=el('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('backup').addEventListener('click',()=>download('tech2go-content-backup.json',JSON.stringify(plan,null,2),'application/json'));
function csvCell(s){const value=/^[\s]*[=+\-@]/.test(s)?"'"+s:s;return '"'+value.replaceAll('"','""')+'"';}
$('export-csv').addEventListener('click',()=>download('tech2go-content-plan.csv',[FIELDS,...plan.map(r=>FIELDS.map(k=>r[k]))].map(row=>row.map(csvCell).join(',')).join('\r\n'),'text/csv;charset=utf-8'));
$('import').addEventListener('click',()=>$('import-file').click());$('import-file').addEventListener('change',async event=>{const file=event.target.files[0];if(!file)return;try{if(file.size>2*1024*1024)throw Error('Backup must be smaller than 2 MB.');const incoming=validatePlan(JSON.parse(await file.text()));if(!confirm(`Replace this browser’s ${plan.length} stories with ${incoming.length} imported stories? Back up current work first.`))return;plan=incoming;const saved=persist();$('notice').textContent=saved?'Backup restored in this browser. Nothing was published.':'Backup opened in memory only; storage unavailable.';render();}catch(e){$('notice').textContent='Import stopped: '+e.message;}finally{event.target.value='';}});
render();
