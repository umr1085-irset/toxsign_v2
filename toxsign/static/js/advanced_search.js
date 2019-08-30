$(function () {

  var search_params = [];

  /* Functions */

  var selected_field_id = "";

  var get_form = function () {
    var entity_type = $("#entity_select").val();
    var url = $("#entity_form").attr("data-url") + "?entity=" + entity_type;
    $.ajax({
      url: url,
      type: 'get',
      dataType: 'json',
      success: function (data) {
        $("#result").html(data.html_form);
        // Fix issue with autocomplete box too small
        $(".select2-container").width("100%");
      }
    });
    return false;
  };

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
            dict['arg_value'] = $("#select2-id_" + arg_type + "-container").attr("title");
            dict['ontology_options']['id'] = $("#id_" + arg_type).val();
            dict['ontology_options']['search_type'] = $("#id_onto_type").val();
        }
        if( dict['arg_value'] == "" || dict['arg_value'] == "**" || dict['arg_type'] == "" ){
            $("#error_field").html("Field name and field value are required<br>");
            return false;
        }
        search_params.push(dict);
        $("#id_type_wrapper").show();
        //Reset fields
        reset_form(arg_type, dict['is_ontology']);
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
        var entity_type = $("#entity_select").val();
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var data = {entity: entity_type, terms: JSON.stringify(search_params), csrfmiddlewaretoken: token};
        var url = $("#entity_form").attr("data-url");
        $.ajax({
            url: url,
            data: data,
            type: 'post',
            dataType: 'json',
            success: function (response) {
                $("#search_results").html(response.html_page);
            }
        });
        return false;
    };

    var get_button = function(arg_number){
        return `<button class='btn btn-link btn-xs remove_arg' arg_value='${arg_number}'><i class='fas fa-trash'></i></button>`;

    }

    var fill_html = function(){
        var html = ""
        for (i=0; i < search_params.length; i++)
            if (i == 0){
                if(search_params[i]['is_ontology']){
                    html += `(${search_params[i]['arg_type']} : ${search_params[i]['arg_value']}, search type : ${search_params[i]['ontology_options']['search_type']}) ${get_button(i)} <br>`;
                } else {
                    html += `(${search_params[i]['arg_type']} : ${search_params[i]['arg_value']}) ${get_button(i)} <br>`;
                }
            } else {
                if(search_params[i]['is_ontology']){
                    html += `${search_params[i]['bool_type']} (${search_params[i]['arg_type']} : ${search_params[i]['arg_value']}, search type : ${search_params[i]['ontology_options']['search_type']}) ${get_button(i)} <br>`;
                } else {
                    html += `${search_params[i]['bool_type']} (${search_params[i]['arg_type']} : ${search_params[i]['arg_value']}) ${get_button(i)} <br>`;
                }
            }
        $("#search_terms").html(html);
    }

    var update_fields = function(){
        var field = $("#id_field").val();
        // Check if a field  with _id_wrapper exists (it must be an ontology), then make it visible
        if ($("#id_" + field + "_ontology_wrapper").length ) {
            $(selected_field_id).hide()
            $("#id_" + field + "_ontology_wrapper").show();
            $("#id_onto_type_wrapper").show();
            selected_field_id = "#id_" + field + "_ontology_wrapper";
        } else {
            $(selected_field_id).hide();
            $("#id_value_wrapper").show();
            selected_field_id = "#id_value_wrapper";
        }
    }

    var reset_form = function(arg_type, is_ontology){
        // Need to manually reset field if it's an ontology
        if(is_ontology){
            $("#id_" + arg_type).val(null).trigger('change');
        }
        $(selected_field_id).hide();
        $("#id_onto_type_wrapper").hide();
        $('#advanced_search_form').trigger("reset");
    }

    var is_ontology = function(field){
        if ($("#id_" + field + "ontology_wrapper").length) {
            return true;
        } else {
            return false;
        }
    }

  /* Binding */
    $('#entity_select').on('change', get_form);
//    $('#result').on('submit','#advanced_search_form', add_param);
    $('#result').on('click','#add_argument', add_param);
    $('#result').on('change','#id_field', update_fields);
    $('#search_terms').on('click','.remove_arg', remove_param);
    $("#load_results").on('click', search);
});

