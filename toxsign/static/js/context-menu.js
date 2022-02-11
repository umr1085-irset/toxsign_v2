d3.contextMenu = function (openCallback) {

    var loadForm = function (url) {
        $.ajax({
            url: url,
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#modal-group").modal("show");
            },
            success: function (data) {
                $("#modal-group .modal-content").html(data.html_form);
            }
        });
        return false;
    };

    // create the div element that will hold the context menu
    d3.selectAll('.d3-context-menu').data([1])
        .enter()
        .append('div')
        .attr('class', 'd3-context-menu');

    // close menu
    d3.select('body').on('click.d3-context-menu', function() {
        d3.select('.d3-context-menu').style('display', 'none');
    });

    // this gets executed when a contextmenu event occurs
    return function(data, index) {

        var menu = [
          {
            title: "View " + data.data.name,
            action: function(elm, d, i) {
              window.location.assign(d.data.view_url);
            }
          },
        ];

        if ('subentities' in data.data){
            for(var i = 0; i < data.data.subentities.length; i++){
                let dict = {title: "View " + data.data.subentities[i].name};
                let path = data.data.subentities[i].view_url;
                if(data.data.subentities[i].is_modal){
                    dict['action'] = function(elm, d, i) {
                        loadForm(path);
                    }
                } else {
                    dict['action'] = function(elm, d, i) {
                        window.location.assign(path);
                    }
                }
                menu.push(dict);
            }
        }

        if (data.data.editable){

            if(data.data.self_editable){

                menu.push({
                    title: "Edit " + data.data.type,
                    action: function(elm, d, i) {
                        window.location.assign(d.data.edit_url);
                    }
                })
            }

            menu.push({
                title: "Clone " + data.data.type,
                action: function(elm, d, i) {
                    window.location.assign(d.data.clone_url);
                }
            })

            for (var key in data.data.create_url){
                let path = data.data.create_url[key];
                menu.push({
                    title: "Create new " + key,
                    action: function(elm, d, i) {
                        window.location.assign(path);
                    }
                })
            }
        };

        var elm = this;

        d3.selectAll('.d3-context-menu').html('');
        var list = d3.selectAll('.d3-context-menu').append('ul');
        list.selectAll('li').data(menu).enter()
            .append('li')
            .html(function(d) {
                // Override title with entity name
                return d.title;
            })
            .on('click', function(d, i) {
                d.action(elm, data, index);
                d3.select('.d3-context-menu').style('display', 'none');
            });

        // the openCallback allows an action to fire before the menu is displayed
        // an example usage would be closing a tooltip
        if (openCallback) openCallback(data, index);

        // display context menu
        d3.select('.d3-context-menu')
            .style('left', (d3.event.pageX - 2) + 'px')
            .style('top', (d3.event.pageY - 2) + 'px')
            .style('display', 'block');

        d3.event.preventDefault();
    };
};
