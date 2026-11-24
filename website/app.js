'use strict';
const config = window.TECH2GO_CONFIG;
const pacific = 'America/Los_Angeles';
const todayString = new Intl.DateTimeFormat('en-CA', {timeZone: pacific,year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const baseDate = new Date(`${todayString}T12:00:00-08:00`);
const dateForDay = offset => { const date = new Date(baseDate); date.setUTCDate(date.getUTCDate()+offset); return date; };
const dateInput = document.getElementById('appointment-date');
dateInput.min = todayString;
const displayDate = date => new Intl.DateTimeFormat('en-US',{timeZone:pacific,month:'short',day:'numeric'}).format(date);
document.getElementById('third-day').textContent = new Intl.DateTimeFormat('en-US',{timeZone:pacific,weekday:'short'}).format(dateForDay(2));
function showStop(index) {
  const stop = config.stops[index];
  document.getElementById('stop-date').textContent = displayDate(dateForDay(index));
  for (const [id,value] of Object.entries({'stop-city':stop.city,'stop-area':stop.area,'stop-note':stop.note,'stop-hours':stop.hours,'stop-address':stop.address})) {
    document.getElementById(id).textContent=value;
  }
  document.querySelectorAll('[data-day]').forEach(button => button.setAttribute('aria-pressed',String(Number(button.dataset.day)===index)));
  const pin = document.getElementById('map-pin');
  pin.style.left=`${stop.x}%`; pin.style.top=`${stop.y}%`;
  document.getElementById('pin-label').textContent=`${stop.city} · sample stop`;
  document.getElementById('booking-city').value=stop.city;
}
document.querySelectorAll('[data-day]').forEach(button => button.addEventListener('click',()=>showStop(Number(button.dataset.day))));
showStop(0);
const digits = config.phone.replace(/\D/g,'');
document.getElementById('phone-display').textContent=digits.length===10 ? `(${digits.slice(0,3)}) ${digits.slice(3,6)}-${digits.slice(6)}` : config.phone;
for (const mode of ['call','text']) {
  const link = document.getElementById(`${mode}-link`);
  if (config.phoneIsPlaceholder) {
    link.addEventListener('click',event=>{
      event.preventDefault();
      const note=document.getElementById('contact-note');
      note.textContent=`${mode==='call'?'Calls':'Texts'} aren’t connected yet. (111) 111-1111 is a demo number. Try the appointment form below.`;
      note.classList.add('highlight');
    });
  } else {
    link.href=`${mode==='call'?'tel':'sms'}:${digits.length===10?'+1':''}${digits}`;
    document.getElementById('contact-note').textContent='Reach out to request an appointment. We’ll confirm availability.';
  }
}
document.querySelectorAll('[data-device]').forEach(button=>button.addEventListener('click',()=>{
  document.getElementById('device').value=button.dataset.device;
  document.getElementById('book').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  document.getElementById('device').focus({preventScroll:true});
}));
const form=document.getElementById('booking-form');
const result=document.getElementById('request-result');
const error=document.getElementById('form-error');
form.addEventListener('submit',event=>{
  event.preventDefault(); error.hidden=true;
  const values=Object.fromEntries(new FormData(form));
  if (!values.customer.trim() || !values.model.trim() || values.issue.trim().length<8) {
    error.textContent='Please add your name, device model and a short description of the issue.';error.hidden=false;return;
  }
  const phone=values.phone.replace(/\D/g,'');
  if (!/^\d{10}$/.test(phone) && !/^1\d{10}$/.test(phone)) {
    error.textContent='Please enter a 10-digit US phone number, with an optional +1 country code.';error.hidden=false;return;
  }
  const currentPacificDate = new Intl.DateTimeFormat('en-CA',{timeZone:pacific,year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
  if(values.date<currentPacificDate){error.textContent='Please choose today or a future date.';error.hidden=false;return;}
  const entries=[['Name',values.customer],['Contact',`${values.phone} · ${values.reply}`],['Device',`${values.device} · ${values.model}`],['Preference',`${values.date} · ${values.time} PT`],['City',values.city],['Issue',values.issue]];
  const summary=document.getElementById('request-summary');summary.replaceChildren();
  entries.forEach(([label,value])=>{
    const dt=document.createElement('dt');dt.textContent=label;
    const dd=document.createElement('dd');dd.textContent=value;
    summary.append(dt,dd);
  });
  form.hidden=true;result.hidden=false;result.focus();
});
document.getElementById('edit-request').addEventListener('click',()=>{
  result.hidden=true;form.hidden=false;form.elements.customer.focus();
});
