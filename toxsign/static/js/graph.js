// Set the dimensions and margins of the diagram
function drawGraph(treeData, max_Parallel, max_Depth, current_Entity=""){

  var current_Entity;

  var textcolored = {
    project: "#337ab7",
    study: "#5cb85c",
    assay: "#f0ad4e",
    factor: "#4ab1eb",
    signature: "#9467bd"
  }

  var glyphicon = {
    project: "fas fa-project-diagram",
    study: "fas fa-book-open",
    assay: "fas fa-flask",
    factor: "fas fa-cog",
    signature: "fas fa-signature"
 }



  var margin = {
					top : 20,
					right : 0,
					bottom : 100,
					left : 10
				 };

  var rectNode = { width : 140, height : 80, textMargin : 5 };

  var height = max_Parallel * (rectNode.height + 20) + 50 - margin.top - margin.bottom;
  var width = max_Depth * (rectNode.width * 1.5) + 100 - margin.top - margin.bottom;


  var colorScale = d3.scaleLinear()
      .domain([0, 1])
  		.range(['red', 'green']);
  var widthScale = d3.scaleLinear()
  		.domain([1,80])
  		.range([1, 10]);

  // append the svg object to the body of the page
  // appends a 'group' element to 'svg'
  // moves the 'group' element to the top left margin
  var svg = d3.select("#graph").append("svg")
      .attr("width", width + margin.right + margin.left)
      .attr("height", height + margin.top + margin.bottom)
      .attr('class', 'svgContainer')
      .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

  var tip = d3.tip().attr('class', 'd3-tip').direction('e').offset([-10,10])
    .html(function(d) {
      var content = "<span style='margin-left: 2.5px;'><b>Left click to see this entity. Right click for more options</b></span><br>";
      return content;
     });

  svg.call(tip);

  var i = 0,
      duration = 750,
      root,
      mousedown, // Use to save temporarily 'mousedown.zoom' value
	  mouseWheel,
	  mouseWheelName,
      isKeydownZoom = false;

  // declares a tree layout and assigns the size
  var treemap = d3.tree().size([height, width]);
  //var treemap = d3.tree().nodeSize([width, height]);

  // Assigns parent, children, height, depth
  root = d3.hierarchy(treeData, function(d) { return d.children; });

  root.x0 = width / 2;
  root.y0 = 0;


  nodeGroup = svg.append('g')
    .attr('id', 'nodes');

  // Collapse after the second level

  // No collapse

  //collapse(root);
  update(root);

  function collapse(element){
    // IF project, do not collapse anything (overwiew)
    if(element.data.type == 'project' && element.data.tsx_id == current_Entity){ return;}

    var stop = false;
    if(element.children){
        var is_current_entity = false;
        for(var i=0; i < element.children.length; i++){
            is_current_entity = collapse(element.children[i]);
            if(is_current_entity){stop = true};
        }
        if(!stop){
            element._children = element.children
            element.children = null
        };
    }
    if( stop || element.data.tsx_id == current_Entity){
        return true;
    } else {
        return false;
    }
  };


  function update(source) {

    // Assigns the x and y position for the nodes
    var treeData = treemap(root);

    // Compute the new tree layout.
    var nodes = treeData.descendants(),
        links = treeData.descendants().slice(1);

    // Normalize for fixed-depth.
    breadthFirstTraversal(nodes, collision);

    nodes.forEach(function(d){
      d.y = d.depth * (rectNode.width * 1.5)
      // Force centering on center of node, not on corner
      //d.y = d.y + (rectNode.height/2)
      //d.x = d.x - (rectNode.width/2)

    });

    // ****************** Nodes section ***************************

    // Update the nodes...
    var node = nodeGroup.selectAll('g.node')
        .data(nodes, function(d) {return d.id || (d.id = ++i); });

    // Enter any new modes at the parent's previous position.

    var nodeEnter = node.enter().insert('g', 'g.node')
        .attr('class', 'node')
        .attr("transform", function(d) {
          return "translate(" + source.y0 + "," + source.x0 + ")";
      })
      .on('click', click);

    // Add rect for the nodes

    nodeEnter.append('rect')
      .attr('rx', 6)
      .attr('ry', 6)
      .attr('width', rectNode.width)
      .attr('height', rectNode.height)
      .attr('class', 'node-rect')
      .on('contextmenu', d3.contextMenu())
      .attr('fill', function(d){
        return textcolored[d.data.type];
      })


    // Add labels for the nodes
    nodeEnter.append('foreignObject')
		  .attr('x', rectNode.textMargin)
		  .attr('y', rectNode.textMargin)
		  .attr('width', function() {
		      return (rectNode.width - rectNode.textMargin * 2) < 0 ? 0
					     : (rectNode.width - rectNode.textMargin * 2)
	     })
		   .attr('height', function() {
			    return (rectNode.height - rectNode.textMargin * 2) < 0 ? 0
						   : (rectNode.height - rectNode.textMargin * 2)
				})
		   .append('xhtml').html(function(d) {
			    return '<div style="width: '
					     + (rectNode.width - rectNode.textMargin * 2) + 'px; height: '
					     + (rectNode.height - rectNode.textMargin * 2) + 'px;" class="node-text wordwrap">'
						 + '<b> ' + d.data.tsx_id + '-' + d.data.name + '</b>'
                         + '<br><br><i style="font-size:12px" class="'+ glyphicon[d.data.type]+ '"></i><br>'
                         + get_subentities(d.data.type, d.data.count_subentities)
					     + '</div>';
       })
           .on('contextmenu', d3.contextMenu())
           .on('mouseover', tip.show)
           .on('mouseout', tip.hide);


    // UPDATE
    var nodeUpdate = nodeEnter.merge(node);

    // Transition to the proper position for the node
    nodeUpdate.transition().duration(duration)
      .attr("transform", function(d) {
            return "translate(" + d.y + "," + d.x + ")";});

    // Update the node attributes and style
    nodeUpdate.select('rect')
      .attr('class', function(d) {
        if(d.data.tsx_id == current_Entity){
            return 'node-rect-current';
        }
        return d._children ? 'node-rect-closed' : 'node-rect';
      });

    nodeUpdate.select('text').style('fill-opacity', 1);

    // Remove any exiting nodes
    var nodeExit = node.exit().transition().duration(duration)
        .attr("transform", function(d) {
            return "translate(" + source.y + "," + source.x + ")";})
        .remove();

    nodeExit.select('text').style('fill-opacity', 1e-6);

    // ****************** links section ***************************

    // Update the links...
    var link = svg.selectAll('path.link')
        .data(links, function(d) { return d.id; })
        .style('stroke-width', function(d){
          return widthScale(d.data.value)
    });

    // Enter any new links at the parent's previous position.
    var linkEnter = link.enter().insert('path', "g")
        .attr("class", "link")
        .attr('d', function(d){
          var o = {x: source.x0, y: source.y0}
          return diagonal(o, o)
        })
        .style('stroke-width', function(d){
          return widthScale(d.data.value)
        });

    // UPDATE
    var linkUpdate = linkEnter.merge(link);

    // Transition back to the parent element position
    linkUpdate.transition()
        .duration(duration)
        .attr('d', function(d){ return diagonal(d, d.parent) });

    // Remove any exiting links
    var linkExit = link.exit().transition()
        .duration(duration)
        .attr('d', function(d) {
          var o = {x: source.x0, y: source.y0}
          return diagonal(o, o)
        })
        .style('stroke-width', function(d){
          return widthScale(d.data.value)
        })
        .remove();

    // Store the old positions for transition.
    nodes.forEach(function(d){
      d.x0 = d.x;
      d.y0 = d.y;
    });

    // Creates a curved (diagonal) path from parent to the child nodes
    function diagonal(s, d) {
            var p0 = {
                   x : s.x + rectNode.height/2,
                   y : s.y
            },
        p3 = {
                   x : d.x + rectNode.height/2,
                   y : d.y + rectNode.width
            },
        m = (p0.y + p3.y) / 2,
        p = [ p0, {
                   x : p0.x,
                   y : m
            }, {
                   x : p3.x,
                   y : m
            }, p3 ];
            p = p.map(function(d) {
                   return [ d.y, d.x ];
            });
            return 'M' + p[0] + 'C' + p[1] + ' ' + p[2] + ' ' + p[3];
    };

    // Go to entity on click
    function click(d) {
      window.location.assign(d.data.view_url);
    };
	// x = ordoninates and y = abscissas
	function collision(siblings) {
	  var minPadding = 5;
	  if (siblings) {
		  for (var i = 0; i < siblings.length - 1; i++)
		  {
			  if (siblings[i + 1].x - (siblings[i].x + rectNode.height) < minPadding){
				  siblings[i + 1].x = siblings[i].x + rectNode.height + minPadding;
              }
		  }
	  }
  }
}
    function breadthFirstTraversal(tree, func){
  	  var max = 0;
  	  if (tree && tree.length > 0){
  		    var currentDepth = tree[0].depth;
  		    var fifo = [];
  		    var currentLevel = [];

 		    fifo.push(tree[0]);
  		    while (fifo.length > 0) {
  			    var node = fifo.shift();
  			    if (node.depth > currentDepth) {
  				    func(currentLevel);
  				    currentDepth++;
  				    max = Math.max(max, currentLevel.length);
  				    currentLevel = [];
  			    }
  			    currentLevel.push(node);
  			    if (node.children) {
  				    for (var j = 0; j < node.children.length; j++) {
  					    fifo.push(node.children[j]);
  				    }
  			    }
  	  	  }
  		    func(currentLevel);
  		    return Math.max(max, currentLevel.length);
  	  }
  	  return 0;
    }

}

    function get_subentities(type, count){
        if(type == "factor"){
            if (count > 0){
                return "<i>" +  count + " subfactor(s)</i>"
            }
            else {
                return "<i>0 subfactors</i>"
            }
        } else {
            return "";
        }
    }

