$(function () {

  var filter_params = [];
  var current_state = {};

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

    var load_full = function () {
        var url = $("#filter_form").attr("data-url");
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var data = {terms: JSON.stringify(filter_params), csrfmiddlewaretoken: token};
        $.ajax({
            url: url,
            data: data,
            type: 'post',
            dataType: 'json',
            success: function (response) {
                // Setup current_state variable
                for (i=0; i < response.types.length; i++){
                  current_state[response.types[i]] = { current_page: 1, current_order: "", current_order_type: "", search_value: ""};
                }
                $("#id_results").html(response.table);
            }
        });
        return false;
    };

    var load_partial = function (request_page, ordered_column, order, search_value, type) {
        var url = $("#" + type + "-id").attr("data-url");
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var data = {request_page: request_page, ordered_column: ordered_column, order:order, search_value: search_value, terms: JSON.stringify(filter_params), csrfmiddlewaretoken: token};
        $.ajax({
            url: url,
            data: data,
            type: 'post',
            dataType: 'json',
            success: function (response) {
                current_state[response.type] = { current_page: response.current_page, current_order: response.current_order, current_order_type: response.current_order_type, search_value: response.search_value};
                $("#" + type + "-table").html(response.table);
                $("#" + type + "-columns").html(response.columns);
                $("#" + type + "-paginate").html(response.paginate);
            }
        });
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

    var order = function(){
      var col_name = $(this).attr("target");
      var type = $(this).attr("data-type");
      var current_page = current_state[type]["current_page"];
      var current_order = current_state[type]["current_order"];
      var current_order_type = current_state[type]["current_order_type"];
      var search_value = current_state[type]["search_value"];
      var order = "desc";
      if (col_name == current_order){
        if (current_order_type == "desc") {
          order = "asc";
        }
      }
      load_partial(current_page, col_name, order, search_value, type);
    }

    var paginate = function(){
      var next_page = $(this).attr("target");
      var type = $(this).attr("data-type");
      var current_order = current_state[type]["current_order"]
      var current_order_type = current_state[type]["current_order_type"]
      var search_value = current_state[type]["search_value"];
      load_partial(next_page, current_order, current_order_type, search_value, type);
    }

    var filter = function(){
        var search_value = $(this).val();
        if(search_value.length > 2){
            var type = $(this).attr("data-type");
            var current_order = current_state[type]["current_order"];
            var current_order_type = current_state[type]["current_order_type"];
            var current_page = current_state[type]["current_page"];
            load_partial(current_page, current_order, current_order_type, search_value, type);
            $(this).focus();
        }
    }

  /* Binding */
    $('#filter_button').on('click', add_param);
    $('#id_filters').on('click','.remove_arg', remove_param);
    $('#id_filters').on('click','.clear_terms', full_form_clear);
    $('#results_button').on('click', load_full);
    $('#id_results').on('click', ".order-action", order);
    $('#id_results').on('click', ".page-action", paginate);
    $('#id_results').on('keyup', ".term_select", filter);
});
