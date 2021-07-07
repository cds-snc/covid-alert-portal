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

document.cookie = 'browserTimezone=' + Intl.DateTimeFormat().resolvedOptions().timeZone + '; path=/';

function navBack() {
  window.history.back();
}

backInlineLinks = document.getElementsByClassName('back-inline-link');
for (let i=0; i< backInlineLinks.length; i++){
  backInlineLinks[i].addEventListener('click', navBack);
}


var startTimeControl = document.getElementById('id_start_time');
if (startTimeControl !== null){
  // Keep a fresh copy of the end time array elements
  var endTimeControlClone = document.getElementById('id_end_time').cloneNode(true);

  function getTimeIntFromElement(value){
    return parseInt(value.replace(/:/g,""));
  }

  // Listener captures selected time and currently selected end time
  // Re-clones array of end times to start with fresh list, deletes any items in list before selected start time
  // End time is reselected if still in list, else pushed to next available end time
  startTimeControl.addEventListener('change', function (ele){
    var startval = getTimeIntFromElement(ele.target.value);
    endTimeControl = document.getElementById('id_end_time');
    var selectedEndValue = endTimeControl.value;
    var replacementClone = endTimeControlClone.cloneNode(true);
    endTimeControl.parentNode.replaceChild(replacementClone, endTimeControl);
    endTimeControl = document.getElementById('id_end_time');
    for(var i = 0; i< endTimeControl.length-1; i++){
      if (getTimeIntFromElement(endTimeControl[i].value) < startval){
        endTimeControl.remove(i);
        i--;
      }
    }
    for(var i = 0; i < endTimeControl.length; i++){
      if(endTimeControl[i].value == selectedEndValue){
        endTimeControl.options[i].selected = true;
        break;
      }else{
        endTimeControl.options[0].selected = true;
      }
    }
  });
}
