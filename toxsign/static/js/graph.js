// Set the dimensions and margins of the diagram
function drawGraph(treeData, max_Parallel, max_Depth){
  var textcolored = {
    project: "#337ab7",
    study: "#5cb85c",
    assay: "#f0ad4e",
    factor: "#4ab1eb",
    signature: "#9467bd"
  }

  var margin = {
					top : 0,
					right : 0,
					bottom : 100,
					left : 0
				 };

  var rectNode = { width : 140, height : 60, textMargin : 10 };
  var tooltip = { width : 150, height : 60, textMargin : 10 };

  var width = max_Parallel * (rectNode.width + 40) + tooltip.width + 40 - margin.right - margin.left;
  var height = max_Depth * (rectNode.height * 1.5) + tooltip.height / 2 - margin.top - margin.bottom;

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
      .attr("transform", "translate("
          + 0  + "," + margin.top + ")");

  var i = 0,
      duration = 750,
      root,
      mousedown, // Use to save temporarily 'mousedown.zoom' value
	  mouseWheel,
	  mouseWheelName,
      isKeydownZoom = false;

  // declares a tree layout and assigns the size
//  var treemap = d3.tree().size([height, width]);
  var treemap = d3.tree().size([width, height]);
//  var treemap = d3.tree().nodeSize([width/2, height/2]);

  // Assigns parent, children, height, depth
  root = d3.hierarchy(treeData, function(d) { return d.children; });
  root.x0 = (width-rectNode.width)/2;
  root.y0 = 0;

  nodeGroup = svg.append('g')
    .attr('id', 'nodes');
  nodeGroupTooltip = svg.append('g')
    .attr('id', 'nodesTooltips');

  // Collapse after the second level
  root.children.forEach(collapse);

  update(root);
  // Collapse the node and all it's children
  function collapse(d) {
    if(d.children) {
      d._children = d.children
      d._children.forEach(collapse)
      d.children = null
    }
  }

  function update(source) {

    var menu = [{
      title: "View %name%",
      action: function(elm, d, i) {
            
      }
    }];

    // Assigns the x and y position for the nodes
    var treeData = treemap(root);

    // Compute the new tree layout.
    var nodes = treeData.descendants(),
        links = treeData.descendants().slice(1);

    // Normalize for fixed-depth.
    breadthFirstTraversal(nodes, collision);

    nodes.forEach(function(d){
      d.y = d.depth * (rectNode.height * 1.5)
    });

    // ****************** Nodes section ***************************

    // Update the nodes...
    var node = nodeGroup.selectAll('g.node')
        .data(nodes, function(d) {return d.id || (d.id = ++i); });

    var nodeTooltip = nodeGroupTooltip.selectAll('g')
        .data(nodes, function(d) {return d.id || (d.id = ++i); });

    // Enter any new modes at the parent's previous position.


    var nodeEnter = node.enter().insert('g', 'g.node')
        .attr('class', 'node')
        .attr("transform", function(d) {
          return "translate(" + source.x0 + "," + source.y0 + ")";
      })
      .on('click', click);

    var nodeEnterTooltip = nodeTooltip.enter().append('g')
  		.attr('transform', function(d) {
          return 'translate(' + d.x + ',' + d.y + ')'; });

    // Add rect for the nodes
    nodeEnter.append('rect')
      .attr('rx', 6)
      .attr('ry', 6)
      .attr('width', rectNode.width)
      .attr('height', rectNode.height)
      .attr('class', 'node-rect')
      .on('contextmenu', d3.contextMenu(menu))
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
						 + '<b> ' + d.data.tsx_id + '-' + d.data.name + '</b><br><br>'
					     + '</div>';
       })
           .on('contextmenu', d3.contextMenu(menu));
