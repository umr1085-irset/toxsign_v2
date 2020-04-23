$(function () {

    var showInfo = function () {
      var val = $(this).val();
      $(".model_description").hide()
      $("#model_" + val).show()
    };

    $('#id_model').on('change', showInfo);
});
