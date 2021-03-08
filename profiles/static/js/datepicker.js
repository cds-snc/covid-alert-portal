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
