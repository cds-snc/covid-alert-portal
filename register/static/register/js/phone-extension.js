const extensionLink = document.getElementById("add-extension-link")
const extensionInput = document.getElementById("id_contact-contact_phone_ext")
const extensionInputContainer = document.getElementById("extension-part")

if (extensionInput.value) {
    extensionInputContainer.classList.remove("hidden")
    extensionLink.classList.add("hidden")
}

extensionLink.onclick = showExtensionInput;

function showExtensionInput() {
    extensionInputContainer.classList.remove("hidden")
    extensionLink.classList.add("hidden")
    extensionInput.focus();
}