$(function () {

    var table = $('#results').DataTable({
        "pageLength": 5,
        "scrollX": true,
        "bFilter": false
    });

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
          $("#modal-group .modal-content").html(data.html);
        }
      });
    };

  /* Binding */
    $("#results").on("click", ".js-load-modal", loadForm);

});
