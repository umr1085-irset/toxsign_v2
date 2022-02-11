var get_details = function(form_id) {
    var div = "#" + form_id;
    var result_div = div + "-results";
    $.ajax({
        url : $(div).attr("action"),
        type: 'POST',
        data : $(div).serialize(),
        success: function(response){
            $(result_div).html(response.html);
        }
    });
}
