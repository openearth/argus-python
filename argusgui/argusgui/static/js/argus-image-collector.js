(function( $, undefined ) {
    
    var thisObject = this;
    
    $.widget( "ui.argusImageCollector", {
	version: "0.0.1",
	options: {
	    jsonHost: "http://argus-public.deltares.nl/db/"
	},
	
	_objMenuBar:        null,
	_objImageCollector: null,
	_objDialogBar:      null,
	_objPreviewDialog:  null,
	_objLoadFrame:      null,
	
	_create: function() {
	    var thisObject = this;
	    
	    objClr = '<div style="clear:both;">';
	    
	    $(window).bind("load", function() { thisObject._resize(); })
		.bind("resize", function() { thisObject._resize(); });
	    
	    $(this.element).addClass("argus-image-collector");
	    
	    this._objMenuBar        = this._getMenuBar();
	    this._objImageCollector = this._getImageCollector();
	    this._objDialogBar      = this._getDialogBar();
	    this._objPreviewDialog  = this._getPreviewDialog();
	    this._objLoadFrame      = this._getLoadFrame();
	    
	    $(this.element).append(this._objMenuBar).append(objClr)
                .append(this._objDialogBar).append(objClr)
                .append(this._objImageCollector)
                .append(this._objPreviewDialog)
		.append(this._objLoadFrame);
            
	    this._loadImageCollection();
	    this._resize();
	},
	
	_resize: function() {
	    var w = $(this.element).width();
	    var h = $(this.element).height();

	    var objHeight = parseInt(h-28)
	    var objWidth  = Math.min(800,parseInt(w-365))
	    
	    $(this._objImageCollector).css("height", objHeight);
	    $(this._objPreviewDialog).css("height", objHeight).css("width", objWidth);
	    $(".preview-info").css("height", parseInt(h-objWidth*3/4-160));
	},
	
	/*****************************************************************************
	 ** PUBLIC FUNCTIONS                                                        **
	 *****************************************************************************/
	
	addImages: function(imgs) {
	    var thisObject = this;
	    
	    for (var i=0;i<imgs.length;i++) {
		if (imgs[i].length>0) {
		    if (this._findImageIndex(imgs[i]) == null) {
			var objImage = $("<img>").attr("src",this._getThumbnail(imgs[i]))
                            .attr("title",this._urlToFile(imgs[i]))
                            .attr("url",imgs[i])
                            .bind("click", function() { 
                                thisObject.setImage($(this).attr("url"));
                            })
                            .tooltip({
                                open: function(e,ui) {
                                    thisObject._loadDynamicData(ui["tooltip"],$(this).attr("url"));
                                }
                            });
			
			var objItem = $("<div>").addClass("argus-image-collector-item").append(objImage);
			
			$(this._objImageCollector).children("div.ui-selectable").append(objItem);
		    }
		}
	    }
	},
	
	getImages: function() {
	    var objImages = $(this._objImageCollector).find("img");
	    
	    var urls = new Array();
	    for (var i=0;i<objImages.length;i++) {
		urls[i] = $(objImages[i]).attr("url");
	    }
	    
	    return urls;
	},

	getImage: function() {
	    return this._objPreviewDialog.children(".preview-image").attr("src");
	},
	
	setImage: function(url) {
	    this._objPreviewDialog.children(".preview-image").attr("src",url);
	    this._loadDynamicData(this._objPreviewDialog.children(".preview-info"), url);
	},
		
	/*****************************************************************************
	 ** GUI CONSTRUCTORS                                                        **
	 *****************************************************************************/
	
	_getMenuBar: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>").addClass("argus-image-collector-menubar");
	    
	    $('<div>').button({text:false, icons: { primary: "ui-icon-trash" }})
		.bind('click', function() { thisObject._deleteSelectedImages(); })
		.tooltip({ content: 'Remove items from collection' })
		.appendTo(obj);

	    $('<div>').button({text:false, icons: { primary: "ui-icon-disk" }})
		.bind('click', function() { thisObject._saveImageCollection(); })
		.tooltip({ content: 'Save image collection' })
		.appendTo(obj);
	    
	    $('<div>').button({text:false, icons: { primary: "ui-icon-document" }})
		.bind('click', function() { thisObject._downloadImageCollectionAsText(); })
		.tooltip({ content: 'Download image collection as text file' })
		.appendTo(obj);
	    
	    $('<div>').button({text:false, icons: { primary: "ui-icon-carat-2-n-s" }})
		.bind('click', function() { thisObject._sortImageCollection(); })
		.tooltip({ content: 'Sort image collection by filename' })
		.appendTo(obj);
	    
	    $('<div>').button({text:false, icons: { primary: "ui-icon-help" }})
		.bind('click', function() { thisObject._showHelp(); })
		.tooltip({ content: 'About the Python Argus GUI' })
		.appendTo(obj);
            
	    return obj;
	},
	
	_getDialogBar: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>").addClass("argus-image-collector-dialogbar")
                .hide();
            
	    $("<div>").addClass("ui-state-error argus-image-collector-dialogbar-confirm")
		.button({text:false, icons: { primary: "ui-icon-check" }})
		.appendTo(obj);
	    
	    $("<div>").addClass("ui-state-error")
		.button({text:false, icons: { primary: "ui-icon-close" }})
		.bind("click", function() { thisObject._hideDialogBar(); })
		.appendTo(obj);
            
	    $("<div>").addClass("ui-state-error ui-corner-all argus-image-collector-dialogbar-message")
		.append($("<span>").addClass("ui-icon ui-icon-alert"))
		.append($("<span>").addClass("dialog-message"))
		.appendTo(obj);
	    
	    return obj;
	},
	
	_getImageCollector: function() {
	    var obj = $("<div>").addClass("argus-image-collector-collection");
	    
	    obj.append($("<div>").sortable({
                items: ".argus-image-collector-item",
                placeholder: "argus-image-collector-item-highlight"})
                       .selectable({
                           filter:".argus-image-collector-item"}));
            
	    return obj;
	},
	
	_getPreviewDialog: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>").addClass("argus-image-collector-preview")
	    
	    var objImage = $("<img>").addClass("preview-image");
	    var objInfo  = $("<div>").addClass("preview-info");
	    var objMoveL = $("<div>").addClass("preview-move-left").text("<<").button();
	    var objMoveR = $("<div>").addClass("preview-move-right").text(">>").button();
	    
	    objMoveL.bind("click", function() { thisObject._movePreview(-1); });
	    objMoveR.bind("click", function() { thisObject._movePreview(+1); });
	    
	    obj.append(objImage)
		.append(objInfo)
		.append(objMoveL)
		.append(objMoveR);
	    
	    return obj;
	},

	_getLoadFrame: function() {
	    var thisObject = this;
	    var obj = $("<iframe>").css("display","none");
	    return obj;
	},
	
	/*****************************************************************************
	 ** ACTION HANDLERS                                                         **
	 *****************************************************************************/
	
	_movePreview: function(d) {
	    var current_url = this._objPreviewDialog.children(".preview-image").attr("src");
	    var image_index = this._findImageIndex(current_url) + d;
	    var next_url    = this._getImageByIndex(image_index);
	    this.setImage(next_url);
	},
	
	_deleteSelectedImages: function() {
	    var thisObject = this;
	    
	    var objSelected = $(this._objImageCollector).find(".argus-image-collector-item.ui-selected");
	    
	    if (objSelected.length==0) {
		this._showDialogBar("Delete <b>all</b> images from collection?", function() {
		    $(thisObject._objImageCollector).find(".argus-image-collector-item").remove();
		});
	    } else {
		objSelected.remove();
	    }
	},
	
	_saveImageCollection: function() {
	    var urls = this.getImages();
	    if (urls.join(",").length >= 4000) {
		this._showDialogBar("Image collection is too large for a cookie (>4kB)", function() {});
	    } else {
		$.cookie("argusimagecollection", urls);
	    }
	},
	
	_loadImageCollection: function() {
	    var urls = $.cookie("argusimagecollection");
	    
	    if (urls != undefined && urls.length>0) {
		urls = urls.split(",");
		this.addImages(urls);
		this.setImage(urls[0]);
	    } else {
		this.setImage("static/blank.jpg");
	    }
	},
	
	_downloadImageCollectionAsText: function() {
	    var urls = this.getImages();
	    var output = "";
	    for (var i = 0; i < urls.length; i++) {
		output = output + urls[i] + "\n";
	    }
	    
	    this._objLoadFrame.attr("src", "data:application/octet-stream;charset=utf-8," + escape(output));
	},

	_sortImageCollection: function() {
    	    var objImages = $(this._objImageCollector)
		.children("div.ui-selectable")
		.children("div.argus-image-collector-item");

	    objImages.sort(function (a, b) {
		if ($(a).children("img").attr("title") > $(b).children("img").attr("title")) {
		    return 1;
		} else if ($(a).children("img").attr("title") < $(b).children("img").attr("title")) {
		    return -1;
		} else {
		    return 0;
		}
	    });

	    $(this._objImageCollector).children("div.ui-selectable").append(objImages);
	},

	_showHelp: function() {
	    var txt = "<p>This is an alternative interface for the Argus image collection. It is based on the Argus REST API and image index, which are both under development as is this interface itself. Suggestions and feature requests can be e-mailed to <a href=\"mailto:bas.hoonhout@deltares.nl\">bas.hoonhout@deltares.nl</a>.</p><p>The interface currently supports the following features:<br><ul><li>Selection of a single (open-source) site</li><li>Selection of multiple cameras at the selected site (not necessarily a range)</li><li>Selection of one or more image types (snap, timex, var, etc.)</li><li>Selection of a day or a range of days</li><li>Selection of one or more image sets (an image set is a synchronized set of images from all cameras in a station). When the 12:00 hours image set is chosen and a date range is selected, it will return the 12:00 synchronized images of all selected days and all selected cameras.</li><li>Construction of an image collection by making multiple queries</li><li>Sorting of the image collection</li><li>Downloading image collection as text file that can be used with, for example, wget to download all selected files at once</li><li>Automatic retrieval of meta-data, like sun position, solar radiation, rainfall, wind speed and direction, etc.</li></ul></p><p>It is intended that the interface will support on-the-fly modifications to the images as well, like segmentation and classification.</p>";

	    $("<div>").html(txt).dialog({
		width: 600,
		height: 350,
		modal: true,
		title: "Argus Image Collection Interface",
		close: function() { $(this).dialog("destroy"); },
	    });
	},
	
	_showDialogBar: function(txt, fcn) {
	    var thisObject = this;
	    
	    this._objDialogBar.find(".dialog-message").html(txt);
	    this._objDialogBar.find(".argus-image-collector-dialogbar-confirm").bind("click",function() {
		fcn();
		thisObject._hideDialogBar();
	    });
	    this._objDialogBar.show();
	    this._objMenuBar.hide();
	},
	
	_hideDialogBar: function() {
	    this._objMenuBar.show();
	    this._objDialogBar.hide();
	},
	
	/*****************************************************************************
	 ** HELPER FUNCTIONS                                                        **
	 *****************************************************************************/
	
	_getImageByIndex: function(i) {
	    var objImages = $(this._objImageCollector).find("img");
	    return $(objImages[i]).attr("url");
	},
	
	_findImageIndex: function(url) {
	    var objImages = $(this._objImageCollector).find("img");
	    for (var i=0;i<objImages.length;i++) {
		if ($(objImages[i]).attr("url") == url) {
		    return i;
		}
	    }
	    
	    return null;
	},
	
	_getThumbnail: function(url) {
	    return url.replace(/(\d{10})/g,"tn/$1")
	},
	
	_loadDynamicData: function(ui,url) {
	    var thisObject = this;
	    var obj = ui;
	    
	    $(obj).append($("<div>").css("text-align","center")
                          .css("margin","10px")
                          .append($("<img>").attr("src","static/jquery-ui-1.10.2/images/ui-anim_basic_16x16.gif")));
    
	    if (url.length>0) {
		var jsonHost = this.options.jsonHost;
		var json_url = jsonHost + "image?url=" + url + "&callback=?";
		$.getJSON(json_url, function(data) {

		    var sunposition = Math.round(data["field"]["sun"]["alt"]/Math.PI*1800)/10 + "&#176; " + 
                        Math.round(data["field"]["sun"]["az"]/Math.PI*1800)/10 + "&#176;";
		    
		    info_table = $("<div>");
		    info_table.append(thisObject._getDynamicDataItem("site",            data["site"]["name"]));
		    info_table.append(thisObject._getDynamicDataItem("station",         data["station"]["name"]));
		    info_table.append(thisObject._getDynamicDataItem("camera",          "#"+data["camera"]["cameraNumber"]));
		    info_table.append(thisObject._getDynamicDataItem("date &amp; time", data["datetime"]["datetime"]+" "+data["datetime"]["timezone"]));
		    info_table.append(thisObject._getDynamicDataItem("type",            data["file"]["imgtype"]));
		    //        info_table.append(thisObject._getDynamicDataItem());
		    
		    info_table.append(thisObject._getDynamicDataItem("sun elevation",   Math.round(data["field"]["sun"]["alt"]/Math.PI*1800)/10, "&#176;"));
		    info_table.append(thisObject._getDynamicDataItem("sun azimuth",     Math.round(data["field"]["sun"]["az"]/Math.PI*1800)/10, "&#176;"));
		    info_table.append(thisObject._getDynamicDataItem("solar radiation", data["field"]["meteo"]["global_radiation"], "J/cm<sup>2</sup>"));
		    info_table.append(thisObject._getDynamicDataItem("rainfall",        data["field"]["meteo"]["precipitation_amount_sum"], "mm/hr"));
		    info_table.append(thisObject._getDynamicDataItem("air temperature", data["field"]["meteo"]["air_temperature_mean"], "&#176;C"));
		    info_table.append(thisObject._getDynamicDataItem("wind speed",      data["field"]["meteo"]["wind_speed_vector_mean"], "m/s"));
		    info_table.append(thisObject._getDynamicDataItem("wind gusts",      data["field"]["meteo"]["wind_speed_minimum_gust_hour"], "m/s"));
		    info_table.append(thisObject._getDynamicDataItem("wind direction",  data["field"]["meteo"]["wind_from_direction_mean"], "&#176;"));
		    
		    $(obj).html(info_table);
		});
	    }
	},
	
	_getDynamicDataItem: function(label, data, units) {
	    
	    objLabel = $("<span>").addClass("dynamic-data-label");
	    objValue = $("<span>").addClass("dynamic-data-value");
	    
	    if (label != undefined && data != undefined) {
		objLabel.html(label+":");
		
		if (data == undefined) {
		    var txt = "?";
		} else {
		    var txt = data;
		}
		if (units == undefined) {
		    $(objValue).html(txt);
		} else {
		    $(objValue).html(txt + " " + units);
		}
	    }
	    
	    obj = $("<div>").addClass("dynamic-data")
                .append(objLabel)
                .append(objValue);
            
	    return obj;
	},
	
	_urlToFile: function(url) {
	    var m = /\d{10}\.(.+)\.(jpg|png)/.exec(url);
	    if (m == null) {
		return url;
	    } else {
		return m[0];
	    }
	},
	
    });
    
})( jQuery );
