/////////////////////////////////
// Global variables, as usual. //
/////////////////////////////////

var divID = "viz" // ID of the div that the visualization lives in.
    w = $("#viz").width(),
    h = $("#panel").height(),
    pic_width_factor = 0.33,
    r = 12,
    small_r = 8,
    fill = d3.scale.category20(),
    // link_length = 25,
    link_length = Math.min(w, h)/20,
	marker_size = 5,
	label_size = 14,
    // tooltip_width = 100,
    // tooltip_offset = 25,
    charge = -200,
    ancestor_charge = -2000,
    famous_charge = -200, 
	link_strength = 0.8,
	gravity = 0.20,
	friction = 0.5,
	theta = 0.8,
	num_ticks = 100;

// Hawking's ID in the database:
var hawking_id = 78459;

var div = d3.select("#" + divID);

var opts = {
  lines: 13, // The number of lines to draw
  length: 20, // The length of each line
  width: 10, // The line thickness
  radius: 30, // The radius of the inner circle
  corners: 1, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  direction: 1, // 1: clockwise, -1: counterclockwise
  color: '#000', // #rgb or #rrggbb
  speed: 1, // Rounds per second
  trail: 60, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: false, // Whether to use hardware acceleration
  className: 'spinner', // The CSS class to assign to the spinner
  // zIndex: -2e9, // The z-index (defaults to 2000000000)
  // top: h/2, // Top position relative to parent in px
  // left: w/2 // Left position relative to parent in px
};
var target = document.getElementById(divID);
var spinner = new Spinner(opts).spin(target);

// var tooltip = div.append("div")
//                 .attr("id", "name-tooltip")
//                 .attr("class", "hidden");

