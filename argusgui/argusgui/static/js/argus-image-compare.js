(function( $, undefined ) {
    
    var thisObject = this;
    
    $.widget( "ui.argusImageCompare", {
	version: "0.0.1",
	options: {
	    jsonHost: "/",
	    imageHost: "/image/",
            datasetHost: "/datasets/",
            dataset: "argusnl",
            image: null,
	},

	_progress: {},
	_objDatasetSelector: null,
	_objImageDisplay: null,
	
	_create: function() {
	    var thisObject = this;
	    
	    objClr = '<div style="clear:both;">';
	    
	    $(this.element).addClass("argus-image-compare");

	    $(this.element).append($("<div>").attr("id","log"));
	    
	    this._objDatasetSelector = this._getDatasetSelector();
	    this._objImageDisplay = this._getImageDisplay();

	    $(this.element).prepend(this._objImageDisplay);
	    $(this.element).prepend(this._objDatasetSelector);

	    this._getImages();
	    
	    this._resize();
	},
	
	_resize: function() {
	    w = $(this.element).width();
	    h = $(this.element).height();
	},

	/*****************************************************************************
	 ** PUBLIC FUNCTIONS                                                        **
	 *****************************************************************************/

	/*****************************************************************************
	 ** GUI CONSTRUCTORS                                                        **
	 *****************************************************************************/

	_getDatasetSelector: function() {
	    var thisObject = this;

	    var obj = $("<div>")
		.addClass("argus-image-compare-datasets");

	    var objDatasets = $("<div>")
		.css("float","left")
		.appendTo(obj);

	    $("<input>")
		.attr("value","compare")
		.css("float","right")
		.on("click", function() { thisObject._getImages(); })
		.button()
		.appendTo(obj);

            var json_url = this.options.datasetHost;

            $.getJSON(json_url, function(data) {
		for (var i = 0; i < data.length; i++) {
		    objId = "argus-image-compare-dataset-" + data[i].replace(/[^\w\d]+/,'');

		    $("<input>")
			.attr("id",objId)
			.attr("type","checkbox")
			.attr("name","datasets[]")
			.attr("value",data[i])
			.appendTo(objDatasets);

		    $("<label>")
			.attr("for",objId)
			.html(data[i])
			.appendTo(objDatasets);
		}

		$(objDatasets).buttonset("refresh");
	    });

	    $(objDatasets).buttonset();

	    return obj;
	},

	_getImageDisplay: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>")
		.addClass("argus-image-compare-display");

	    return obj;
	},

	_getImages: function() {
	    var thisObject = this;
	    var obj = this._objImageDisplay;

	    $(obj).html("");

            var objCanvas = document.createElementNS("http://www.w3.org/2000/svg", "svg")

            objCanvas.width = objCanvas.clientWidth;
            objCanvas.height = objCanvas.clientHeight;

	    this._progress['comparison'] = false;
	    this._progress['raster'] = {};
	    this._progress['assignment'] = {};
	    this._showProgress();

	    var objs = this._objDatasetSelector.find("input:checked");
	    var datasets = new Array();
	    for (var i = 0; i < objs.length; i++) {
		datasets[i] = $(objs[i]).val();
	    }

            var json_url = this.options.datasetHost + "compare/?datasets=" + datasets.join();

            $.getJSON(json_url, function(data) {
		thisObject.options.dataset = data[1][0];
		
		if (!$.isEmptyObject(data[0])) {

		    var objTabs = $("<ul>")
			.appendTo(obj)

		    var n = 1;
		    $.each(data[0], function(im, comparison) {
			
			thisObject._progress['raster'][im] = false;
			thisObject._progress['assignment'][im] = {};
			thisObject._showProgress();
			
			$("<li>")
			    .append(
				$("<a>")
				    .attr("href","#tab-" + n)
				    .attr("title",im)
				    .text(im))
			    .appendTo(objTabs);
			
			var objTab = $("<div>")
			    .attr("id","tab-" + n)
			    .appendTo(obj);
			
			$("<div>")
			    .addClass("display-image")
			    .addClass("display-image-original")
			    .append($("<div>").append($(objCanvas).clone()))
			    .appendTo(objTab);
			
			$("<div>")
			    .addClass("display-image")
			    .addClass("display-image-diff")
			    .append($("<div>").append($(objCanvas).clone()))
			    .appendTo(objTab);

			for (var i = 0; i < data[1].length; i++) {
			    $("<div>")
				.addClass("display-image")
				.addClass("display-image-dataset")
				.attr("dataset",data[1][i])
				.attr("title",data[1][i])
				.append($("<div>").append($(objCanvas).clone()))
				.appendTo(objTab);
			}

			thisObject._getImageOverlay(objTab, im, comparison);

			n++;
		    });

		    $(obj)
			.tabs("refresh")
			.tabs("option","active",0);
		} else {
		    $("<div>")
			.css("margin","10px")
			.text("No images to compare")
			.appendTo(obj);
		}

		thisObject._progress['comparison'] = true;
		thisObject._showProgress();
	    });

	    $(obj).tabs();
	},

        _getImageOverlay: function(obj, im, comparison) {
            var thisObject = this;

            var qs = "?keys=url,contours,width,height,nx,ny&callback=?";
	    var json_url = this.options.datasetHost + this.options.dataset + "/" + im + qs;

            $.getJSON(json_url, function(data) {
                var objs = $(obj).find(".display-image svg");
		for (var i = 0; i < objs.length; i++) {
                    thisObject._drawSuperpixelRaster(objs[i], data["width"], data["height"], data["contours"]);

		    switch (i) {
		    case 0:
			$(objs[i]).css("background-image","url(" + thisObject.options.imageHost + data["url"] + ")");
			break;
		    case 1:
			thisObject._fillSuperpixelRaster(objs[i], comparison);
			break;
		    default:
			thisObject._getAssignments(objs[i], im);
			break;
		    }
		}

		thisObject._progress['raster'][im] = true;
		thisObject._showProgress();
            });
        },

	_getAssignments: function(obj, im) {
            var thisObject = this;
	    var ds = $(obj).parent().parent().attr("dataset");

	    this._progress['assignment'][im][ds] = false;
	    this._showProgress();

            var qs = "?keys=assignments&callback=?";

	    var json_url = this.options.datasetHost + ds + "/" + im + qs;

            $.getJSON(json_url, function(data) {
		thisObject._fillSuperpixelRaster2(obj, data["assignments"]);
		thisObject._progress['assignment'][im][ds] = true;
		thisObject._showProgress();
	    });
	},
	
	/*****************************************************************************
	 ** ACTION HANDLERS                                                         **
	 *****************************************************************************/

        _drawSuperpixelRaster: function(obj, w, h, contours, comparison) {
            var thisObject = this;

            d3.select(obj)
                .attr("preserveAspectRatio","none")
                .attr("viewBox","0,0," + w + "," + h);

            var objs = d3.select(obj).selectAll(".superpixel")
                .data(contours, function(d) { return d; });

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
                .attr("d", function(d) {
                    return thisObject._getSVGPath(d,
                                                  $(obj).width()/w,
                                                  $(obj).height()/h); })
                .on("click", function() {
                    thisObject._highlightSuperpixel(
                        parseInt(d3.select(this).attr("nr"))); });
        },

        _fillSuperpixelRaster: function(obj, comparison) {
            var thisObject = this;

            d3.select(obj).selectAll(".superpixel")
                .classed("match", function(d,i) {
		    if (comparison.length > i) {
			return !comparison[i];
		    } else {
			return false;
		    } })
                .classed("nomatch", function(d,i) {
		    if (comparison.length > i) {
			return comparison[i];
		    } else {
			return false;
		    } });
        },

        _fillSuperpixelRaster2: function(obj, values) {
            var thisObject = this;

	    if (values.length > 0) {
		d3.select(obj).selectAll(".superpixel")
                    .classed("classified", function(d,i) {
			return values[i] != null; })
                    .style("fill", function(d,i) {
			return thisObject._getClassColor(values[i]); });
	    }
        },

        _highlightSuperpixel: function(idx) {
            d3
                .selectAll(".argus-image-compare-display svg")
                .selectAll(".superpixel")
                .classed("selected",false);
            d3
                .selectAll(".argus-image-compare-display svg")
                .select("#superpixel_" + idx)
                .classed("selected",true);
        },

        _getClassColor: function(name) {
	    switch (name) {
	    case "sky":
		return "#9999ff";
		break;
	    case "sea":
		return "#0000ff";
		break;
	    case "beach":
		return "#ffff00";
		break;
	    case "dune":
		return "#00ff00";
		break;
	    case "object":
		return "#000000";
		break;
	    case "label":
		return "#ff0000";
		break;
	    default:
		return "#aaaaaa";
		break;
	    }
        },

        _showMessage: function(title,text) {
            var obj = $("<div>")
                .append($("<p>").text(text))
                .dialog({
                    title: title,
                    height: 140,
                    modal: true,
                    buttons: {
                        "OK": function() { $(this).dialog("close"); }},
                    close: function() { $(this).dialog("destroy"); }});

            return obj;
        },

        _showOverlay: function(text) {
            var obj = this._showMessage("",text)
                .append($("<img>")
                        .attr("src","../static/jquery-ui-1.10.2/images/ui-anim_basic_16x16.gif"))
                .css("text-align","center")
                .parent()
                .addClass("overlay");
            
            return obj;
        },

        _hideOverlay: function() {
            $(".ui-dialog.overlay .ui-dialog-content").dialog("close");
        },

	_showProgress: function() {
	    var obj = $("#log");

	    $(obj).html("");

	    $("<div>")
		.css("color",(this._progress["comparison"] ? "#00ff00" : "#ff0000"))
		.text("comparison")
		.appendTo(obj);

	    $.each(this._progress["raster"], function(k,v) {
		$("<div>")
		    .css("color",(v ? "#00ff00" : "#ff0000"))
		    .text("raster " + k)
		    .appendTo(obj);
	    });

	    $.each(this._progress["assignment"], function(k,v) {
		$.each(v, function(k2,v2) {
		    $("<div>")
			.css("color",(v2 ? "#00ff00" : "#ff0000"))
			.text("assignment " + k + " from " + k2)
			.appendTo(obj);
		});
	    });
	},

	/*****************************************************************************
	 ** HELPER FUNCTIONS                                                        **
	 *****************************************************************************/

        _getSVGPath: function(contours, width_scale, height_scale) {
            p = "";
            for (var i = 0; i < contours.length; i++) {
                pi = new Array();
                for (var j = 0; j < contours[i].length; j++) {
                    w = contours[i][j][0][0];// * width_scale;
                    h = contours[i][j][0][1];// * height_scale;
                    pi[j] = w + "," + h;
                }
                p = p + "M" + pi.join("L");
            }
            return p;
        },
    });
    
})( jQuery );
