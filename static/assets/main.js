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

function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

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

function InitOptions(data) { 
  var company = getCookie("company");
  var year = getCookie("year");
  var type = getCookie("type");
  // console.log(company)
  // console.log(year)
  // console.log(type)

  var company_select = document.getElementById('company-selector');
  var year_select = document.getElementById('year-selector');
  var report_select = document.getElementById('report-selector');
  var company_year = new Array();
  var company_type = {};
  
  $('#company-selector').empty();
  $('#year-selector').empty();
  $('#report-selector').empty();
  // 用 subindustry 分開
  // $.each(data.category, function(key, value){
  //     var group = document.createElement('optgroup');
  //     group.setAttribute('label', key)
  //     for (var i in value) {
  //       console.log(value[i])
  //       group.append(new Option(value[i]));
  //     }
  //     company_select.appendChild(group);
  // });

  for (var i in data.company) {
    company_select.options[company_select.options.length] = new Option(data.company[i]);   
	}
  for (const i of data.files) {
    if (i.includes(company_select.options[0].value)){
      company_year.push(i.split('-')[0]);
      if (!(i.split('-')[0] in company_type)){
        company_type[i.split('-')[0]] = [i.split('-')[2]];
      }
      else{
        company_type[i.split('-')[0]].push(i.split('-')[2]);
      }
    }
	}
  for (var i of new Set(company_year)) {
    year_select.options[year_select.options.length] = new Option(i);   
	}
  if ( type==""){
    for (var i of new Set(company_type[company_year[0]])) {
      report_select.options[report_select.options.length] = new Option(i);   
    }
  }
  else{
    // report_select.options[report_select.options.length] = new Option(type);  
    $.ajax({
      type: 'POST',  // http method
      url: '/getReportList',
      data: { 'company': company, 'year': year },  // data to submit
      dataType: 'json',
      success: function (res) {
          var report_select = document.getElementById('report-selector');
          for( i in res.type){
            report_select.options[report_select.options.length] = new Option(res.type[i]); 
          }
          $("#report-selector").val(type);
          $("#report-selector").selectpicker("refresh");
      }
    });
  }

  //report_select.selectedIndex = 1
  if (company!="") {
    $("#company-selector").val(company);
  }
  if (year!="") {
    $("#year-selector").val(year);
  }
  //要放最下面
  $("#company-selector").selectpicker("refresh"); //用select變數不行
  $("#year-selector").selectpicker("refresh");
  $("#report-selector").selectpicker("refresh");
}

function ChangeOptions(data, change_option) { 
  console.log("foo")
  var company_select = document.getElementById('company-selector').value;
  var year_select = document.getElementById('year-selector');
  var report_select = document.getElementById('report-selector');
  var company_year = new Array();
  var company_type = new Array();
  var search_name = company_select

  $('#report-selector').empty();
  if (change_option == "company"){
    $('#year-selector').empty();
  }
  else{
    year_select = year_select.value
    search_name = year_select + '-' + company_select  
  }
  for (const i of data.files) {
    if (i.includes(search_name)){
      company_year.push(i.split('-')[0]);
      company_type.push(i.split('-')[2]);
    }
  }
  if (change_option == "company"){
    for (var i of new Set(company_year)) {
      year_select.options[year_select.options.length] = new Option(i);   
    }
    setCookie("year", $("#year-selector").val());
    $("#year-selector").selectpicker("refresh");
  }
  for (var i of new Set(company_type)) {
    report_select.options[report_select.options.length] = new Option(i);   
  }
  // 用 subindustry 分開 To Do
  // $.each(data.category, function(key, value){
  //     var group = document.createElement('optgroup');
  //     group.setAttribute('label', key)
  //     for (var i in value) {
  //       console.log(value[i])
  //       group.append(new Option(value[i]));
  //     }
  //     company_select.appendChild(group);
  // });
  setCookie("type", $("#report-selector").val());
  $("#report-selector").selectpicker("refresh");
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
      console.log("Success")
      InitOptions(data);
  }
})

$('#company-selector').change(function(){
  $.ajax({
    url: "/showReports",
    success: function(data){ 
      ChangeOptions(data, "company");
    }
  })
  setCookie("company", this.value);
});

$('#year-selector').change(function(){
  $.ajax({
    url: "/showReports",
    success: function(data){ 
      ChangeOptions(data, "year");
    }
  })
  setCookie("year", this.value);
});

$('#report-selector').change(function(){
  setCookie("type", this.value);
});

$(document).ready(function(){
  changeTextareaValid();
  $("input[name='plotRadio']").change(changeTextareaValid);
  //document.getElementById("upload-alert").innerHTML = "Please choose a qualified file.";
});

$(window).bind('unload', function(){
  changeTextareaValid();
  $("input[name='plotRadio']").change(changeTextareaValid);            
});
