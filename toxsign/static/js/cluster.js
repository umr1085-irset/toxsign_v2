$(document).ready(function() {
    $('#conditions').DataTable();

    if (has_signature){
      $('#signature').DataTable();
    }

    if (has_chem_enr){
      $.ajax({
        url: $("#chem2enr").attr("data-url"),
        type: "GET",
        dataType: 'json',
        success: function (data) {
            if (data['data'][0]['x'].length > 0){
                Plotly.newPlot('chem2enr', data['data'], data['layout']);
            }
        }
      });
    }

    if (has_gene_enr){
      $.ajax({
        url: $("#gene2enr").attr("data-url"),
        type: "GET",
        dataType: 'json',
        success: function (data) {
            if (data['data'][0]['x'].length > 0){
                Plotly.newPlot('gene2enr', data['data'], data['layout']);
            }
        }
      });
    }

});
