// Find all of the links with the 'button' role and add a click event to them
var buttonLinks = document.querySelectorAll('a[role="button"]');

for (var i = 0, len = buttonLinks.length; i < len; i++) {
  buttonLinks[i].addEventListener("keydown", function (e) {
    if (e.keyCode == 32) {
      e.target.click();
      e.preventDefault();
    }
  });
} 

// Add disabled to buttons after click
var form = document.querySelector("main form");

if (form) {
  form.addEventListener("submit", function (e) {
    form.querySelector("button").disabled = true;
  });
}

var radios = document.getElementsByName('otk-sent-next');
radios.forEach(function(radio) {
    radio.addEventListener('click', function(e) {
        let value = document.querySelector('input[name="otk-sent-next"]:checked').value;
        document.getElementById('otk_sms_sent_next').href = radio.value;
    });
});
