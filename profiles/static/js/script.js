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

// This prevents enter on the date picker from accidentally submitting the form when hitting enter on the month/year
document.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
      if (e.target.id.indexOf('DuetDateMonth') === 0 || e.target.id.indexOf('DuetDateYear') === 0){
        e.preventDefault();
        document.querySelectorAll("duet-date-picker")[0].hide();
      }
    }
});

var validationSummary = document.getElementById('validation-errors');

if (validationSummary) {
  validationSummary.focus();
}
