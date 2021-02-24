const pickers = document.querySelectorAll("duet-date-picker")

pickers.forEach(function(picker) {

    // Get the index
    var i = picker.id.split('_')[2];

    // Replace the default input and button combo with our own 'show' button
    var button = document.querySelector("#date_"+ i);
    button.addEventListener('click', function (evt) {
        picker.show();
    });

    // Intercept the change events to populate our own form fields
    picker.addEventListener('duetChange', function(evt) {
        let toks = evt.detail.value.split('-');
        document.querySelector('#id_day_' + i).value = toks[2];
        document.querySelector('#id_month_' + i).value = toks[1];
        document.querySelector('#id_year_' + i).value = toks[0];
    });

    // Adjust the language if necessary (default English)
    const language = picker.getAttribute("language");
    if (language == 'fr') {
        picker.localization = {
            buttonLabel: "Choose date",
            prevMonthLabel: "Previous month",
            nextMonthLabel: "Next month",
            monthSelectLabel: "Month",
            yearSelectLabel: "Year",
            closeLabel: "Close dialog",
            keyboardInstruction: "You can use arrow keys to navigate dates",
            calendarHeading: "Select date",
            dayNames: [
              "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
              "Friday", "Saturday"
            ],
            monthNames: [
              "January", "February", "March", "April",
              "May", "June", "July", "August",
              "September", "October", "November", "December"
            ],
            monthNamesShort: [
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ],
            locale: "ca-FR",
        }
    }
});
