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
            window.location.href = correct_url();
        }
        else {
          $("#modal-group .modal-content").html(data.html_form);
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
            window.location.href = correct_url();
        }
      }
    });
      return false;
  };

  var correct_url = function () {
    var url = window.location.href;
    url = url.split("?")[0];
    return url + "?notification=true"
  }

  /* Binding */
    $("#notification_list").on("click", ".js-refuse-invitation", loadForm);
    $("#modal-group").on("submit", ".js-dismiss-notif-form", saveForm);
    $("#notification_list").on("click", ".js-notif-action", send_action);
});
