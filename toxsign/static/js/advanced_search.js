$(function () {

  var search_params = [];
  var history = [];

  /* Functions */

  var selected_field_id = "";
  var active_ontology_id = "";
  var current_search = {}

    var add_param = function() {
        $("#error_field").html("");
        var arg_type = $("#id_field").val();
        var arg_value = "*" + $("#id_value").val() + "*";
        var type = $("#id_type").val();
        var dict = { bool_type: type, arg_type:arg_type, arg_value: arg_value, is_ontology: false, ontology_options: {}};
        // Get options if it's an ontology
        if(is_ontology(arg_type)){
            dict['is_ontology'] = true;
            // Need to access the name from the other field
            dict['arg_value'] = $("#id_" + arg_type + " option:selected").text();
            dict['ontology_options']['id'] = $("#id_" + arg_type).val();
        }
        if( dict['arg_value'] == "" || dict['arg_value'] == "**" || dict['arg_type'] == "" ){
            $("#error_field").html("Field name and field value are required<br>");
            return false;
        }
        search_params.push(dict);
        $("#id_type_wrapper").show();
        //Reset fields
        reset_form();
        fill_html();
        return false;
    };

    var remove_param = function(){
        var value = $(this).attr("arg_value");
        search_params.splice(value, 1);
        // Regenerate arguments
        fill_html();
        if(search_params.length == 0){
            $("#id_type_wrapper").hide();
        }
        return false;
    };

    var search = function () {
        if (search_params.length == 0){
            $("#search_terms").html("<div  style='text-align:center;color:red;'> Please select some terms before searching</div>");
            return false;
        }
        var url = $("#load_results").attr("data-url");
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var data = {terms: JSON.stringify(search_params), csrfmiddlewaretoken: token};
        update_history({terms:search_params});
        current_search = {terms:search_params};
        $.ajax({
            url: url,
            data: data,
            type: 'post',
            dataType: 'json',
            success: function (response) {
                $("#search_results_wrapper").show();
                $("#search_results").html(response.html_page);
                $("#search_results_wrapper")[0].scrollIntoView()
            }
        });
        return false;
    };

    var relaunch_search = function(){
        var history_key = $(this).attr("key");
        var search_params = history[history_key];
        var url = $("#load_results").attr("data-url");
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var body = {terms: JSON.stringify(search_params['raw_data']), csrfmiddlewaretoken: token};
        current_search = history[history_key];
        $.ajax({
            url: url,
            data: body,
            type: 'post',
            dataType: 'json',
            success: function (response) {
                $("#search_results_wrapper").show();
                $("#search_results").html(response.html_page);
                $("#search_results_wrapper")[0].scrollIntoView()
            }
        });
        return false;
    }

    var get_button = function(arg_number){
        return `<button class='btn btn-link btn-xs remove_arg' arg_value='${arg_number}'><i class='fas fa-trash'></i></button>`;

    }

    var fill_html = function(){
        var html = ""
        for (i=0; i < search_params.length; i++)
            if (i == 0){
                html += `(${search_params[i]['arg_type']} : ${search_params[i]['arg_value']}) ${get_button(i)} <br>`;
            } else {
                html += `${search_params[i]['bool_type']} (${search_params[i]['arg_type']} : ${search_params[i]['arg_value']}) ${get_button(i)} <br>`;
            }
        if (search_params.length >0){
            html += "<button type='button' class='btn btn-danger clear_terms'>Clear <i class='fa fa-trash' aria-hidden='true'></i><br></button><br>"
        }
        $("#search_terms").html(html);
    }

    var update_fields = function(){
        var field = $("#id_field").val();
        // Check if a field  with _id_wrapper exists (it must be an ontology), then make it visible
        if ($("#id_" + field + "_ontology_wrapper").length ) {
            $(selected_field_id).hide()
            $("#id_" + field + "_ontology_wrapper").show();
            selected_field_id = "#id_" + field + "_ontology_wrapper";
            active_ontology_id = "#id_" + field;
        } else {
            $(selected_field_id).hide();
            $("#id_onto_type_wrapper").hide()
            $("#id_value_wrapper").show();
            selected_field_id = "#id_value_wrapper";
            active_ontology_id = "";
        }
    }

    var reset_form = function(){
        // Need to manually reset field if it's an ontology
        $(selected_field_id).hide();
        $("#id_onto_type_wrapper").hide();
        $('#advanced_search_form').trigger("reset");
    }

    var is_ontology = function(field){
        if ($("#id_" + field).length) {
            return true;
        } else {
            return false;
        }
    }

    var update_history = function(data=false){
        if (data){
            // Need to make a true copy, and not a reference
            var copy = JSON.parse(JSON.stringify(data['terms']));
            var dict = {raw_data: copy}
            var terms = "";
            for  (i=0; i < data['terms'].length; i++){
                terms += `${data['terms'][i]['bool_type']} (${data['terms'][i]['arg_type']} : ${data['terms'][i]['arg_value']} `
                terms += ") "
            }
            dict['terms'] = terms
            history.push(dict);
        }
        var html = ""
        for (i=0; i< history.length; i++){
            html += `Signature search: {${history[i]['terms']}}`;
            html += "<button type='button' key='" + i +"' class='btn btn-link search_button'><i class='fa fa-sync' aria-hidden='true'></i><br></button><br>"
        }
        if(history.length > 0){
            html += "<br><div style='text-align:center'> <button type='button' class='btn btn-danger clear_history'>Clear <i class='fa fa-trash' aria-hidden='true'></i></button></div><br>"
        }

        $("#history").html(html);
    }

    var full_form_clear = function(){
        search_params = [];
        $("#search_terms").html("<div  style='text-align:center;'>Search terms you have selected will appear here for review</div>");
        $("#id_type_wrapper").hide();
        // Need to manually reset field if it's an ontology

        if(active_ontology_id != ""){
            $(active_ontology_id).val(null).trigger('change');
        }
        $(selected_field_id).hide();
        $("#id_onto_type_wrapper").hide();
        $('#advanced_search_form').trigger("reset");
    }

    var reset_history = function(){
        history = [];
        update_history();
    }

    var paginate = function(){
        var next_page = $(this).attr("target");
        var url = $("#load_results").attr("data-url");
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var body = {terms: JSON.stringify(current_search['terms']), page:next_page, csrfmiddlewaretoken: token};
        $.ajax({
            url: url,
            data: body,
            type: 'post',
            dataType: 'json',
            success: function (response) {
                $("#search_results").html(response.html_page);
                $("#search_results_wrapper")[0].scrollIntoView()
            }
        });
        return false;
    }



  /* Binding */
    $('#result').on('click','#add_argument', add_param);
    $('#result').on('change','#id_field', update_fields);
    $('#search_terms').on('click','.remove_arg', remove_param);
    $('#search_terms').on('click','.clear_terms', full_form_clear);
    $("#load_results").on('click', search);
    $("#history").on('click', '.search_button', relaunch_search);
    $("#history").on('click', '.clear_history', reset_history);
    $('#search_results').on('click', ".page-action", paginate);
});

