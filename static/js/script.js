let x = 0;

function addIng(ingredient, quantity, quantity_spoon) {
    let str2 = '<div id="input' + x + '"></div>';
    document.getElementById('inputing').innerHTML += str2;

    let id = "'input" + x + "'"

    let str3 = '<button class="tag is-delete" onclick="delInput(' + id + ')"></button>'
    let str = '<label><input type="text" name="ingredient' + (x + 1) + '" value="' + ingredient + '"></label><label><input type="text" name="quantity' + (x + 1) + '" value="' + quantity + '"></label><label><input type="text" name="quantity_spoon' + (x + 1) + '" value="' + quantity_spoon + '"></label>';
    
    document.getElementById('input' + x).innerHTML = str+str3;
    x++;
}

function search_generate_url(type, search_content) {
    if (!type) {
        var select = document.getElementById('type_input')
        var type = select.options[select.selectedIndex].value;
    }
    if (!search_content) {
        var search_content = document.getElementsByClassName('search_input')[0].value
    }
    console.log(type)
    console.log(search_content)
    let url = 'search?' + type + '=' + search_content;
    location.assign(url);
}

function addInput() {
    var str = '<label><input type="text" name="ingredient' + (x + 1) + '"></label><label><input type="text" name="quantity' + (x + 1) + '"></label><label><input type="text" name="quantity_spoon' + (x + 1) + '"></label>';
    var div_var = document.createElement("div");
    div_var.innerHTML = str;
    document.getElementById('inputing').append(div_var);
    x++
}

function delInput(id) {
    document.getElementById(id).remove();
}