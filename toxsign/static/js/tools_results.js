$(function () {

  var filter_params = [];

  /* Functions */

    var add_param = function() {
        $("#error_field").html("");
        var arg_filter_type = $("#filter_type").val();
        var arg_filter_type_display = $("#filter_type option:selected").text();
        var arg_filter_adjust = $("#filter_adjust").val();
        var arg_filter_adjust_display = $("#filter_adjust option:selected").text();
        var arg_filter_number = $("#filter_number").val();
        var dict = { filter_type: arg_filter_type, filter_adjust: arg_filter_adjust, filter_number: arg_filter_number, type_display: arg_filter_type_display, adjust_display: arg_filter_adjust_display};
        filter_params.push(dict);
        $("#id_filters").show();
        //Reset fields
        reset_form();
        fill_html();
        return false;
    };

    var remove_param = function(){
        var value = $(this).attr("arg_value");
        filter_params.splice(value, 1);
        // Regenerate arguments
        fill_html();
        if(filter_params.length == 0){
            $("#id_filters").hide();
        }
        return false;
    };

    var show_results = function () {
        var url = window.location.href.split(/[?#]/)[0];
        var entity_type = $("#entity_select").val();
        if(filter_params.length >0){
            url += "?";
            var string= ""
            for (i=0; i < filter_params.length; i++){
                string += `filter=${filter_params[i]['filter_type']},${filter_params[i]['filter_adjust']},${filter_params[i]['filter_number']}&`
            }
            string = encodeURI(string.slice(0, -1));
            url += string;
        }
        window.location.href = url;
        return false;
    };

    var get_button = function(arg_number){
        return `<button class='btn btn-link btn-xs remove_arg' arg_value='${arg_number}'><i class='fas fa-trash'></i></button>`;

    }

    var fill_html = function(){
        var html = ""
        for (i=0; i < filter_params.length; i++){
            html += `(${filter_params[i]['type_display']} : ${filter_params[i]['adjust_display']} ${filter_params[i]['filter_number']}) ${get_button(i)} <br>`;
        }
        if (filter_params.length >0){
            html += "<button type='button' class='btn btn-danger clear_terms'>Clear <i class='fa fa-trash' aria-hidden='true'></i><br></button><br><br>"
        }
        $("#selected_filters").html(html);
    }

    var reset_form = function(){
        // Need to manually reset field if it's an ontology
        $('#filter_form').trigger("reset");
    }

    var full_form_clear = function(){
        filter_params = [];
        fill_html()
        $("#id_filters").hide();
        $('#filter_form').trigger("reset");
    }

  /* Binding */
    $('#filter_button').on('click', add_param);
    $('#id_filters').on('click','.remove_arg', remove_param);
    $('#id_filters').on('click','.clear_terms', full_form_clear);
    $('#results_button').on('click', show_results);
});

