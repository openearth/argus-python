(function( $, undefined ) {
    
    var thisObject = this;
    
    $.widget( "ui.argusImageClassifier", {
	version: "0.0.1",
	options: {
	    jsonHost: "/",
	    imageHost: "/image/",
            datasetHost: "/datasets/",
            dataset: null,
            image: null,
	},

        _contours: null,
        _centroids: null,
        _classes: new Array(),
        _assignments: new Array(),
	_prediction: new Array(),
        _width: null,
        _height: null,
        _nx: null,
        _ny: null,
        _currentSuperpixel: null,
        _lastClass: null,
        _classFilter: "",
        _isChanged: false,
	_nrOfPictures: 3,
        _keyDownShift: false,
        _keyDownCtrl: false,
        _keyDownAlt: false,

	_objImageDisplay: null,
        _objClassSelector: null,
	_objQueueList: null,
        _objToolbar: null,
	
	_create: function() {
	    var thisObject = this;
	    
	    objClr = '<div style="clear:both;">';
	    
	    $(window)
                .bind("keydown", function(e) { thisObject._keydown(e); })
                .bind("keyup", function(e) { thisObject._keyup(e); })
                .bind("load", function() { thisObject._resize(); })
		.bind("resize", function() { thisObject._resize(); })
                .bind("beforeunload", function() { return thisObject._checkIfSaved(); });
	    
	    $(this.element).addClass("argus-image-classifier");
	    
            this._objToolbar = this._getToolbar();
	    this._objImageDisplay = this._getImageDisplay();
	    this._objClassSelector = this._getClassSelector();
	    this._objQueueList = this._getQueueList();

            $(this.element).append(this._objToolbar);
	    $(this.element).append(this._objImageDisplay);
	    $(this.element).append(this._objClassSelector);
	    $(this.element).append(this._objQueueList);

	    this._resize();
	},
	
	_resize: function() {
	    w = $(this.element).width();
	    h = $(this.element).height();

            imgW = parseInt((w-(20 * this._nrOfPictures))/this._nrOfPictures);
            imgH = imgW /4 * 3;

            $(this._objImageDisplay)
                .find(".display-image")
                .css("width", imgW)
                .css("height", imgH);

            $(this._objClassSelector)
                .css("height", parseInt(h-imgH-88));
	},

        _keydown: function(e) {
            switch (e.keyCode) {
            case 16:
                this._keyDownShift = true;
                break;
            case 17:
                this._keyDownCtrl = true;
                break;
            case 18:
                this._keyDownAlt = true;
                break;
            }
        },
            
        _keyup: function(e) {
            switch (e.keyCode) {
            case 16:
                this._keyDownShift = false;
                break;
            case 17:
                this._keyDownCtrl = false;
                break;
            case 18:
                this._keyDownAlt = false;
                break;
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
            case 32:
                if (this._hasNewClass() && this._getNewClass().hasClass("selected")) {
                    this._addClass();
                }
                this._classifySuperpixelsFromKeyCode();
                break;
            case 27:
                this._clearClass();
                break;
            case 13:
                if (this._hasNewClass()) {
                    this._addClass();
                }
                this._classifySuperpixelsFromKeyCode();
                break;
            case 8:
                if (this._classFilter.length > 0) {
                    this._classFilter = this._classFilter.substring(0, this._classFilter.length - 1);
                }
                break;
            default:
                if (e.keyCode >= 48 && e.keyCode <= 90) {
                    this._classFilter = this._classFilter + String.fromCharCode(e.keyCode).toLowerCase();
                    this._getNewClass().text(this._classFilter);
                    
                    var obj = $(this._objClassSelector).find("li[name^='" + this._classFilter + "']");
                    switch (obj.length) {
                    case 0:
                        this._selectClass(null);
                        break;
                    case 1:
                        this._selectClass($(obj).attr("name"));
                        break;
                    }
                }
                break;
            }
        },

        _classifySuperpixelsFromKeyCode: function() {
            if (this._keyDownShift) {
                this._classifySuperpixelsNonclassified(this._lastClass);
            } else if (this._keyDownCtrl) {
                this._classifySuperpixelsLeft(this._lastClass);
            } else if (this._keyDownAlt) {
                this._classifySuperpixelsRight(this._lastClass);
            } else {
                this._classifyCurrentSuperpixel(this._lastClass);
            }
        },
	
	/*****************************************************************************
	 ** PUBLIC FUNCTIONS                                                        **
	 *****************************************************************************/

	updateQueue: function() {
	    this._updateQueue();
	},
	
	/*****************************************************************************
	 ** GUI CONSTRUCTORS                                                        **
	 *****************************************************************************/

	_getImageDisplay: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>").addClass("argus-image-classifier-display");

            var objCanvas = document.createElementNS("http://www.w3.org/2000/svg", "svg")

            objCanvas.width = objCanvas.clientWidth;
            objCanvas.height = objCanvas.clientHeight;

	    var objOriginal = $("<div>")
                .addClass("display-image")
                .addClass("display-image-original")
                .append($("<div>").append($(objCanvas).clone()))
		.appendTo(obj);

            var objClassified = $("<div>")
                .addClass("display-image")
                .addClass("display-image-classified")
                .append($("<div>").append($(objCanvas).clone()))
		.appendTo(obj);
            
            var objPredicted = $("<div>")
                .addClass("display-image")
                .addClass("display-image-predicted")
                .append($("<div>").append($(objCanvas).clone()))
		.appendTo(obj);

            this._getImageOverlay();

	    return obj;
	},

        _getClassSelector: function() {
            var thisObject = this;

            var obj = $("<div>")
                .addClass("argus-image-classifier-selector")
                .append($("<ul>"));

            return obj;
        },

	_getQueueList: function() {
	    var thisObject = this;

	    var obj = $("<div>")
		.addClass("argus-image-classifier-queue")
		.append($("<div>").append($("<ul>")))

	    this._updateQueue();
		
	    return obj;
	},

        _getToolbar: function() {
            var thisObject = this;

            var obj = $("<div>")
                .addClass("argus-image-classifier-toolbar")

            var objSpacer = $("<div>").addClass("spacer");

            $("<label>")
                .text("dataset:")
                .appendTo(obj);

            $("<div>")
                .text("[select dataset]")
                .addClass("dataset-select")
                .bind("click", function() { thisObject._selectDataset(); })
                .button()
                .appendTo(obj);

            $(objSpacer).clone().appendTo(obj);

	    $("<div>")
                .button({text:false, icons: { primary: "ui-icon-seek-prev" }})
		.bind("click", function() { thisObject._selectNextImage(-1); })
		.tooltip({ content: 'Previous image' })
		.appendTo(obj);

            $("<div>")
                .text("[select image]")
                .addClass("image-select")
                .bind("click", function() { thisObject._selectImage(); })
                .button()
                .appendTo(obj);

	    $("<div>")
                .button({text:false, icons: { primary: "ui-icon-seek-next" }})
		.bind("click", function() { thisObject._selectNextImage(1); })
		.tooltip({ content: 'Next image' })
		.appendTo(obj);

            $(objSpacer).clone().appendTo(obj);

	    $("<label id=\"counter\">")
		.text("0/0")
		.appendTo(obj);
	    
            $(objSpacer).clone().appendTo(obj);

	    $("<div>")
                .button({text:false, icons: { primary: "ui-icon-refresh" }})
		.bind("click", function() { thisObject._refreshImage(); })
		.tooltip({ content: 'Reload current image' })
		.appendTo(obj);

	    $("<div>")
                .button({text:false, icons: { primary: "ui-icon-play" }})
		.bind("click", function() { thisObject._trainModel(); })
		.tooltip({ content: 'Fit model to data' })
		.appendTo(obj);

	    $("<div>")
                .button({text:false, icons: { primary: "ui-icon-copy" }})
		.bind("click", function() { thisObject._copyPrediction(); })
		.tooltip({ content: 'Use model prediction as classification' })
		.appendTo(obj);

	    $("<div>")
                .button({text:false, icons: { primary: "ui-icon-disk" }})
		.bind("click", function() { thisObject._saveClasses(); })
		.tooltip({ content: 'Save classification to server' })
		.appendTo(obj);

            $(objSpacer).clone().appendTo(obj);

            $("<label>")
                .text("compactness:")
                .appendTo(obj);

            $("<input>")
                .attr("name","compactness")
                .attr("value","20")
                .appendTo(obj)
                .spinner();

            $(objSpacer).clone().appendTo(obj);

            $("<label>")
                .text("segments:")
                .appendTo(obj);

            $("<input>")
                .attr("name","n_segments")
                .attr("value","600")
                .appendTo(obj)
                .spinner();

            $(objSpacer).clone().appendTo(obj);

	    $("<div>")
                .button({text:false, icons: { primary: "ui-icon-scissors" }})
		.bind("click", function() { thisObject._forceSegmentation(); })
		.tooltip({ content: 'Recalculate image segments' })
		.appendTo(obj);

            $(objSpacer).clone().appendTo(obj);

	    $("<div>")
                .button({text:false, icons: { primary: "ui-icon-help" }})
		.bind("click", function() { })
		.tooltip({ content: 'Usage instructions' })
		.appendTo(obj);

            return obj;
        },

        _getImageOverlay: function(force) {
            force = (typeof force === "undefined") ? false : force;
            
            var thisObject = this;

            if (this.options.dataset != null && this.options.image != null) {

                var qs = "?keys=url,contours,width,height,nx,ny,assignments,prediction,classes,centroids";
                var qs = qs + "&compactness=" + $(this._objToolbar).find("input[name='compactness']").val();
                var qs = qs + "&n_segments=" + $(this._objToolbar).find("input[name='n_segments']").val();
                var qs = qs + "&force_segmentation=" + force;
                var qs = qs + "&callback=?";

                var json_url = this.options.datasetHost + this.options.dataset + "/" + this.options.image + qs;

                $.getJSON(json_url, function(data) {
                    thisObject._contours = data["contours"];
                    thisObject._centroids = data["centroids"];
                    thisObject._width    = data["width"];
                    thisObject._height   = data["height"];
                    thisObject._nx       = data["nx"];
                    thisObject._ny       = data["ny"];
		    thisObject._classes    = data["classes"];
		    thisObject._prediction = data["prediction"];
                    
		    if (data["assignments"].length == 0) {
			thisObject._assignments = Array
			    .apply(null, new Array(thisObject._contours.length))
			    .map(function() { return null; });
		    } else {
			thisObject._assignments = data["assignments"];
		    }
                    thisObject._fillClassSelector();
                    
                    var obj = $(thisObject._objImageDisplay).find("div.display-image-original svg")[0];
                    $(obj).css("background-image","url('" + thisObject.options.imageHost + encodeURIComponent(data["url"]) + "')");
                    thisObject._drawSuperpixelRaster(obj);
                    
                    var obj = $(thisObject._objImageDisplay).find("div.display-image-classified svg")[0];
                    thisObject._drawSuperpixelRaster(obj);
                    thisObject._fillSuperpixelRaster(obj, thisObject._assignments);

                    var obj = $(thisObject._objImageDisplay).find("div.display-image-predicted svg")[0];
                    thisObject._drawSuperpixelRaster(obj);
                    thisObject._fillSuperpixelRaster(obj, thisObject._prediction);

		    if (thisObject._prediction.length == 0) {
			thisObject._hidePrediction();
		    } else {
			thisObject._showPrediction();
		    }

                    thisObject._highlightSuperpixel(0);
                    thisObject._hideOverlay();
                });
            }
        },
	
	/*****************************************************************************
	 ** ACTION HANDLERS                                                         **
	 *****************************************************************************/

	_selectDataset: function() {
            var thisObject = this;
            
            var obj = this._showDialog("Select dataset", "", function() {
                thisObject._setDataset($(".ui-dialog select[name='dataset']").val()) });

            json_url = this.options.datasetHost;
            $.getJSON(json_url, function(data) {
                var objSelect = $("<select name=\"dataset\">").appendTo(obj);
                for (var i=0;i<data.length;i++) {
                    $("<option>")
                        .val(data[i])
                        .text(data[i])
                        .appendTo(objSelect);
                }
            });
        },
        
        _setDataset: function(dataset) {
            this.options.image = null;
            this.options.dataset = dataset;
            $(this._objToolbar)
                .find(".dataset-select")
                .button("option","label",this.options.dataset);
        },

	_selectImage: function() {
            var thisObject = this;

            var obj = this._showDialog("Select image", "", function() {
                thisObject._setImage(
		    $(".ui-dialog .ui-selectable li.ui-selected img")
			.attr("file")); });

	    $(obj)
		.dialog("option","width",600)
		.dialog("option","height",400);

            json_url = this.options.datasetHost + this.options.dataset + "/";
            $.getJSON(json_url, function(data) {
                var objSelect = $("<ol>")
		    .selectable()
		    .appendTo(obj);

                for (var i=0;i<data.length;i++) {
		    if (data[i]["isclassified"]) {
//                        continue; // FIXME
                    }

		    var objImg = $("<img>")
			.attr("file",data[i]["file"])
			.attr("title",data[i]["file"])
                        .attr("src", 
			      thisObject.options.imageHost + "/" + 
			      thisObject.options.dataset + "/" + data[i]["file"])
			.bind("dblclick", function() {
			    thisObject._setImage($(this).attr("file"));
			    $(obj).dialog("close"); })
		    
		    if (data[i]["isclassified"]) {
			$(objImg).addClass("isclassified");
		    }

		    $("<li>")
			.append(objImg)
                        .appendTo(objSelect);
                }
            });
        },

        _selectNextImage: function(n) {
            var thisObject = this;

            var json_url = this.options.datasetHost + this.options.dataset + "/";
            $.getJSON(json_url, function(data) {
                var files = data
                    .map(function(obj){return $(obj).attr("file");})
                var idx = files.indexOf(thisObject.options.image) + n;
                if (idx >= 0 && idx < files.length) {
                    thisObject._setImage(files[idx]);
                }
            });
        },

	_refreshImage: function() {
	    this._setImage(this.options.image);
	},

        _setImage: function(name) {
            var thisObject = this;

            if (this._isChanged) {
                this._showDialog("Classification changed",
                                 "You have unsaved changes in this classification. Do you want to load a new image without saving?",
                                 function() {
                                     thisObject._isChanged = false;
                                     thisObject._setImage(name) });
            } else {
                this.options.image = name;
                $(this._objToolbar)
                    .find(".image-select")
                    .button("option","label",this.options.image);
                
                this._showOverlay("image is being loaded...");
                this._getImageOverlay();
            }
        },

	_updateQueue: function() {
	    var thisObject = this;

            var json_url = this.options.jsonHost + "queue/";
            $.getJSON(json_url, function(data) {
		objs = $(thisObject._objQueueList).find("li");
		for (var i = 0; i < objs.length; i++) {
		    var is_present = false;
		    $.each(data, function(key, item) {
			if ($(objs[i]).attr("id") == "queue_" + key) {
			    is_present = true;
			}
		    });
		    if (!is_present) {
			$(objs[i])
			    .css("z-index",-1)
			    .animate({
				marginTop: "+34px",
				opacity: 0,
			    }, {
				duration:500,
				queue:true,
				complete:function() { $(this).remove(); }});
		    }
		}

		$.each(data, function(key, item) {
		    var id = "queue_" + key;

		    if (thisObject._objQueueList.find("li#" + id).length == 0) {
			var obj = $("<li>")
			    .text(item["msg"])
			    .attr("id",id)
			    .append($("<div>")
				    .text("[" + key + "]")
				    .addClass("queue_id"))
			    .appendTo($(thisObject._objQueueList).find("ul"));

			$(obj).animate({
			    marginLeft: "-4px",
			}, {
			    duration:500, 
			    queue:true });
		    }
		});
            });
	},

	_copyPrediction: function() {
	    this._assignments = this._prediction;
	    var obj = $(this._objImageDisplay).find("div.display-image-classified svg")[0];
            this._fillSuperpixelRaster(obj, this._assignments);
	},

	_forceSegmentation: function() {
            this._showOverlay("Re-segmentating image...");
	    this._getImageOverlay(true);
	},
 
	_trainModel: function() {
	    var thisObject = this;

            var json_url = this.options.jsonHost + "train/" + this.options.dataset + "/";
            $.getJSON(json_url, function(data) {
		// pass
            });
	},

        _fillClassSelector: function() {
            $(this._objClassSelector).find("ul").html("");
            for (var i = 0; i < this._classes.length; i++) {
                this._addClass(this._classes[i]);
            }
        },

	_updateClassificationCounter: function() {
	    var obj = $(this._objToolbar).find("#counter");

	    var i = -1;
	    var n = -1;
	    while (i >= 0 || n < 0) {
		i = this._assignments.indexOf(null, i+1);
		n = n + 1;
	    }

	    $(obj)
		.text(n + "/" + this._assignments.length);
	},

        _classifySuperpixel: function(idx, name) {
            this._assignments[idx] = name;
            
            this._selectClass(name);
            this._clearClass();
            
            var obj = $(this._objImageDisplay).find("div.display-image-classified svg")[0];

            d3
                .select(".argus-image-classifier .display-image-classified svg")
                .select("#superpixel_" + idx)
                .classed("classified",true)
                .style("stroke",this._getClassColor(name))
                .style("fill",this._getClassColor(name));

            var obj = $(this._objImageDisplay).find("div.display-image-original svg")[0];
            this._highlightAdjacentSuperpixel("right");

            this._isChanged = true;
        },

        _classifyCurrentSuperpixel: function(name) {
            var idx = this._currentSuperpixel;
            
            if (idx != null) {
                this._classifySuperpixel(idx, name);
            }

	    this._updateClassificationCounter();
        },
            
        _classifySuperpixelsNonclassified: function(name) {
            for (idx = 0; idx < this._contours.length; idx++) {
                if (this._assignments[idx] == null) {
                    this._classifySuperpixel(idx, name);
                }
            }

	    this._updateClassificationCounter();
        },

        _classifySuperpixelsLeft: function(name) {
            var idxCurrent = this._currentSuperpixel;
            for (idx = 0; idx <= idxCurrent; idx++) {
                this._classifySuperpixel(idx, name);
            }

	    this._updateClassificationCounter();
        },

        _classifySuperpixelsRight: function(name) {
            var idxCurrent = this._currentSuperpixel;
            for (idx = idxCurrent; idx < this._contours.length; idx++) {
                this._classifySuperpixel(idx, name);
            }

	    this._updateClassificationCounter();
        },
        
        _drawSuperpixelRaster: function(obj) {
            var thisObject = this;

            d3.select(obj)
                .attr("preserveAspectRatio","none")
                .attr("viewBox","0,0," + this._width + "," + this._height);

            d3.select(obj)
                .selectAll(".superpixel")
                .remove();
            
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
                .attr("d", function(d) {
                    return thisObject._getSVGPath(d,
                                                  $(obj).width()/thisObject._width,
                                                  $(obj).height()/thisObject._height); })
                .on("click", function() {
                    thisObject._highlightSuperpixel(
                        parseInt(d3.select(this).attr("nr"))); })
                .on("mouseover", function() {
                    thisObject._hoverSuperpixel(
                        parseInt(d3.select(this).attr("nr"))); });

	    this._updateClassificationCounter();
        },

        _fillSuperpixelRaster: function(obj, values) {
            var thisObject = this;

	    if (values.length > 0) {
		d3.select(obj).selectAll(".superpixel")
                    .classed("classified", function(d,i) {
			return values[i] != null; })
                    .style("stroke", function(d,i) {
			return thisObject._getClassColor(values[i]); })
                    .style("fill", function(d,i) {
			return thisObject._getClassColor(values[i]); });
	    }
        },

        _hoverSuperpixel: function(idx) {
            if (this._contours != null) {
                if (idx >= this._contours.length) idx = idx - this._contours.length;
                if (idx < 0) idx = idx + this._contours.length;
                
                d3
                    .selectAll(".argus-image-classifier-display svg")
                    .selectAll(".superpixel")
                    .classed("hover",false);
                d3
                    .selectAll(".argus-image-classifier-display svg")
                    .select("#superpixel_" + idx)
                    .classed("hover",true);
            }
        },

        _highlightSuperpixel: function(idx) {
            if (this._contours != null) {
                if (idx >= this._contours.length) idx = idx - this._contours.length;
                if (idx < 0) idx = idx + this._contours.length;
                this._currentSuperpixel = idx;
                
                d3
                    .selectAll(".argus-image-classifier-display svg")
                    .selectAll(".superpixel")
                    .classed("selected",false);
                d3
                    .selectAll(".argus-image-classifier-display svg")
                    .select("#superpixel_" + idx)
                    .classed("selected",true);

		current_class = this._assignments[this._currentSuperpixel];
		if (current_class == null) {
		    $(this._objClassSelector).find("li").removeClass("current");
		} else {
		    $(this._objClassSelector).find("li[name!='" + current_class + "']")
			.removeClass("current");
		    $(this._objClassSelector).find("li[name='" + current_class + "']")
			.addClass("current");
		}
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

        _selectClass: function(name) {
            this._lastClass = name;
            $(this._objClassSelector).find("li").removeClass("selected");
            if (name == null) {
                this._getNewClass().addClass("selected");
            } else {
                $(this._objClassSelector).find("li[name='" + name + "']").addClass("selected");
            }
        },

        _addClass: function(name) {
            name = (typeof name === "undefined") ? this._classFilter : name;

            this._lastClass = name;

            var thisObject = this;
            var obj = this._getNewClass(name);

            $(obj)
                .removeClass("new")
                .css("background-color",this._getRandomColor(name))
                .attr("name",$(obj).text())
                .bind("click", function() {
                    thisObject._classifyCurrentSuperpixel($(this).text()) });

            this._clearClass();
        },

        _newClass: function(name) {
            name = (typeof name === "undefined") ? this._classFilter : name;

            var obj = $("<li>")
                .addClass("new")
                .css("background-color","#ffffff")
                .text(name);

            $(this._objClassSelector).find("ul").append(obj);

            return obj;
        },

        _clearClass: function() {
            this._classFilter = "";
            $(this._objClassSelector).find("li.new").remove();
        },

        _saveClasses: function() {
            var thisObject = this;

            var url = this.options.datasetHost + this.options.dataset + "/" + this.options.image + "/";
            var data = JSON.stringify({"assignments" : this._assignments});

            this._showOverlay("Saving classification...");

            $.post(url, data, function(d) {
                thisObject._hideOverlay();
                if (d==0) {
                    thisObject._isChanged = false;
                } else {
                    thisObject._showMessage("Save failed","Saving classification failed");
                }});
        },

        _checkIfSaved: function() {
            if (this._isChanged) {
                return "You have unsaved changes in this classification. " + 
                    "Are you sure you want to navigate away from this page without saving?";
            }
        },

	_hidePrediction: function() {
            $(this._objImageDisplay).find("div.display-image-predicted").hide();
	    this._nrOfPictures = 2;
	    this._resize();
	},

	_showPrediction: function() {
            $(this._objImageDisplay).find("div.display-image-predicted").show();
	    this._nrOfPictures = 3;
	    this._resize();
	},

        _showDialog: function(title,text,fcn_ok,fcn_cancel) {
            fcn_ok = (typeof fcn_ok === "undefined") ? function() {} : fcn_ok;
            fcn_cancel = (typeof fcn_cancel === "undefined") ? function() {} : fcn_cancel;

            var obj = $("<div>")
                .append($("<p>").text(text))
                .dialog({
                    title: title,
                    height: 140,
                    modal: true,
                    buttons: {
                        "Cancel": function() { fcn_cancel(); $(this).dialog("close"); },
                        "OK": function() { fcn_ok(); $(this).dialog("close"); }},
                    close: function() { $(this).dialog("destroy"); },
                    open: function() { $(this).parent().find(".ui-dialog-buttonpane button:eq(1)").focus(); }});

            return obj;
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

	/*****************************************************************************
	 ** HELPER FUNCTIONS                                                        **
	 *****************************************************************************/

        _getNewClass: function(name) {
            var obj = $(this._objClassSelector).find("li.new");
            if (obj.length == 0) {
                return this._newClass(name);
            } else {
                return obj;
            }
        },

        _hasNewClass: function() {
            return $(this._objClassSelector).find("li.new").length > 0;
        },
    
        _clearCanvas: function(obj) {
            var context = obj.getContext("2d");
            context.clearRect(0,0,obj.width,obj.height);
        },

	_drawSuperpixel: function(obj, idx, fill, stroke) {

            if (this._contours != null && idx >= 0 && idx < this._contours.length) {

/*                var ws = this._width / obj.width;
                var hs = this._height / obj.height;
                
                var context = obj.getContext('2d');
                var contour = this._contours[idx];
                
                context.beginPath();
                context.lineWidth = 1;
                context.fillStyle = fill;
                context.strokeStyle = stroke;
                
                for (var i = 0; i < contour.length; i++) {
                    
                    context.moveTo(contour[i][0][0][0]/ws,
                                   contour[i][0][0][1]/hs);
                    for (var j = 1; j < contour[i].length; j++) {
                        context.lineTo(contour[i][j][0][0]/ws,
                                       contour[i][j][0][1]/hs);
                    }
                }
                
                if (fill != null) context.fill();
                if (stroke != null) context.stroke();
                
                context.closePath();*/


            }
        },

        _getClassColor: function(name) {
	    if (typeof(name) === "string") {
		obj = $(this._objClassSelector).find("li[name='" + name + "']")[0];
	    } else {
		obj = $(this._objClassSelector).find("li:eq(" + name + ")")[0];
	    }
            return $(obj).css("background-color");
        },

        _getRandomColor: function(name) {
            switch (name) {
                case "objectdune":
                return "#eeeeee";
                break;
                case "objectsea":
                return "#cccccc";
                break;
                case "objectbeach":
                return "#aaaaaa";
                break;
                case "water":
                case "watersea":
                return "#0000ff";
                break;
                case "waterpool":
                return "#000099";
                break;
                case "air":
                case "sky":
                return "#6666ff";
                break;
                case "sandbeach":
                return "#ffff00";
                break;
                case "sanddune":
                case "sandune":
                return "#ff9900";
                break;
                case "vegetation":
                return "#00ff00";
                break;
                case "wave":
                return "#ff6666";
                break;
                }
/*
            color = "#";
            for (var i = 0; i < 3; i++) {
                color = color + Math.round(100 + Math.random() * 155).toString(16);
            }
            return color;*/
        },

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
