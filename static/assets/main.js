// Disabling form submissions if there are invalid fields
(function () {
    'use strict'
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation')
  
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
      .forEach(function (form) {
        form.addEventListener('submit', function (event) {
          if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
          }
  
          form.classList.add('was-validated')
        }, false)
      })
  })()

function changeTextareaValid(){
  var textarea_valid = document.getElementById("text")
  var e = document.querySelector('input[name="plotRadio"]:checked').value;
  if( e=="text" ){
    textarea_valid.setAttribute('required','required');
  }
  else{
    textarea_valid.removeAttribute('required');
  }
}

function changeOptions(data) { 
  var select = document.getElementById('report-selector');
  // Add options
	for (var i in data) {
        select.options[select.options.length] = new Option(data[i]);   
	}
    $("#report-selector").selectpicker("refresh"); //用select變數不行
}

function showModal(){
  //$('#uploadModal').modal('show');
  var modal = new bootstrap.Modal(document.getElementById('uploadModal'));
  modal.show();
}

function hideModal(){
  //$('#uploadModal').modal('hide');
  var modal = new bootstrap.Modal(document.getElementById('uploadModal'));
  modal.hide();
}

function initModal(){
  document.getElementById('upload-alert').innerHTML = "Please choose a qualified file.";
}

// Let selectPicker can be dynamically changed
$.ajax({
  url: "/showReports",
  success: function(data){ 
      changeOptions(data.files);
  }
})
// .done(function(){
//   initModal();
// });

// Alert after uploading file
// $("#upload-btn").on('click', function(){
//   $.ajax({
//     url: "/upload",
//     success: showModal(),
//     // async: false,
//   })
// })

$(document).ready(function(){
  changeTextareaValid();
  $("input[name='plotRadio']").change(changeTextareaValid);
  //document.getElementById("upload-alert").innerHTML = "Please choose a qualified file.";
});

