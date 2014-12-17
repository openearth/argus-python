(function( $, undefined ) {
    
    var thisObject = this;
    
    $.widget( "ui.argusImageDisplay", {
	version: "0.0.1",
	options: {
	    imageHost: "/image/",
            datasetHost: "/datasets/",
            dataset: null,
            image: null,
	    classes: null,
	    background: true,
	    colors: {},
	    select: null,
	    linkedTo: null,
	},

	_objImageCanvas: null,

	_create: function() {
	    var thisObject = this;

	    $(window)
                .bind("keydown", function(e) { thisObject._keydown(e); })

	    this._objImageCanvas = this._getImageCanvas();
	    $(this.element).append(this._objImageCanvas);

	    this._getImageOverlay();	    
	},

        _keydown: function(e) {
            switch (e.keyCode) {
            case 37:
                this._highlightAdjacentSuperpixel("left");
                break;
            case 38:
                this._highlightAdjacentSuperpixel("up");
                break;
            case 39:
                this._highlightAdjacentSuperpixel("right");
                break;
            case 40:
                this._highlightAdjacentSuperpixel("down");
                break;
	    }
	},

	/*****************************************************************************
	 ** PUBLIC FUNCTIONS                                                        **
	 *****************************************************************************/

	getImage: function(ds, im) {
	    this.options.dataset = ds;
	    this.options.image   = im;

	    this._getImageOverlay();
	},

	/*****************************************************************************
	 ** GUI CONSTRUCTORS                                                        **
	 *****************************************************************************/

	_getImageCanvas: function() {
            var objCanvas = document.createElementNS("http://www.w3.org/2000/svg", "svg")

            objCanvas.width  = objCanvas.clientWidth;
            objCanvas.height = objCanvas.clientHeight;

	    var obj = $("<div>")
		.addClass("display-image")
		.append($("<div>").append(objCanvas));

	    return obj
	},

        _getImageOverlay: function() {
            var thisObject = this;

	    var obj = $(this._objImageCanvas).find("svg")[0];

	    $(obj).parent().addClass("loading");

	    if (this.options.dataset != null && this.options.image != null) {

		var qs = "?keys=url,contours,width,height,nx,ny&callback=?";
		var json_url = this.options.datasetHost + this.options.dataset + "/" + this.options.image + qs;

		$.getJSON(json_url, function(data) {
		    thisObject._url      = data["url"];
                    thisObject._contours = data["contours"];
                    thisObject._width    = data["width"];
                    thisObject._height   = data["height"];
                    thisObject._nx       = data["nx"];
                    thisObject._ny       = data["ny"];

		    thisObject._setImageBackground(obj);
		    thisObject._drawSuperpixelRaster(obj);
		    thisObject._fillSuperpixelRaster(obj);

		    $(obj).parent().removeClass("loading");
		});
            }
        },
	
	/*****************************************************************************
	 ** ACTION HANDLERS                                                         **
	 *****************************************************************************/

	_setImageBackground: function(obj) {
	    if (this.options.background) {
		$(obj)
		    .parent()
		    .css("background-image","url(" + this.options.imageHost + this._url + ")");
	    }
	},

        _drawSuperpixelRaster: function(obj) {
            var thisObject = this;

            d3
		.select(obj)
                .attr("preserveAspectRatio","none")
                .attr("viewBox","0,0," + this._width + "," + this._height);

            var objs = d3
		.select(obj)
		.selectAll(".superpixel")
                .data(this._contours, function(d) { return d; });

            objs
                .enter()
                .append("path");

            objs
                .exit()
                .remove()

            objs
                .attr("class", "superpixel")
                .attr("id", function(d,i) { return "superpixel_" + i; })
                .attr("nr", function(d,i) { return i; })
                .attr("d", function(d) { return thisObject._getSVGPath(d); })
                .on("click", function() {
                    thisObject._highlightSuperpixel(
                        parseInt(d3.select(this).attr("nr"))); });
        },

        _fillSuperpixelRaster: function(obj) {
	    var thisObject = this;
	    var classes = this.options.classes;

	    if (classes != null && classes.length > 0) {
		d3
		    .select(obj)
		    .selectAll(".superpixel")
                    .classed("hasclass", function(d,i) {
			return classes[i] != null; })
                    .style("fill", function(d,i) {
			return thisObject._getClassColor(classes[i]); });
	    }
        },

        _highlightSuperpixel: function(idx) {
	    if (this.options.select == null) {
		if (this._contours != null) {
                    if (idx >= this._contours.length) idx = idx - this._contours.length;
                    if (idx < 0) idx = idx + this._contours.length;
                    this._currentSuperpixel = idx;

		    var objs = this._objImageCanvas;

		    d3
			.selectAll(objs)
			.selectAll("svg")
			.selectAll(".superpixel")
			.classed("selected",false);
		    d3
			.selectAll(objs)
			.selectAll("svg")
			.select("#superpixel_" + idx)
			.classed("selected",true);
		}
	    } else {
		this.options.select(this, idx);
	    }
        },

        _highlightAdjacentSuperpixel: function(side) {
            switch (side) {
            case "left":
                this._highlightSuperpixel(this._currentSuperpixel - 1);
                break;
            case "right":
                this._highlightSuperpixel(this._currentSuperpixel + 1);
                break;
            case "up":
                this._highlightSuperpixel(this._currentSuperpixel - this._ny);
                break;
            case "down":
                this._highlightSuperpixel(this._currentSuperpixel + this._ny);
                break;
            }
        },

        _getClassColor: function(name) {
	    if ($.isEmptyObject(this.options.colors)) {
		var classes = $.unique(this.options.classes);
		for (var i = 0; i < classes.length; i++) {
		    this.options.colors[classes[i]] = this._getRandomColor();
		}
	    }
		
	    return this.options.colors[name];
        },

	/*****************************************************************************
	 ** HELPER FUNCTIONS                                                        **
	 *****************************************************************************/

        _getRandomColor: function() {
            color = "#";
            for (var i = 0; i < 3; i++) {
                color = color + Math.round(100 + Math.random() * 155).toString(16);
            }
            return color;
        },

        _getSVGPath: function(contours) {
            p = "";
            for (var i = 0; i < contours.length; i++) {
                pi = new Array();
                for (var j = 0; j < contours[i].length; j++) {
                    w = contours[i][j][0][0];
                    h = contours[i][j][0][1];
                    pi[j] = w + "," + h;
                }
                p = p + "M" + pi.join("L");
            }
            return p;
        },
    });
    
})( jQuery );
