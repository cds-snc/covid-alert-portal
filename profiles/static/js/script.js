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

// get user's timezone
var tzInput = document.querySelector("#tz-offset");
if (tzInput) {
  var now = new Date();
  var timezoneOffset = now.getTimezoneOffset();
  tzInput.setAttribute("value", timezoneOffset);
}