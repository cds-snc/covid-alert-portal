let pickers = document.querySelectorAll("duet-date-picker");

// This Array.apply converts the nodelist to an array so IE can iterate with forEach
Array.apply(null,pickers).forEach(function(picker) {
    // Replace the default input and button combo with our own 'show' button
    var button = document.querySelector("#button_datepicker");
    button.addEventListener('click', function (evt) {
        picker.show();
    });

    // Intercept the change events to populate our own form fields
    picker.addEventListener('duetChange', function(evt) {
        let toks = evt.detail.value.split('-');
        document.querySelector('#id_day').value = toks[2];
        document.querySelector('#id_month').value = parseInt(toks[1]);
        document.querySelector('#id_year').value = toks[0];
    });

    // Adjust the language if necessary (default English)
    const language = picker.getAttribute("language");
    if (language == 'fr') {
        picker.localization = {
            buttonLabel: "Choisissez la date",
            prevMonthLabel: "Le mois précédent",
            nextMonthLabel: "Le mois prochain",
            monthSelectLabel: "Mois",
            yearSelectLabel: "An",
            closeLabel: "Fermer la boîte de dialogue",
            keyboardInstruction: "Vous pouvez utiliser les touches fléchées pour parcourir les dates",
            calendarHeading: "Sélectionner une date",
            dayNames: [
              "dimanche", "lundi", "mardi", "mercredi", "jeudi",
              "vendredi", "samedi"
            ],
            monthNames: [
              "janvier", "février", "mars", "avril",
              "mai", "juin", "juillet", "août",
              "septembre", "octobre", "novembre", "décembre"
            ],
            monthNamesShort: [
              "janv", "févr", "mars", "avril", "mai", "juin",
              "juil", "août", "sept", "oct", "nov", "déc"
            ],
            locale: "ca-FR",
        }
    }
});
