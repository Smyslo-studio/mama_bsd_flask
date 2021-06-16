var $add = document.getElementsByClassName('add')[0];
var $form = document.getElementsByClassName('form')[0];
$add.addEventListener('click', function(event) {
  var $input = document.createElement('input');
  $input.type = 'text';
  $input.placeholder = 'Кол-во';
  $input.classList.add('amount');
  $form.insertBefore($input, $add);
});