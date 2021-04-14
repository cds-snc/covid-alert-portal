// Find all of the links with the 'button' role and add a click event to them
var buttonLinks = document.querySelectorAll('a[role="button"]')

for (var i = 0, len = buttonLinks.length; i < len; i++) {
  buttonLinks[i].addEventListener("keydown", function (e) {
    if (e.keyCode == 32) {
      e.target.click()
      e.preventDefault()
    }
  })
}

// Add disabled to buttons after click
var form = document.querySelector("main form")

if (form) {
  form.addEventListener("submit", function (e) {
    setTimeout(function () { // timeout for the JS event loop to allow submit post data on pre-disabled buttons
      form.querySelector("button").disabled = true;
    }, 1)
  })
}

// get user's timezone
var tzInput = document.getElementById("id_timezone");
if (tzInput) {
  tzInput.value = Intl.DateTimeFormat().resolvedOptions().timeZone;
}
