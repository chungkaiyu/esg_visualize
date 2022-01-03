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


function changeOptions(data) {
    
    var select = document.getElementById('report-selector');
    // Add options
	for (var i in data) {
        select.options[select.options.length] = new Option(data[i]);   
	}
    $("#report-selector").selectpicker("refresh"); //用select變數不行
}

function alertBox(info){
    $("#upload-alert p").val(info);
    console.log("???")
    $("#uploadModal").attr("aria-hidden", false);
}

// Let selectPicker can be dynamically changed
$.ajax({
    url: "/showReports",
    success: function(data){ 
        changeOptions(data.files); 
    }
});

// Alert funciton
$.ajax({
    url: "/alert",
    success: function(info){ 
        alertBox(info);
    }
});
