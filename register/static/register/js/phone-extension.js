const ext = document.getElementById("id-ext-label")
const ext_input = document.getElementById("id_contact-contact_phone_ext")
document.getElementById("id_ext-div").style.display = 'none'

if (ext_input.value) {
    extensionInput();
}

ext.onclick = extensionInput;

function extensionInput() {
    document.getElementById("id-ext-label").style.display = 'none';
    document.getElementById("id_ext-div").style.display = 'block'
    document.getElementById("id_contact-contact_phone_ext").focus();
}