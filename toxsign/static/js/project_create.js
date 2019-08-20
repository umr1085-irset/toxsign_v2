
$("#id_status").change(function () {
    var visibility = $(this).val();
    if (visibility == "PUBLIC"){
        $("#id_read_groups").prop('disabled', 'disabled');
        $("#id_read_groups").find("option:selected").prop('selected',false);
    } else {
        $("#id_read_groups").prop('disabled', false);
    };
});

// TODO : Use jquery to set read groups to be at least the same as edit groups
