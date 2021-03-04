// gives CORS errors, but this is the one we apparently should use?:
// const url = 'https://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/AutoComplete/v1.00/wsdlnew.ws';

const key = 'BC76-EY79-GM26-BZ52'

/**
 * Just a wrapper around xhr for convenience.
 * @param {string} method 
 * @param {string} url 
 * @param {string} params 
 * @param {function} callback 
 */
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

/**
 * Ajax autocomplete from Canada Post Address Complete API
 * @param {string} query 
 * @param {functino} callback 
 */
function autocomplete(query, callback) {
    // autocomplete url
    const url = 'https://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/AutoComplete/v1.00/json3.ws'

    let params = '';
    params += "&Key=" + encodeURIComponent(key);
    params += "&SearchTerm=" + encodeURIComponent(query);
    params += "&Country=" + encodeURIComponent('CAN')

    xhr('post', url, params, function(response) {
        if (response.Items.length == 0) {
            // TODO: handle this sitch
            console.log("no results");
        } else {
            const results = response.Items.map(function(result) {
                return {
                    'id': result['Id'],
                    'name': result['Text'],
                    'description': result['Description'],
                    'retrievable': result['IsRetrievable']
                }
            })
            callback(results)
        }
    })
}

/**
 * Get the address details from Canada Post RetrieveById API
 * @param {string} id 
 */
function getDetails(id, callback) {
    const url = 'https://ws1.postescanada-canadapost.ca/AddressComplete/Interactive/RetrieveById/v1.00/json3.ws';

    let params = '';
    params += "&Key=" + encodeURIComponent(key);
    params += "&Id=" + encodeURIComponent(id);

    xhr('post', url, params, function(response) {
        if (response.Items.length == 0) {
            // TODO: handle this sitch
            console.log("no results");
        } else {
            const results = response.Items;

            const line1 = results.find(obj => {
                return obj.FieldGroup === 'Common' && obj.FieldName === 'Line1'
            });

            const city = results.find(obj => {
                return obj.FieldGroup === 'Common' && obj.FieldName === 'City'
            })

            const province = results.find(obj => {
                return obj.FieldGroup === 'Common' && obj.FieldName === 'ProvinceCode'
            })

            const postal = results.find(obj => {
                return obj.FieldGroup === 'Common' && obj.FieldName === 'PostalCode'
            })

            const address = {
                'line1': line1.FormattedValue,
                'city': city.FormattedValue,
                'province': province.FormattedValue,
                'postal': postal.FormattedValue
            };

            callback(address);
        }
    })
}

accessibleAutocomplete({
    element: document.querySelector('#address-autocomplete-container'),
    id: 'address-autocomplete', // To match it to the existing <label>.
    source: autocomplete,
    name: 'address-address',
    onConfirm: function(confirmed) {
        if(typeof confirmed !== 'undefined') {
            getDetails(confirmed.id, function(address) {
                document.getElementsByName("address-address")[0].value = address.line1;
                document.getElementsByName("address-city")[0].value = address.city;
                document.getElementsByName("address-province")[0].value = address.province;
                document.getElementsByName("address-postal_code")[0].value = address.postal;
            })
        }
    },
    minLength: 2,
    confirmOnBlur: false,
    defaultValue: document.getElementById("autocomplete-hidden-address").value,
    templates: {
        suggestion: function(item) {
            if(typeof item !== 'object') {
                return ''
            }
            return item.name + ' ' + item.description
        },
        inputValue: function (item) {
            if(typeof item !== 'object') {
                return ''
            }
            return item.name;
        }
    }
})