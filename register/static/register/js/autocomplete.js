// const url = 'http://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/Find/v2.10/wsdlnew.ws';
// const url = 'https://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/Find/v2.10/json3.ws';

// gives CORS errors, but this is the one we should use:
// const url = 'https://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/AutoComplete/v1.00/wsdlnew.ws';

// autocomplete url
const url = 'http://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/AutoComplete/v1.00/json3.ws'



const key = 'BC76-EY79-GM26-BZ52'

var results = [];

function hinter(query, populateResults) {    
    var params = '';
    params += "&Key=" + encodeURIComponent(key);
    params += "&SearchTerm=" + encodeURIComponent(query);
    params += "&Country=" + encodeURIComponent('CAN')

    var http = new XMLHttpRequest();
    http.open('POST', url, true);
    http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    http.onreadystatechange = function() {
        if(http.readyState == 4 && http.status == 200) {
            var response = JSON.parse(http.responseText);
            // Test for an error
            if (response.Items.length == 1 && typeof(response.Items[0].Error) != "undefined") {
                // Show the error message
                console.log(response.Items[0].Description);
            } else {
                // Check if there were any items found
                if (response.Items.length == 0)
                    alert("Sorry, there were no results");
                else {
                    console.log(response.Items)
                    var results = response.Items.map(function(result) {
                        return {
                            'name': result['Text'],
                            'id': result['Id']
                        }
                    })
                    console.log(results);
                    populateResults(results)
                }
        }
        }
    }
    http.send(params);
}


accessibleAutocomplete({
    element: document.querySelector('#my-autocomplete-container'),
    id: 'my-autocomplete', // To match it to the existing <label>.
    source: hinter,
    onConfirm: function(confirmed) {
        console.log(confirmed)
    },
    templates: {
        suggestion: function(item) {
            return item.name
        },
    }
})

  // var ac_input = document.getElementById('my-autocomplete');
  //   ac_input.addEventListener("keyup", function(event){hinter(event)});


  /* SAMPLE FROM CANADA POST
var params = '';
    params += "&Key=" + encodeURIComponent(Key);
    params += "&SearchTerm=" + encodeURIComponent(SearchTerm);
    params += "&LastId=" + encodeURIComponent(LastId);
    params += "&SearchFor=" + encodeURIComponent(SearchFor);
    params += "&Country=" + encodeURIComponent(Country);
    params += "&LanguagePreference=" + encodeURIComponent(LanguagePreference);
    params += "&MaxSuggestions=" + encodeURIComponent(MaxSuggestions);
    params += "&MaxResults=" + encodeURIComponent(MaxResults);
var http = new XMLHttpRequest();
http.open('POST', url, true);
http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
http.onreadystatechange = function() {
  if(http.readyState == 4 && http.status == 200) {
      var response = JSON.parse(http.responseText);
      // Test for an error
      if (response.Items.length == 1 && typeof(response.Items[0].Error) != "undefined") {
        // Show the error message
        alert(response.Items[0].Description);
      }
      else {
        // Check if there were any items found
        if (response.Items.length == 0)
            alert("Sorry, there were no results");
        else {
            // PUT YOUR CODE HERE
            //FYI: The output is an array of key value pairs (e.g. response.Items[0].Id), the keys being:
            //Id
            //Text
            //Highlight
            //Cursor
            //Description
            //Next
        }
    }
  }
}
http.send(params);
*/