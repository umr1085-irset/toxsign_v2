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
    return false;
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
            window.location.href = data.redirect;
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

  var send_action = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      data: [{name: 'csrfmiddlewaretoken', value: token }],
      type: 'post',
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
            window.location.href = data.redirect;
        }
      }
    });
      return false;
  };

  /* Binding */
    $("#notification_list").on("click", ".js-refuse-invitation", loadForm);
    $("#notification_list").on("click", ".js-notif-action", send_action);
    $("#groups").on("click", ".js-create", loadForm);
    $("#superprojects").on("click", ".js-create", loadForm);
    $("#modal-group").on("submit", ".js-form", saveForm);
});
