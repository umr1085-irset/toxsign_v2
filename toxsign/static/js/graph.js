// Set the dimensions and margins of the diagram
function drawGraph(treeData){

  var textcolored = {
    project: "red",
    study: "blue",
    assay: "green",
    factor: "yellow",
    signature: "gray"
  }

  var margin = {
					top : 0,
					right : 0,
					bottom : 100,
					left : 0
				 },
		// Height and width are redefined later in function of the size of the tree
		// (after that the data are loaded)

  var maxDepth = 0;
  var maxTreeWidth = breadthFirstTraversal(treemap.nodes(treeData), function(currentLevel) {
    maxDepth++;
  });

	width = 800 - margin.right - margin.left,
	height = 400 - margin.top - margin.bottom;

	var rectNode = { width : 120, height : 45, textMargin : 5 };

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
      .append("g")
      .attr("transform", "translate("
            + margin.left + "," + margin.top + ")");

  var i = 0,
      duration = 750,
      root;

  // declares a tree layout and assigns the size
  var treemap = d3.tree().size([height, width]);

  // Assigns parent, children, height, depth
  root = d3.hierarchy(treeData, function(d) { return d.children; });
  root.x0 = height / 2;
  root.y0 = 0;

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

    // Assigns the x and y position for the nodes
    var treeData = treemap(root);

    // Compute the new tree layout.
    var nodes = treeData.descendants(),
        links = treeData.descendants().slice(1);

    // Normalize for fixed-depth.
    nodes.forEach(function(d){ d.y = d.depth * 180});

    // ****************** Nodes section ***************************

    // Update the nodes...
    var node = svg.selectAll('g.node')
        .data(nodes, function(d) {return d.id || (d.id = ++i); });

    // Enter any new modes at the parent's previous position.
    var nodeEnter = node.enter().append('g')
        .attr('class', 'node')
        .attr("transform", function(d) {
          return "translate(" + source.y0 + "," + source.x0 + ")";
      })
      .on('click', click);

    // Add Circle for the nodes
    nodeEnter.append('rect')
      .attr('rx', 6)
      .attr('ry', 6)
      .attr('width', rectNode.width)
      .attr('height', rectNode.height)
      .attr('class', 'node-rect')
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
							 + '<b>' + d.data.name + '</b><br><br>'
							 + '</div>';
       })

    // UPDATE
    var nodeUpdate = nodeEnter.merge(node);

    // Transition to the proper position for the node
    nodeUpdate.transition()
      .duration(duration)
      .attr("transform", function(d) {
          return "translate(" + d.y + "," + d.x + ")";
       });

    // Update the node attributes and style
    nodeUpdate.select('rect')
      .attr('class', function(d) { return d._children ? 'node-rect-closed' : 'node-rect'; });

    nodeUpdate.select('text').style('fill-opacity', 1);

    // Remove any exiting nodes
    var nodeExit = node.exit().transition()
        .duration(duration)
        .attr("transform", function(d) {
            return "translate(" + source.y + "," + source.x + ")";
        })
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

    function zoomAndDrag() {
	    //var scale = d3.event.scale,
	     var scale = 1,
	     translation = d3.event.translate,
	     tbound = -height * scale,
	     bbound = height * scale,
	     lbound = (-width + margin.right) * scale,
	     rbound = (width - margin.left) * scale;
	    // limit translation to thresholds
	     translation = [
	        Math.max(Math.min(translation[0], rbound), lbound),
	        Math.max(Math.min(translation[1], bbound), tbound)
	     ];
	     d3.select('.drawarea')
	      .attr('transform', 'translate(' + translation + ')' +
	      ' scale(' + scale + ')');
    }

    // Creates a curved (diagonal) path from parent to the child nodes
    function diagonal(s, d) {
		    var p0 = {
			       x : s.x + rectNode.height / 2,
			       y : (s.y + rectNode.width)
		    },
        p3 = {
			       x : d.x + rectNode.height / 2,
			       y : d.y  - 12 // -12, so the end arrows are just before the rect node
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
    // Toggle children on click.
    function click(d) {
      if (d.children) {
          d._children = d.children;
          d.children = null;
        } else {
          d.children = d._children;
          d._children = null;
        }
      update(d);
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
	// x = ordoninates and y = abscissas
	function collision(siblings) {
	  var minPadding = 5;
	  if (siblings) {
		  for (var i = 0; i < siblings.length - 1; i++)
		  {
			  if (siblings[i + 1].x - (siblings[i].x + rectNode.height) < minPadding)
				  siblings[i + 1].x = siblings[i].x + rectNode.height + minPadding;
		  }
	  }
  }
}
}
