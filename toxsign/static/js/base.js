jQuery(function( $ ){

    $('.close').click(function( e ){
        // Do not perform default action when button is clicked
        e.preventDefault();
        document.cookie = "citation_alert_box=closed;path=/";
    });
});

