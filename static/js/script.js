let x = 0;

function addInput() {
    let str = '<label><input type="text" name="ingredient' + (x + 1) +'" required></label> <label><input type="text" name="quantity' + (x + 1) + '" required></label>' + '<div id="input' + (x + 1) + '"></div>';
    document.getElementById('input' + x).innerHTML = str;
    x++;
}