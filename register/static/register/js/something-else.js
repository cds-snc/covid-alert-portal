document.getElementById("id_category-category_description").parentElement.style.display = 'none'

const categorySelect = document.getElementById('id_category-category');
if (categorySelect.value === 'other'){
  document.getElementById("id_category-category_description").parentElement.style.display = 'block';
}
categorySelect.onchange = function (e) {
  if (this.value === 'other') {
    document.getElementById("id_category-category_description").parentElement.style.display = 'block';
  } else {
    document.getElementById("id_category-category_description").value = "";
    document.getElementById("id_category-category_description").parentElement.style.display = 'none';
  }
}
// Add optgroup to allow text zoom in mobile html control
const optGroup = document.createElement("optgroup");
categorySelect.append(optGroup);
