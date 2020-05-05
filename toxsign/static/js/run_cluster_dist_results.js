$(function () {


    jQuery.extend( jQuery.fn.dataTableExt.oSort, {
        "formatted-num-pre": function ( a ) {
            a === "nan" ? 0 : a;
            return parseFloat( a );
        },
        "formatted-num-asc": function ( a, b ) {
            return a - b;
        },
        "formatted-num-desc": function ( a, b ) {
            return b - a;
        }
    });



    var table = $('#results').DataTable({
        "pageLength": 5,
        "scrollX": true,
        "order": [[ 1, order_type]],
        "bFilter": false,
        "columnDefs": [{ type: 'formatted-num', targets: 1 }]
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
