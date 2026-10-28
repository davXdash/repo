'use strict';
const form=document.querySelector('#unlock'),status=document.querySelector('#authstatus'),button=document.querySelector('#unlockbutton');
const bytes=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
form.addEventListener('submit',async event=>{
 event.preventDefault();button.disabled=true;status.textContent='Sammlung wird geöffnet …';
 try{
  if(!window.crypto?.subtle)throw new Error('crypto');
  let response;try{response=await fetch('catalog.enc.json',{cache:'no-store'});if(!response.ok)throw Error();}catch{throw new Error('network')}
  let payload;try{payload=await response.json()}catch{throw new Error('network')}
  const material=await crypto.subtle.importKey('raw',new TextEncoder().encode(document.querySelector('#password').value),'PBKDF2',false,['deriveKey']);
  const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:bytes(payload.salt),iterations:payload.iterations,hash:'SHA-256'},material,{name:'AES-GCM',length:256},false,['decrypt']);
  let plaintext;try{plaintext=await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(payload.iv)},key,bytes(payload.ciphertext))}catch{throw new Error('password')}
  window.findsCatalog=JSON.parse(new TextDecoder().decode(plaintext));
  const script=document.createElement('script');script.src='app.js';
  await new Promise((resolve,reject)=>{script.onload=resolve;script.onerror=reject;document.body.append(script)});
  document.querySelector('#password').value='';document.querySelector('#gate').hidden=true;document.querySelector('#catalog').hidden=false;document.body.classList.remove('locked');document.querySelector('#query').focus();
 }catch(error){status.textContent=error.message==='password'?'Das Passwort stimmt nicht. Bitte erneut versuchen.':error.message==='crypto'?'Bitte die Seite über HTTPS in einem aktuellen Browser öffnen.':'Die Sammlung konnte nicht geladen werden. Bitte erneut versuchen.';}
 finally{button.disabled=false;}
});
