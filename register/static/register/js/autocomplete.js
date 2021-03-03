// gives CORS errors, but this is the one we apparently should use?:
// const url = 'https://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/AutoComplete/v1.00/wsdlnew.ws';

const key = 'BC76-EY79-GM26-BZ52'

// just a wrapper around xhr
const xhr = function(method, url, params, callback) {
    const xhr = new XMLHttpRequest();
    
    xhr.onreadystatechange = function() {
        if ( xhr.readyState === 4 && xhr.status == 200) {
            callback(JSON.parse(xhr.responseText));
        }            
    };

    xhr.open( method, url, true );
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    
    xhr.send(params);
}


function hinter(query, populateResults) {
    // autocomplete url
    const url = 'http://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/AutoComplete/v1.00/json3.ws'

    var params = '';
    params += "&Key=" + encodeURIComponent(key);
    params += "&SearchTerm=" + encodeURIComponent(query);
    params += "&Country=" + encodeURIComponent('CAN')

    xhr('post', url, params, function(response) {
        if (response.Items.length == 0) {
            // TODO: handle this sitch
            console.log("no results");
        } else {
            var results = response.Items.map(function(result) {
                return {
                    'id': result['Id'],
                    'name': result['Text'],
                    'description': result['Description'],
                    'retrievable': result['IsRetrievable']
                }
            })
            populateResults(results)
        }
    })
}

function details(id) {
    const url = 'http://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/RetrieveById/v1.00/json3.ws';

    var params = '';
    params += "&Key=" + encodeURIComponent(key);
    params += "&Id=" + encodeURIComponent(id);
    // params += "&Application=" + encodeURIComponent(Application);

    xhr('post', url, params, function(response) {
        if (response.Items.length == 0) {
            // TODO: handle this sitch
            console.log("no results");
        } else {
            var results = response.Items;

            var line1 = results.find(obj => {
                return obj.FieldGroup === 'Common' && obj.FieldName === 'Line1'
            });

            var city = results.find(obj => {
                return obj.FieldGroup === 'Common' && obj.FieldName === 'City'
            })

            var province = results.find(obj => {
                return obj.FieldGroup === 'Common' && obj.FieldName === 'ProvinceCode'
            })

            var postal = results.find(obj => {
                return obj.FieldGroup === 'Common' && obj.FieldName === 'PostalCode'
            })

            const address = {
                'line1': line1.FormattedValue,
                'city': city.FormattedValue,
                'province': province.FormattedValue,
                'postal': postal.FormattedValue
            };

            document.getElementsByName("address-address")[0].value = address.line1;
            document.getElementsByName("address-city")[0].value = address.city;
            document.getElementsByName("address-province")[0].value = address.province;
            document.getElementsByName("address-postal_code")[0].value = address.postal;
        }
    })
}


accessibleAutocomplete({
    element: document.querySelector('#address-autocomplete-container'),
    id: 'address-autocomplete', // To match it to the existing <label>.
    source: hinter,
    name: 'address-address',
    onConfirm: function(confirmed) {
        details(confirmed.id)
    },
    templates: {
        suggestion: function(item) {
            return item.name
        },
        inputValue: function (item) {
            return item ? item.name : ''
        }
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