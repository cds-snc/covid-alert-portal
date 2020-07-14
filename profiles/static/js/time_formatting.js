document.addEventListener('DOMContentLoaded', function(){
  const expiry = moment().add(1, 'days');
  const lang = JSON.parse(document.getElementById('lang_code').textContent);
  if (lang == 'fr') {
      // example : 12 juillet a 18 h 12, heure locale
      document.getElementById('expiry-date').innerHTML = expiry.format('D MMMM');
      document.getElementById('expiry-time').innerHTML = expiry.format('HH [h] mm')+ ', heure locale';
  } else {
      // example : July 12 at 6:12 pm local time
      document.getElementById('expiry-date').innerHTML = expiry.format('MMMM D');
      document.getElementById('expiry-time').innerHTML = expiry.format('h:mm a') + ' local time';
  }
}, false);
