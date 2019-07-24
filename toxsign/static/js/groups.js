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
        console.log(data);
        if (data.form_is_valid) {
            window.location.reload();
        }
        else {
          $("#modal-group .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };


  /* Binding */
    $("#group_users").on("click", ".js-remove_user", loadForm);
    $("#modal-group").on("submit", ".js-user-remove-form", saveForm);

});