/*
       .on('mouseover', function(d) {
                $('.tooltip-box').css('visibility', 'hidden');
                $('.tooltip-text').css('visibility', 'hidden');
			    $('#nodeInfoID' + d.id).css('visibility', 'visible');
			    $('#nodeInfoTextID' + d.id).css('visibility', 'visible');
	   })
*/
    nodeEnterTooltip.append("rect")
 		  .attr('id', function(d) { return 'nodeInfoID' + d.id; })
     	  .attr('x', rectNode.width / 2)
 		  .attr('y', rectNode.height / 2)
 		  .attr('width', tooltip.width)
 		  .attr('height', tooltip.height)
     	  .attr('class', 'tooltip-box')
     	  .style('fill-opacity', 0.8);

 	nodeEnterTooltip.append("text")
 		  .attr('id', function(d) { return 'nodeInfoTextID' + d.id; })
     	  .attr('x', rectNode.width / 2 + tooltip.textMargin)
 		  .attr('y', rectNode.height / 2 + tooltip.textMargin * 2)
 		  .attr('width', tooltip.width)
 		  .attr('height', tooltip.height)
 		  .attr('class', 'tooltip-text')
 		  .style('fill', 'white')
 		  .append("tspan")
 	      .text(function(d) {return 'Name: ' + d.data.name;})
 	      .append("tspan")
 	      .attr('x', rectNode.width / 2 + tooltip.textMargin)
 	      .attr('dy', '1.5em')
 	      .text(function(d) {return 'Info: ' + d.data.name;});

    // UPDATE
    var nodeUpdate = nodeEnter.merge(node);

    // Transition to the proper position for the node
    nodeUpdate.transition().duration(duration)
      .attr("transform", function(d) {return "translate(" + d.x + "," + d.y + ")";});

    nodeTooltip.transition().duration(duration)
   	  .attr('transform', function(d) { return 'translate(' + d.x + ',' + d.y + ')'; });

    // Update the node attributes and style
    nodeUpdate.select('rect')
      .attr('class', function(d) { return d._children ? 'node-rect-closed' : 'node-rect'; });

    nodeUpdate.select('text').style('fill-opacity', 1);

    // Remove any exiting nodes
    var nodeExit = node.exit().transition().duration(duration)
        .attr("transform", function(d) {return "translate(" + source.x + "," + source.y + ")";})
        .remove();

    nodeTooltip.exit().transition().duration(duration)
        .attr('transform', function(d) { return 'translate(' + source.x + ',' + source.y + ')'; })
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
          var o = {x: source.x, y: source.y}
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
                   x : s.x + rectNode.width/2,
                   y : s.y
            },
        p3 = {
                   x : d.x + rectNode.width/2,
                   y : d.y + rectNode.height // -12, so the end arrows are just before the rect node
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
                   return [ d.x, d.y ];
            });
            return 'M' + p[0] + 'C' + p[1] + ' ' + p[2] + ' ' + p[3];
    };


    // Toggle children on click.
    function click(d) {
      $('.tooltip-box').css('visibility', 'hidden');
      $('.tooltip-text').css('visibility', 'hidden');
      if (d.children) {
          d._children = d.children;
          d.children = null;
        } else {
          d.children = d._children;
          d._children = null;
        }
      update(d);
    };
	// x = ordoninates and y = abscissas
	function collision(siblings) {
	  var minPadding = 5;
	  if (siblings) {
		  for (var i = 0; i < siblings.length - 1; i++)
		  {
			  if (siblings[i + 1].x - (siblings[i].x + rectNode.width) < minPadding)
				  siblings[i + 1].x = siblings[i].x + rectNode.width + minPadding;
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
    function zoomAndDrag() {
        var transform = d3.event.transform;
	    //var scale = d3.event.scale,
	     var scale = transform["k"],
	     tbound = -height * scale,
	     bbound = height * scale,
	     lbound = (-width + margin.right) * scale,
	     rbound = (width - margin.left) * scale;
	    // limit translation to thresholds
         transform = {
           k: scale,
           x: Math.max(Math.min(transform["x"], rbound), lbound),
           y:Math.max(Math.min(transform["y"], bbound), tbound)
         };
	     d3.select('#graph')
	      .attr('transform', transform);
    }

    function getMouseWheelEvent() {
    		if (d3.select('#graph').select('svg').on('wheel.zoom')){
    			mouseWheelName = 'wheel.zoom';
    			return d3.select('#graph').select('svg').on('wheel.zoom');
    		}
    		if (d3.select('#graph').select('svg').on('mousewheel.zoom') != null){
    			mouseWheelName = 'mousewheel.zoom';
    			return d3.select('#graph').select('svg').on('mousewheel.zoom');
    		}
    		if (d3.select('#graph').select('svg').on('DOMMouseScroll.zoom')){
    			mouseWheelName = 'DOMMouseScroll.zoom';
    			return d3.select('#graph').select('svg').on('DOMMouseScroll.zoom');
    		}
	}

    function removeMouseEvents() {
        // Drag and zoom behaviors are temporarily disabled, so tooltip text can be selected
       mousedown = d3.select('#graph').select('svg').on('mousedown.zoom');
       d3.select('#graph').select('svg').on("mousedown.zoom", null);
    }

    function reactivateMouseEvents() {
      // Reactivate the drag and zoom behaviors
      d3.select('#graph').select('svg').on('mousedown.zoom', mousedown);
    }
}