d3.json("json/small.json", function(json) {
// d3.json("json/everything.json", function(json) {
    d3.json("json/famous.json", function(famous) {      
        
        var autolist = [],
            index = 0;
        json.nodes.forEach(function(n){
            autoperson = {"label":n.name, "value":index};
            autolist.push(autoperson);
            index += 1;
        });

        // Handling color behavior for default text in autocomplete field.
        // Pulled from this SO thread:
        // http://stackoverflow.com/questions/15639152/jqueryui-autocomplete-with-default-text
        $('#autocomplete').each(function () {
            var $t = $(this),
                default_value = this.value;
            $t.css('color', '#929292');
            $t.focus(function () {
                if (this.value == default_value) {
                    this.value = '';
                    $t.css('color', 'black');
                }
            });
            $t.blur(function () {
                if ($.trim(this.value) == '') {
                    $t.css('color', '#929292');
                    this.value = default_value;
                }
            });
        });
        
        // $(function() {
            
            accentMap = {
                "á":"a",
                "å":"a",
                "à":"a",
                "ä":"a",
                "â":"a",
                "ç":"c",
                "č":"c",
                "é":"e",
                "è":"e",
                "ë":"e",
                "ê":"e",
                "ě":"e",
                "ì":"i",
                "í":"i",
                "ï":"i",
                "î":"i",
                "ł":"l",
                "ñ":"n",
                "ø":"o",
                "ö":"o",
                "ő":"o",
                "ò":"o",
                "ó":"o",
                "ô":"o",
                "š":"s",
                "ß":"ss",
                "ü":"u",
                "ú":"u",
                "ù":"u",
                "û":"u",
                "ž":"z"
                
            };
            normalize = function( term ) {
                var ret = "";
                for ( var i = 0; i < term.length; i++ ) {
                ret += accentMap[ term.charAt(i) ] || term.charAt(i);
                }
                return ret;
            };
            
            selection_event = function(event, ui){ 
        	    // First, stop the default action, which is to populate the text box with the value of the chosen item.
        	    // In this case, the value is the ID -- a meaningless number between 1 and 180,000 which would only confuse the user.
        	    // We definitely don't want that!
                event.preventDefault();
        	    // Now populate the field with the actual name selected.
        	    $(this).prop("value", ui.item.label);
        	    // Finally, fire off the click() function with the appropriate node!
        	    // console.log(ui.item.value);
        	    person = json.nodes[ui.item.value];
        	    bare_click(person);
        	    };
            
        	$("#autocomplete").autocomplete({
        		minLength: 5,
                // source: autolist
                source: function( request, response ) {
                    // This function uses the accent map given above 
                    // to allow users to input names without accents into the autocomplete form.
                    // How does it do it?
                    // THIS IS BLACK MAGIC!
                    // I pulled it from the jQuery UI example here:
                    // http://jqueryui.com/autocomplete/#folding
                    var matcher = new RegExp( $.ui.autocomplete.escapeRegex( request.term ), "i" );
                    response( $.grep(autolist, function( value ) {
                        value = value.label || value.value || value;
                        return matcher.test( value ) || matcher.test( normalize( value ) );
                    }) );
                }
        	});
        	
        	// Normally, the autocomplete window will fill the field with the value of the selected item on keyboard navigation,
        	// i.e. if you're navigating the list with the arrow keys.
        	// Again, we really don't want those numbers to show up...
        	$("#autocomplete").on( "autocompletefocus", function( event, ui ) {
        	    event.preventDefault();
                // $(this).prop("value", ui.item.label);
        	} );
        	
        	$("#autocomplete").on("autocompleteselect", selection_event);
        	
        // });
        
        spinner.stop();
        
        // // $("body").append("p")
        // d3.select("body").append("p")
        // .html('<font id="source">Source: <a href="http://genealogy.math.ndsu.nodak.edu/" target="_blank">Mathematics Genealogy Project</font></a>');
        // // $("#source").css("bottom", 0);
        // var panel_bottom = $("#panel").offset().top + $("#panel").outerHeight();
        // // d3.select("#source").style("top", panel_bottom).style("right", 0)
        // // $("#source").css("bottom", "");
        // $("#source").css("top", panel_bottom);
        
        var svg = div.append("svg")
            .attr("width", w)
            .attr("height", h);
            // .attr("width", "100%")
            // .attr("height", "100%");
            
            // Per-type markers, as they don't inherit styles.
            svg.append("defs")
             .append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 30)
                .attr("refY", 0)
                .attr("markerWidth", marker_size)
                .attr("markerHeight", marker_size)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5");
	
	// Initializing the force layout
    var force = d3.layout.force()
	    .charge(function(n){
		if (n.generation <= -1) {return ancestor_charge;}
		else if (n.famous) {return famous_charge;}
		else {return charge;};
		})
		.linkDistance(function(l){
            if (l.target.famous ){ 
               return 2*link_length;
               }
              else {
			    return link_length
                };
		})
        .linkStrength(link_strength)
        .gravity(gravity)
        .friction(friction)
        .theta(theta)
	    .size([w, h])
        // .on("tick", tick);
	
	force.nodes(json.nodes)
      .links(json.links)
      .start();
      
      // Setting up the drop-down menu.
      var drop_down = d3.selectAll(".jq-dropdown-menu");
      // var drop_down = d3.selectAll("form")
      //                     .append("select")
      //                     // .on("click", tiny_spinner)
      //                     .on("change", change);
      
      // var famousnames = [];
      // famous.forEach(function(obj){
      //     famousnames.push(obj.names);
      // })
      
      // drop_down.selectAll("option")
      //     // .data(famousnames)
      //     // .data(famous.names)
      //     .data(famous)
      //     .enter()
      //     .append("option")
      //     .attr("value", function(n){return n.id;})
      //     .text(function(n){return n.firstname + " " + n.lastname;});
      drop_down.selectAll("li")
          // .data(famousnames)
          // .data(famous.names)
          .data(famous)
          .enter()
          .append("li")
          .attr("value", function(n){return n.id;})
          .text(function(n){return n.firstname + " " + n.lastname;})
          // .html(function(n){return "<li>" + n.firstname + " " + n.lastname + "</li> <li class="jq-dropdown-divider"></li>";})
          .on("click", change);
    
    // Ensure that the drop-down starts on Hawking.
    // drop_down.property("selectedIndex", 10);
    
    function change(d){
        
        // Set the name selected as the person in focus.
        // var v = drop_down.property("value");
        var v = d.id;
		json.nodes.forEach(function(n){
            if (n.id.toString() === v){
                n.focus = true;
            }
            else {
		        n.focus = false
                };
		    });
        // v.focus = true;
		update();
		
    };
	
	function update(){
	    
	    // Turn off the visibility of the SVG canvas.
	    svg.attr("display", "none");
	    
	    // Turn on the spinner.
        spinner = new Spinner(opts).spin(target);
        	
		// Finding and fixing the node in focus and its ancestors.
		json.nodes.forEach(function(n){
			n.isFixed = false;
            n.fixed = false;
			n.generation = null;
			n.charge = null;
			});
		focus_node = json.nodes.filter(function(n){return n.focus})[0]; // global variable!
		focus_node.isFixed = true;
		focus_node.generation = 0;
		var advisors = [];
		var grand_advisors = [];
		var link_list = [];
		single_ancestors = false; // global variable!

		// Get advisors of the physicist in focus
		json.links.forEach(function(l){
			if (l.target === focus_node){
				var n = json.nodes.filter(function(n){return n === l.source})[0]
				n.isFixed = true;
				n.generation = -1;
				advisors.push(n);
				link_list.push(l);
			}; 
		});

		// Get the advisor's advisors for the physicist in focus.
		advisors.forEach(function(n){
			json.links.forEach(function(l){
				if (l.target === n){
					var m = json.nodes.filter(function(n){return n === l.source})[0]
					m.isFixed = true;	
					if (m.generation !== -1 && grand_advisors.indexOf(m) === -1){
					    m.generation = -2;
					    grand_advisors.push(m);
					    };
					link_list.push(l);
				}; 
			});
		});

        // Find any remaining connections among the advisors of the physicist in focus.
        grand_advisors.forEach(function(n){
		    json.links.forEach(function(l){
			    if (l.target === n){
			        if (grand_advisors.indexOf(l.source) !== -1 || advisors.indexOf(l.source) !== -1){
			            link_list.push(l);
			        };
			    };
		    });
		});

		if (advisors.length <= 1 && grand_advisors.length <= 1){single_ancestors = true};
		
		
		// next, find the children out to two generations, and other advisors of the first generation.
		var students = [];
        var grand_students = [];
		var other_advisors = [];

		// Get students of the physicist in focus
		json.links.forEach(function(l){
			if (l.source === focus_node){
				var n = json.nodes.filter(function(n){return n === l.target})[0]
				students.push(n);
				link_list.push(l);
			}; 
		});
		
		node_list = advisors.concat(grand_advisors, students, focus_node);

		// Get the students' students (or other advisors of the students) for the physicist in focus.
		// There's a way to unify this with the loop above, but forget that for now.
		students.forEach(function(n){
			json.links.forEach(function(l){
			    // We're not populating grand-students on mobile, because it's just too intensive.
			    // Or ARE WE?
                // if (l.source === n){
                //  var m = json.nodes.filter(function(n){return n === l.target})[0]
                //                     if ((node_list.indexOf(m) === -1) && (other_advisors.indexOf(m) === -1) && (grand_students.indexOf(m) === -1)) {
                //                         grand_students.push(m);
                //                     };
                //                     link_list.push(l);
                // }; 
				if (l.target === n){
					if (l.source !== focus_node){
						link_list.push(l);
						var m = json.nodes.filter(function(n){return n === l.source})[0]
						if ((node_list.indexOf(m) === -1) && (other_advisors.indexOf(m) === -1) && (grand_students.indexOf(m) === -1)) {
                            other_advisors.push(m);
                            };
					};
				};
			});
		});
		
		// Finally, concatenate them all into a list of nodes
        node_list = node_list.concat(grand_students, other_advisors);
		
		// If the current node has no advisors, give it a generation of -1, 
		// so it will have a large charge and sit higher on the page.
		if (advisors.length + grand_advisors.length === 0){focus_node.generation = -1};
	    
		force.nodes(node_list)
	      .links(link_list)
          // .start();
		
		// Make sure that none of the non-ancestors start out up top, 
		// and that all the ancestors start near the center of the top.
		// This should make it hard for any stray branches to get caught up near the ancestors,
		// since we're giving the ancestors huge charges.
		var not_ancestors = students.concat(grand_students, other_advisors);
		var ancestors = advisors.concat(grand_advisors);
		not_ancestors.forEach(function(n){
		    if (n.y < h/2){ 
		        n.y += h/2; 
		        };
		});
		ancestors.forEach(function(n){
		    var distance  = n.x - w/2
		    if (Math.abs(distance) > w/4){
		        n.x -= distance/Math.abs(distance) * w/4;
		    }
		})
		
		links = svg.selectAll("line")
				.data(link_list);
		
		links.enter()
		.append("line")
		.style("marker-end", "url(#arrowhead)");
		
		links.exit().remove();
		
		svg.selectAll("text").remove();

        // svg.selectAll("circle").remove();
        svg.selectAll("g.circle-g").remove();
	    	
        var color = d3.scale.linear()
                                // .domain([0, 1, 2, 3, 5, 7, 9, 12, 17, 26])
                                // .range(["#08306B", "#9ECAE1", "#DEEBF7"]);
                                // .range(["#08306B", "#DEEBF7", "#F7FBFF"]);
                                // .range(["#08306B", "#08519C", "#2171B5", "#4292C6", "#6BAED6", "#9ECAE1", "#C6DBEF", "#DEEBF7", "#F7FBFF", "#FFFFFF"]);
                                .domain([0, 6, 11, 28]) // 18])
                                .range(["#2171B5", "#6BAED6", "#BDD7E7", "#EFF3FF"]);
                
        var featured_color = d3.scale.linear()
                        .domain([0, 6, 11, 28]) // 18])
                                .range(["#D94701", "#FD8D3C", "#FDBE85", "#FEEDDE"]);
        
                // Figure out how far the closest person to Hawking is.
        var min_distance = 100; // impossible dummy value
                // node_list.reduce(function(pv, cv, i, a){
                //     return Math.min(pv.distance, cv.distance)
                //     });
                node_list.forEach(function(n){
            min_distance = Math.min(min_distance, n.distance);
            });
            
                // // Colors
                // var color = d3.scale.linear()
                //                          // .domain([0, 1, 2, 3, 4])
                //                          .domain([4, 3, 2, 1, 0])
                //                          .range(["#EFF3FF", "#BDD7E7", "#6BAED6", "#3182BD", "#08519C"]);
                //          
                // var featured_color = d3.scale.linear()
                //                         // .domain([0, 1, 2, 3, 4])
                //                         .domain([4, 3, 2, 1, 0])
                //                         .range(["#FEEDDE", "#FDBE85", "#FD8D3C", "#E6550D", "#A63603"]);
		
		node_gs = svg.selectAll("g.circle-g")
	    	.data(node_list);
		
        node_gs.enter().append("g").attr("class", "circle-g");
        
        node_gs.append("circle")
            .attr("class", "underlay")
            .attr("r", function(d){
             if (d.famous){
                 return r
             }
                else {return small_r};
             })
            .style("fill", "white")
            .style("stroke", "white")
            .style("opacity", 1);
        
        nodes = node_gs.append("circle")
         .attr("r", function(d){
             if (d.famous){
                 return r
             }
                        else {return small_r};
             })
             .style("fill", function(d) {
                        // if (d.famous || d.highlighted){
                        //  return "blue";
                        // }
                        // else {
                        //  return "#1BB2E0";
                        // };
                        //
                        // if (d.id === hawking_id){
                        //     // return "#08306B";
                        //     return color(d.distance);
                        // }
                        // else 
                        if (d.famous || d.highlighted){
                            // return "blue";
                            return featured_color(d.distance);
                            // return featured_color(d.distance - min_distance);
                        }
                        else {
                            return color(d.distance);
                            // return color(d.distance - min_distance);
                        };
             })
                     .style("stroke", function(d) { 
                            // return d3.rgb(fill(d.group)).darker();
                            return "black" 
                         })
                        .style("opacity", function(d){
                                            return (10 - (d.distance - min_distance))/10;
                        })
                     .on("click", click)
                     // .on("mouseover", tooltip_over)
                     // .on("mouseout", function(d){tooltip.classed("hidden", true);});
                     // .call(force.drag);
	
        // svg.selectAll(".underlay").call(force.drag);
	
	    svg.selectAll("g.name").remove(); // to ensure that the names are drawn LAST.
	    
	    names = svg.selectAll("g.name")
	                .data(node_list);
	                
	    names.enter().append("g")
	            .attr("class", "name");
	    
	    shadows = names.append("text")
	            .attr("class", "shadow")
	            .text(function(d){
    				if (d.famous || d.focus || d.highlighted){
    					return d.name;
    				};
    			})
    			.attr("font-size", label_size)
    			.attr("x", function(d){return d.x})
    			.attr("y", function(d){return d.y})
    			.style("fill", "white")
    			.attr("opacity", 0.85);
    	
    	names_t = names.append("text")
	            .text(function(d){
    				if (d.famous || d.focus || d.highlighted){
    					return d.name;
    				};
    			})
    			.attr("class", "name")
    			.attr("font-size", label_size)
    			.attr("x", function(d){return d.x})
    			.attr("y", function(d){return d.y})
    			.style("fill", "black"
                // function(d){
                    // // this function actually calculates the width of the text and saves it in a variable.
                    // // I'm putting it here so we don't have to recompute it each tick, 
                    // // which would slow things down considerably.
                    // d.name_width = this.getComputedTextLength();
                    // return "black";
                // }
    			)
    			.on("click", click);
    	
    	force.on("tick", tick);

        // This will, among other things, turn the SVG visibility back on.
    	force.on("end", showtick); // ADDED FOR MOBILE TESTING -- AMB 03/2014

        force.start();
        for (var i = 0; i < num_ticks; ++i) force.tick();
        force.stop();
    	
		panel_update(focus_node);
		
	};

	update();
    // resize();
    // d3.select("body").append("p")
    //   .html('<font id="source">Source: <a href="http://genealogy.math.ndsu.nodak.edu/" target="_blank">Mathematics Genealogy Project</font></a>');
    //   $("#source").css("bottom", 0);
    // var panel_bottom = $("#panel").offset().top + $("#panel").outerHeight();
    // // d3.select("#source").style("top", panel_bottom).style("right", 0)
    // // $("#source").css("bottom", "");
    // $("#source").css("top", panel_bottom);

	function click(d){
        // // Don't register a click if there was also a dragging behavior.
        // if (d3.event.defaultPrevented) return; // ignore drag
        // If there wasn't dragging, then click!
        bare_click(d);
	};

    function bare_click(d){
		// Set this node as the one that's in focus.
        // json.nodes.forEach(function(n){n.focus = false;}) // hideously inefficient
        focus_node.focus = false;
		d.focus = true;
        // // Make sure the tooltip goes away. Stay classy.
        //         tooltip.classed("hidden", true);
		// Update the display!
		update();
	};

	function tick(e) {
		
		// // Push sources up and targets down to form a weak tree.
		// 	    var k = 6 * e.alpha;
		// 	    json.links.forEach(function(d, i) {
		// 	      d.source.y -= k;
		// 	      d.target.y += k;
		// 	    });

		focus_node.x = w/2;
		// focus_node.y = h/2;
		focus_node.fixed = true;

		json.nodes.forEach(function(d){
			// ancestors.forEach(function(d){
				if (d.isFixed){
					if (single_ancestors){
						d.fixed = true;
						d.x = w/2
						};
					d.y = h/2 + 2*d.generation*link_length;
			};
			// else {d.fixed = false};
		});

	};
	
	function showtick(e) {
		
		// // Push sources up and targets down to form a weak tree.
		// 	    var k = 6 * e.alpha;
		// 	    json.links.forEach(function(d, i) {
		// 	      d.source.y -= k;
		// 	      d.target.y += k;
		// 	    });

		focus_node.x = w/2;
		// focus_node.y = h/2;
		focus_node.fixed = true;

		json.nodes.forEach(function(d){
			// ancestors.forEach(function(d){
				if (d.isFixed){
					if (single_ancestors){
						d.fixed = true;
						d.x = w/2
						};
					d.y = h/2 + 2*d.generation*link_length;
			};
			// else {d.fixed = false};
		});
    
        // Keep the circles in the alloted space.
        // nodes.attr("cx", function(d) { return d.x = Math.max(r, Math.min(w - r, d.x)); })
        svg.selectAll("circle").attr("cx", function(d) { return d.x = Math.max(r, Math.min(w - r, d.x)); })
         .attr("cy", function(d) { return d.y = Math.max(r, Math.min(h - r, d.y)); });
    
    links.attr("x1", function(d) { return d.source.x; })
          .attr("y1", function(d) { return d.source.y; })
          .attr("x2", function(d) { return d.target.x; })
          .attr("y2", function(d) { return d.target.y; });
        
        // This one is tricky -- the names don't have fixed sizes.
        // So we'll find the length of the name using this.getComputedTextLength(),
        // and use it to prevent the text from leaving the space.
        
        names_t.attr("x", function(d) {
                         var text_width = this.getComputedTextLength();
                         return Math.max(text_width/2, Math.min(w - text_width/2, d.x));
                })
             .attr("y", function(d) {
                         return Math.max(label_size, d.y - r);
             });
                
        shadows.attr("x", function(d) {
                         var text_width = this.getComputedTextLength();
                         return Math.max(text_width/2, Math.min(w - text_width/2, d.x));
                })
             .attr("y", function(d) {
                         return Math.max(label_size, d.y - r);
             });
        
        // Turn off the spinner.
 	    spinner.stop();
     	    
        // Turn the visibility of the SVG canvas back on.
	    svg.attr("display", null);

	};
	
    function panel_update(node){
        
        // Updating the panel for the person in focus, if they're famous.
        
        var panel = d3.select("#panel");
        
        if (node.famous){
            
            w_panel = $("#panel").width();
            
            // First, remove anything that's already there.
            panel.select("h3").remove();
            panel.selectAll("p").remove();
            panel.selectAll("img").remove();
            panel.selectAll("a").remove();
        
            // Now put in the new stuff.
            panel.append("h3").text(node.name)
        
            // Get the person's image and blurb.
            var fame_data = famous.filter(function(n){return n.id === node.id.toString()})[0]
            // Put the image in.
            panel.append("img")
                .attr("id", "picture")
                .attr("src", "img/" + fame_data.picture_file)
                // .attr("height", h/2)
                .attr("width", pic_width_factor*w_panel)
                .style("float", "left");
            
            // Put the blurb in.
            panel.append("p").html(fame_data.blurb);
            
            // COMMENTED THIS OUT FOR MOBILE TESTING -- AMB 03/2014
            // Make sure things stay the right size.
            
            $("#picture").one('load', resize)
            .each(function() {
              if(this.complete) $(this).load();
            });
            
            // resize();
        };
    };

    // function tooltip_over(node){
    // 
    //     // //Get the x/y values for the tooltip based on the position of the mouse.
    //     var xPosition = d3.mouse(svg[0][0])[0] + tooltip_offset; // don't want it directly under the pointer
    //     var yPosition = d3.mouse(svg[0][0])[1];
    //     
    //     tooltip.selectAll("p").remove();
    //     
    //     //Update the tooltip position and value
    //     var text = tooltip.style("width", tooltip_width + "px")
    //         .style("left", xPosition + "px")
    //         .style("top", yPosition + "px")
    //         .append("p")
    //        // .attr("font-size", label_size)
    //         .attr("class", "name")
    //         .text(node.name)
    //          .append("p")
    //         // .attr("font-size", label_size)
    //          .attr("class", "name")
    //          .text("Degrees from Hawking: " + node.distance);
    //             
    //     //Show the tooltip
    //     tooltip.classed("hidden", false);
    //     
    // };
    
    // $("#viz").resize(function(){
    //     h = $("#viz").height();
    //    svg.attr("height", h);
    // });
    
    function resize() {
        
        old_w = w;
        old_h = h;
        
        console.log("resizing is happening!")

        // // Turn on the spinner.
        //         spinner = new Spinner(opts).spin(target);
        
        w = $("#viz").width();
        w_panel = $("#panel").width();
        d3.select("#picture").attr("width", pic_width_factor*w_panel);
        // h = document.getElementById(divID).innerHeight;
        
        h = $("#panel").height();
        // console.log(h);
        
        // pos = $("#viz").offset();
        // h = $(window).height() - pos.top - $("#source").height() - 10;
        // console.log(h)
        // // h = $(window).height() - $("#source").height() - $("#header").height() - $("#viz").prop("offsetTop");
        // h = Math.max(250, h);
        
        link_length = Math.min(w, h)/20;
                
        force.linkDistance(link_length)
                .size([w, h]);
        
        node_list.forEach(function(d){
            d.x = d.x + (w - old_w)/2
            d.y = d.y + (h - old_h)/2
        });
        
        // // Run the showtick function.
        force.start();
        force.stop();
        
        svg.attr("width", w);
        
         // h = $("#viz").height();
        svg.attr("height", h);
        
        try
        {        
            var panel_bottom = $("#panel").offset().top + $("#panel").outerHeight();
            // d3.select("#source").style("top", panel_bottom).style("right", 0)
            console.log($("#source").offset().top); // this is here SOLELY to throw an error if the source credit hasn't been created yet.
            $("#source").css("bottom", "");
            $("#source").css("top", panel_bottom);
        }
        catch(err){
            // This was the only way I could figure out of creating the source credit in the right location on the first try.
            // Though I suppose I could have made it appear in the wrong location, invisible, and make it visible later...
            // console.log(err)
            // console.log("hello!")
            d3.select("#content").append("p")
              .html('<font id="source">Source: <a href="http://genealogy.math.ndsu.nodak.edu/" target="_blank">Mathematics Genealogy Project</a>; produced by Adam Becker and Peter Aldhous, published xx xxxxxx 2015.</font>');
              // $("#source").css("bottom", 0);
              var panel_bottom = $("#panel").offset().top + $("#panel").outerHeight();
              // d3.select("#source").style("top", panel_bottom).style("right", 0)
              // $("#source").css("bottom", "");
              $("#source").css("top", panel_bottom);
        };
    
    };
    
    $(window).resize(resize);

//     d3.json("json/everything.json", function(new_json) {
//                 
//         new_force = d3.layout.force()
//          .charge(function(n){
//          if (n.generation <= -1) {return ancestor_charge;}
//          else if (n.famous) {return famous_charge;}
//          else {return charge;};
//          })
//          .linkDistance(function(l){
//                 if (l.target.famous ){ 
//                    return 2*link_length;
//                    }
//                   else {
//                  return link_length
//                     };
//          })
//             .linkStrength(link_strength)
//             .gravity(gravity)
//             .friction(friction)
//             .theta(theta)
//          .size([w, h])
//         
//         new_force.nodes(new_json.nodes)
//           .links(new_json.links)
//           // .start();
//           
//         // d3.select("#" + divID).style("background", "#009900");
//         
//         // On the next node click after the new network is loaded, the old network is replaced with the new.
//         // new_click() calls click(), and click() calls update(), 
//         // and update() sets the click action to click(),
//         // so this will only happen once.
//         names_t.on("click", new_click);
//         nodes.on("click", new_click);
//         
//         // And the drop-down menu.
//         // new_change() resets the drop-down change action to change(), so this will only happen once. 
//         drop_down.on("change", new_change);
//         
//         function new_click(d){
//             //             // Don't register a click if there was also a dragging behavior.
//             // if (d3.event.defaultPrevented) return; // ignore drag
//             new_d = new_json.nodes.filter(function(n) {return d.name === n.name})[0];
//             // if (new_json !== json){
//                 force = new_force;
//                 json = new_json;
//                 force.start();
//             // };
//             click(new_d);
//         };
//         
//         function new_change(){
//             if (new_json !== json){
//                 force = new_force;
//                 json = new_json;
//                 force.start();
//             };
//             change();
//             drop_down.on("change", change)
//         };
//         
//         // force = new_force;
//         // json = new_json;
//         // update();
//         
//         console.log("Updating autocomplete!");
//         console.log(new_json === json);
//         
//         // Finally, update the source for the autocompleting search bar.
//         autolist = [],
//             index = 0;
//         new_json.nodes.forEach(function(n){
//             autoperson = {"label":n.name, "value":index};
//             autolist.push(autoperson);
//             index += 1;
//         });
//             
//         // Removing the old autocomplete function!
//         $("#autocomplete").off("autocompleteselect");
//          
//         // Putting in the new one!
//         $("#autocomplete").on("autocompleteselect", function(event, ui){ 
//              // First, stop the default action, which is to populate the text box with the value of the chosen item.
//              // In this case, the value is the ID -- a meaningless number between 1 and 180,000 which would only confuse the user.
//              // We definitely don't want that!
//                 event.preventDefault();
//              // Now populate the field with the actual name selected.
//              $(this).prop("value", ui.item.label);
//              // Update the global variables.
//              if (new_json !== json){
//                  force = new_force;
//                  json = new_json;
//                  force.start();
//              };
//              // Finally, fire off the click() function with the appropriate node!
//              console.log(ui.item.value);
//              person = new_json.nodes[ui.item.value];
//              console.log(person);
//              bare_click(person);
//              // And revert the action to the old action!
//              $("#autocomplete").off("autocompleteselect");
//              $("#autocomplete").on("autocompleteselect", selection_event);
//              // $(this).on("autocompleteselect", function(event, ui){
//              //    event.preventDefault();
//              //     person = json.nodes[ui.item.value];
//              //     click(person);
//              //    });
//              });
//     
// 
// });
});
});
