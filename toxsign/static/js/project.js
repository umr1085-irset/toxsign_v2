$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});

$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-group").modal("show");
      },
      success: function (data) {
        $("#modal-group .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
            window.location.href = data.redirect
        }
        else {
          $("#modal-group .modal-content").html(data.html_form);
          if (data.error){
            $("#modal-group .modal-content #error").html(data.error);
          }
        }
      }
    });
    return false;
  };

  /* Binding */
    $("#button-div").on("click", ".js-make-public", loadForm);
    $("#modal-group").on("submit", ".js-make-public-form", saveForm);
});