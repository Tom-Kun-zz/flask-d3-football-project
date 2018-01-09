$(function() {
	console.log('jquery is working!');
    $('button').click(function() {
        var home = $('#home_team').val();
        var away = $('#away_team').val();
        $.ajax({
            url: '/send_teams',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
	loadData();
	createGraph();
	predictMatch();
});

function loadData() {
	d3.json("/data", function(error, data) {
		function create_table(data, columns) {
			var table = d3.select('#results').append('table')
			var thead = table.append('thead')
			var tbody = table.append('tbody');

			// append the header
			thead.append('tr')
				.selectAll('th')
				.data(columns).enter()
				.append('th')
					.text(function (column) { return column; });

			// create a row for each json object in the data
			var rows = tbody.selectAll('tr')
				.data(data)
				.enter()
				.append('tr');

			var cells = rows.selectAll('td')
				.data(function (row) {
					return columns.map(function (column) {
						return { column: column, value: row[column]};
					});
				})
				.enter()
				.append('td')
					.text(function (d) { return d.value; });
			return table
		}

		// render the table
		create_table(data, ['HomeTeam', 'AwayTeam', 'HomeGoals', 'AwayGoals', 'HomeHalfGoals', 'AwayHalfGoals'])
	});
}

function createGraph() {
	// set the dimensions of the canvas
	var margin = {top: 20, right: 20, bottom: 70, left: 40},
	    width = 1000 - margin.left - margin.right,
	    height = 600 - margin.top - margin.bottom;

	// set colors
	var colorRange = d3.scaleOrdinal(d3.schemeCategory20);;
	var color = d3.scaleOrdinal()
	    .range(colorRange.range());


	// set the ranges
	var x0 = d3.scaleBand()
	    .rangeRound([0, width])
	    .padding(.1);

	var x1 = d3.scaleBand();

	var y = d3.scaleLinear()
	    .range([height, 0]);

	// define the axis
	var xAxis = d3.axisBottom(x0);

	var yAxis = d3.axisLeft(y)
	    .tickFormat(d3.format(".2s"));

	// add the SVG element
	var svg = d3.select("#goals").append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	// load the data from goals home and away
	d3.json("/goals", function(error, data) {
		var options = d3.keys(data[0]).filter(function(key) { return key !== "Goals"; });
		//console.log(options);

		data.forEach(function(d) {
	    	d.values = options.map(function(name) { return {name: name, value: +d[name]}; });
	    	//console.log(d.values);
	    });

	  	x0.domain(data.map(function(d) { return d.Goals; console.log(d.Goals) }));
		x1.domain(options).rangeRound([0, x0.bandwidth()]);
		y.domain([0, d3.max(data, function(d) { return d3.max(d.values, function(d) { return d.value; }); })]);

		var divTooltip = d3.select("body").append("div").attr("class", "toolTip");

	 	// add axis
	 	// axis X
		svg.append("g")
		    .attr("class", "x axis")
		    .attr("transform", "translate(0," + height + ")")
		    .call(xAxis);

		// axis Y
		svg.append("g")
		    .attr("class", "y axis")
		    .call(yAxis)
		    .append("text")
		    .attr("transform", "rotate(-90)")
		    .attr("y", 6)
		    .attr("dy", ".71em")
		    .style("text-anchor", "end")
		    .text("Goals scored");

	  	// Add bar chart
	  	// Create variable which will contain the different bar to build the chart
	  	var bar = svg.selectAll(".bar")
	    	.data(data)
	    	.enter().append("g")
	    	.attr("class", "rect")
	    	.attr("transform", function(d) { return "translate(" + x0(d.Goals) + ",0)"; });

		bar.selectAll("rect")
		    .data(function(d) { return d.values; })
		    .enter().append("rect")
		    .attr("width", x1.bandwidth())
		    .attr("x", function(d) { return x1(d.name); })
		    .attr("y", function(d) { return y(d.value); })
		    .attr("value", function(d){return d.name;})
		    .attr("height", function(d) { return height - y(d.value); })
		    .style("fill", function(d) { return color(d.name); });

		bar.on("mousemove", function(d){
	        divTooltip.style("left", d3.event.pageX+10+"px");
	        divTooltip.style("top", d3.event.pageY-25+"px");
	        divTooltip.style("display", "inline-block");
	        var x = d3.event.pageX, y = d3.event.pageY
	        var elements = document.querySelectorAll(':hover');
	        l = elements.length
	        l = l-1
	        elementData = elements[l].__data__
	        divTooltip.html(elementData.name+"<br>"+elementData.value);
	    });

		bar.on("mouseout", function(d){
	        divTooltip.style("display", "none");
	    });

		// Create the chart's legend
		var legend = svg.selectAll(".legend")
	    	.data(options.slice())
	    	.enter().append("g")
	    	.attr("class", "legend")
	    	.attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

		legend.append("rect")
	    	.attr("x", width - 18)
	    	.attr("width", 18)
	    	.attr("height", 18)
	    	.style("fill", color);

		legend.append("text")
	    	.attr("x", width - 24)
	    	.attr("y", 9)
	    	.attr("dy", ".35em")
	    	.style("text-anchor", "end")
	    	.text(function(d) { return d; });
	});
}

function predictMatch() {
	d3.json("/send_teams", function(error, data) {
		data.forEach(function(d) {
	    	d.home_team = +d.home_team;
	    	d.away_team = +d.away_team;
	    });
	    console.log(data[0]);	
	});
}