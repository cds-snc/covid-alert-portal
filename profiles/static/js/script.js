// Find all of the links with the 'button' role and add a click event to them
var elements = document.querySelectorAll('a[role="button"]');

for (var i = 0, len = elements.length; i < len; i++) {
  elements[i].addEventListener('keydown', function (e) {
    if (e.keyCode == 32) {
      e.target.click();
      e.preventDefault();
    }
  });
}

