$(function () {


    $.fn.dataTable.ext.search.push(
        function( settings, data, dataIndex ) {
            if ( settings.nTable.id !== 'results' ) {
                return true;
            }
            var min = parseFloat( $('#min').val(), 0.5 );
            var proba = parseFloat( data[1] ) || 0; // use data for the age column

            if  (( isNaN( min ) ) || ( min <= proba ))
            {
                return true;
            }
            return false;
        }
    );

    var table = $('#results').DataTable({
        "order": [[ 4, "desc" ]],
        "pageLength": 5,
        "dom": 'l<"wrapper">rtip'

    });
    $("div.wrapper").css("float", "right");
    $("div.wrapper").html('<label for="min">Probability cutoff </label> <input type="text" id="min" name="min" value="0.0" placeholder="0.0">');

    $(".wrapper").on('keyup', '#min', function() {
        console.log("test")
        table.draw();
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
