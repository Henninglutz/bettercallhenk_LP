
function scrollCarousel(delta){
  const track = document.querySelector('.track');
  if(!track) return;
  track.scrollBy({left: delta, behavior:'smooth'});
}

async function submitLead(e){
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  // very light validation
  if(!data.email || !data.whatsapp){ alert('Bitte E-Mail und WhatsApp-Nummer angeben.'); return false; }
  try{
    const res = await fetch('/api/subscribe', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data)});
    if(res.ok){ e.target.reset(); alert('Danke! Du bist für die ersten 100 vorgemerkt.'); }
    else{ window.location.href = 'mailto:beta@bettercallhenk.de?subject=Beta%20Anmeldung&body='+encodeURIComponent(JSON.stringify(data,null,2)); }
  }catch(_){
    window.location.href = 'mailto:beta@bettercallhenk.de?subject=Beta%20Anmeldung&body='+encodeURIComponent(JSON.stringify(data,null,2));
  }
  return false;
}