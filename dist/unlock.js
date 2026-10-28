'use strict';
const form=document.querySelector('#unlock'),status=document.querySelector('#authstatus'),button=document.querySelector('#unlockbutton');
const bytes=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
// A non-extractable WebCrypto key survives tab suspension; the password is never stored.
function deviceKey(mode,value){return new Promise((resolve,reject)=>{const req=indexedDB.open('finds-device-unlock',1);req.onupgradeneeded=()=>req.result.createObjectStore('keys');req.onerror=()=>reject(req.error);req.onsuccess=()=>{const db=req.result,tx=db.transaction('keys',mode==='get'?'readonly':'readwrite'),store=tx.objectStore('keys');const action=mode==='get'?store.get('material'):mode==='delete'?store.delete('material'):store.put(value,'material');action.onsuccess=()=>{if(mode==='get')resolve(action.result)};tx.oncomplete=()=>{db.close();if(mode!=='get')resolve()};tx.onerror=()=>reject(tx.error)}})}
window.forgetFindsDevice=async()=>{await deviceKey('delete');location.reload()};
async function openCollection(savedMaterial){button.disabled=true;status.textContent='Sammlung wird geöffnet …';
 try{
  if(!window.crypto?.subtle)throw new Error('crypto');
  let response;try{response=await fetch('catalog.enc.json',{cache:'no-store'});if(!response.ok)throw Error();}catch{throw new Error('network')}
  let payload;try{payload=await response.json()}catch{throw new Error('network')}
  const material=savedMaterial||await crypto.subtle.importKey('raw',new TextEncoder().encode(document.querySelector('#password').value),'PBKDF2',false,['deriveKey']);
  const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt:bytes(payload.salt),iterations:payload.iterations,hash:'SHA-256'},material,{name:'AES-GCM',length:256},false,['decrypt']);
  let plaintext;try{plaintext=await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(payload.iv)},key,bytes(payload.ciphertext))}catch{throw new Error('password')}
  window.findsCatalog=JSON.parse(new TextDecoder().decode(plaintext));
  try {
   const indexResponse=await fetch('imports/index.json',{cache:'no-store'});
   if(indexResponse.ok){
    const index=await indexResponse.json();window.findsCatalog.importReports=index.reports||[];
    if(index.files?.length){
     const ring=await (await fetch('keyring.enc.json')).json();
     const ringKey=await crypto.subtle.deriveKey({name:'PBKDF2',salt:bytes(ring.salt),iterations:ring.iterations,hash:'SHA-256'},material,{name:'AES-GCM',length:256},false,['decrypt']);
     const privateBytes=await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(ring.iv)},ringKey,bytes(ring.ciphertext));
     const privateKey=await crypto.subtle.importKey('pkcs8',privateBytes,{name:'RSA-OAEP',hash:'SHA-256'},false,['decrypt']);
     for(const file of index.files){
      if(!/^[a-f0-9]+\.json$/.test(file))continue;
      try {
       const envelope=await (await fetch('imports/'+file,{cache:'no-store'})).json();
       const aesRaw=await crypto.subtle.decrypt({name:'RSA-OAEP'},privateKey,bytes(envelope.key));
       const aes=await crypto.subtle.importKey('raw',aesRaw,'AES-GCM',false,['decrypt']);
       const decoded=await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(envelope.iv)},aes,bytes(envelope.ciphertext));
       const content=envelope.compression==='gzip'?await new Response(new Blob([decoded]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer():decoded;
       const imported=JSON.parse(new TextDecoder().decode(content));
       const knownSource=window.findsCatalog.sources.find(s=>s.id===imported.source.id);
       if(knownSource)Object.assign(knownSource,imported.source,{status:'Skriptimport erfolgreich'});else window.findsCatalog.sources.push({...imported.source,status:'Skriptimport erfolgreich'});
       const importedUrls=new Set(imported.products.map(p=>p.url));
       window.findsCatalog.products=window.findsCatalog.products.filter(p=>p.source!==imported.source.id||!importedUrls.has(p.url)).concat(imported.products);
      }catch{window.findsCatalog.importReports.push({source:file,status:'blocked',reason:'Importdatei konnte nicht geöffnet werden; bisherige Daten bleiben erhalten.'})}
     }
    }
    window.findsCatalog.note='Tabellenpreise ohne Versand. Währungsangaben werden nur bei eindeutiger Kennzeichnung umgerechnet. Fehlende Bilder, unklare Preise und nicht erkannte Links stehen im Importbericht.';
   }
  }catch {window.findsCatalog.importReports=[{source:'Skriptimporte',status:'blocked',reason:'Zusätzliche Importe gerade nicht erreichbar; bisherige Sammlung geladen.'}]}

  const script=document.createElement('script');script.src='app.js?v=gallery4';
  await new Promise((resolve,reject)=>{script.onload=resolve;script.onerror=reject;document.body.append(script)});
  if(!savedMaterial&&document.querySelector('#remember-device').checked){try{await deviceKey('put',material)}catch{status.textContent='Dieses Gerät konnte nicht gespeichert werden.'}}
  document.querySelector('#password').value='';document.querySelector('#gate').hidden=true;document.querySelector('#catalog').hidden=false;document.body.classList.remove('locked');document.querySelector('#query').focus();
 }catch(error){if(savedMaterial&&error.message==='password'){try{await deviceKey('delete')}catch{}}status.textContent=error.message==='password'?'Das Passwort stimmt nicht. Bitte erneut versuchen.':error.message==='crypto'?'Bitte die Seite über HTTPS in einem aktuellen Browser öffnen.':'Die Sammlung konnte nicht geladen werden. Bitte erneut versuchen.';}
 finally{button.disabled=false;}
}
form.addEventListener('submit',event=>{event.preventDefault();openCollection()});
deviceKey('get').then(key=>{if(key)openCollection(key)}).catch(()=>{});
