const ext = document.getElementById("id-ext-label")
document.getElementById("id_ext-div").style.display = 'none'



ext.onclick = function() {
    document.getElementById("id-ext-label").style.display = 'none';
    document.getElementById("id_ext-div").style.display = 'block'
}