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

$(document).ready(function(){
  changeTextareaValid();
  $("input[name='plotRadio']").change(changeTextareaValid);
});

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

// Let selectPicker can be dynamically changed
$.ajax({
    url: "/showReports",
    success: function(data){ 
        changeOptions(data.files);
        // upload();
    }
});

// Alert after uploading file
function upload(){
  console.log("???")
  $.ajax({
    url: "/upload",
    success: function(){ 
      myModal.show();
    }
  });
}

var myModal = new bootstrap.Modal(document.getElementById('uploadModal'));