document.addEventListener("DOMContentLoaded", function () {
  var expiry = moment().add(1, "days");
  var lang = JSON.parse(document.getElementById("lang_code").textContent);

  if (lang == "fr") {
    // example : 12 juillet a 18 h 12, heure locale
    document.getElementById("expiry-datetime").innerHTML = expiry.format("D MMMM") + " à " + expiry.format("HH [h] mm") + ", heure locale";
  } else {
    // example : July 12 at 6:12 pm local time
    document.getElementById("expiry-datetime").innerHTML = expiry.format("MMMM D") + " at " + expiry.format("h:mm a") + " local time";
  }
}, false);

