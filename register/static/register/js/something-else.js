document.getElementById("id_category-category_description").parentElement.style.display = 'none'


const radios = document.getElementsByName("category-category")

for (var i = 0, len = radios.length; i < len; i++) {
    if (radios[i].checked) {
      if (radios[i].value === "other") {
        document.getElementById("id_category-category_description").parentElement.style.display = 'block';
      }
    }
    radios[i].onclick = function() {
      if (this.checked && this.value === "other") {
        document.getElementById("id_category-category_description").parentElement.style.display = 'block';
      } else {
        document.getElementById("id_category-category_description").parentElement.style.display = 'none';
      }
    };
  }


