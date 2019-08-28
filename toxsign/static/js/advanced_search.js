$(function () {

  var search_params = [];

  /* Functions */

  var get_form = function () {
    var entity_type = $("#entity_select").val();
    var url = $("#entity_form").attr("data-url") + "?entity=" + entity_type;
    $.ajax({
      url: url,
      type: 'get',
      dataType: 'json',
      success: function (data) {
        $("#result").html(data.html_form);
        $("#load_results").show();
      }
    });
    return false;
  };

    var add_param = function() {
        var arg_type = $("#id_field").val();
        var arg_value = $("#id_value").val();
        var type = $("#id_type").val();
        $("#id_type").show();
        var dict = { bool_type: type, arg_type:arg_type, arg_value: arg_value};
        search_params.push(dict);
        //Reset fields
        $('#advanced_search_form').trigger("reset");
        fill_html();
        return false;
    };

    var remove_param = function(){
        var value = $(this).attr("arg_value");
        search_params.splice(value, 1);
        // Regenerate arguments
        fill_html();
        if(search_params.length == 0){
            $("#id_type").hide();
        }
        return false;
    };

    var search = function () {
        var entity_type = $("#entity_select").val();
        var token = $("input[name=csrfmiddlewaretoken]").val();
        var data = {entity: entity_type, terms: JSON.stringify(search_params), csrfmiddlewaretoken: token};
        console.log(data);
        var url = $("#entity_form").attr("data-url");
        $.ajax({
            url: url,
            data: data,
            type: 'post',
            dataType: 'json',
            success: function (response) {
                console.log(response);
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
                html += `(${search_params[0]['arg_type']} : *${search_params[0]['arg_value']}*) ${get_button(0)} <br>`;
            } else {
                html += `${search_params[i]['bool_type']} (${search_params[i]['arg_type']} : *${search_params[i]['arg_value']}*) ${get_button(i)} <br>`;
            }
        $("#search_terms").html(html);
    }

  /* Binding */
    $('#entity_select').on('change', get_form);
    $('#result').on('submit','#advanced_search_form', add_param);
    $('#search_terms').on('click','.remove_arg', remove_param);
    $("#load_results").on('click', search);
});

