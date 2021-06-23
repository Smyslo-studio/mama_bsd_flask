let x = 0;


function addInput() {
    let str2 = '<tr id="input' + x + '"></tr>';
    document.getElementById('inputing').innerHTML += str2;
    
    let str = '<td><label><input type="text" name="ingredient' + (x + 1) +'"></label></td><td><label><input type="text" name="quantity' + (x + 1) + '"></label></td>';
    document.getElementById('input' + x).innerHTML = str;
    x++;
}


function addIng(ingredient, quantity) {
    let str2 = '<tr id="input' + x + '"></tr>';
    document.getElementById('inputing').innerHTML += str2;
    
    let str = '<td><label><input type="text" name="ingredient' + (x + 1) +'" value="' + ingredient + '"></label></td><td><label><input type="text" name="quantity' + (x + 1) + '" value="' + quantity + '"></label></td>';
    document.getElementById('input' + x).innerHTML = str;
    x++;
}