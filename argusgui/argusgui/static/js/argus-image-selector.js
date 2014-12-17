(function( $, undefined ) {

    var img_types = new Array();
    img_types[0] = "snap";
    img_types[1] = "timex";
    img_types[2] = "var";
    img_types[3] = "min";
    img_types[4] = "max";
    /*img_types[5] = "merge";
      img_types[6] = "ir";*/

    var thisObject = this;
  
    $.widget( "ui.argusImageSelector", {
	version: "0.0.1",
	options: {
	    jsonHost: "http://argus-public.deltares.nl/db/",
	    imgTypes: img_types,
	    showRandomButton: true,
	    showSelectButton: true,
	    selectButtonText: "Add images",
	    randomButtonText: "I'm feeling lucky",
	    onSelect: null,
	    marginSet: 600,
	    maxNrCameras: 8,
	    maxNrTimeOptions: 24 * 2 - 1,
	    noImageSetsMessage: "No image sets found",
	},
	
	_objTypeSelector: null,
	_objSiteSelector: null,
	_objDateSelector: null,
	_objTimeSelector: null,

	_selectedDates: new Array(),
	
	_create: function() {
	    objClr = '<div style="clear:both;">';
	    
	    $(this.element).addClass("argus-image-selector");
	    
	    this._objTypeSelector = this._getTypeSelector();
	    this._objCamSelector  = this._getCamSelector();
	    this._objSiteSelector = this._getSiteSelector();
	    this._objDateSelector = this._getDateSelector();
	    this._objTimeSelector = this._getTimeSelector();
	    
	    if (this.options.showRandomButton) {
		$(this.element).append(this._getRandomButton()).append(objClr);
	    }
	    
	    $(this.element).append(this._objTypeSelector).append(objClr)
                .append(this._objCamSelector).append(objClr)
                .append(this._objSiteSelector).append(objClr)
                .append(this._objDateSelector).append(objClr)
                .append(this._objTimeSelector).append(objClr);
	    
	    if (this.options.showSelectButton) {
		$(this.element).append(this._getSelectButton()).append(objClr);
	    }
	},
	
	/*****************************************************************************
	 ** GUI CONSTRUCTORS                                                        **
	 *****************************************************************************/
	
	_getTypeSelector: function() {
	    var obj = $("<div>").addClass("argus-image-selector-types");
	    
	    var img_types = this.options.imgTypes;
	    for (var i=0;i<img_types.length;i++) {
		objId = "argus-image-selector-type-" + this._randomHash(5);
		
		$("<input>")
		    .attr("type","radio")
                    .attr("id", objId)
                    .attr("value", img_types[i])
                    .attr("name", "imgtypes[]")
                    .appendTo(obj);
		
		$("<label>")
		    .attr("for", objId)
                    .html(img_types[i])
                    .css("width", 100/img_types.length + "%")
                    .appendTo(obj);
	    }
    
	    var selected = $.cookie("argus-image-selector-type");
    
	    if (selected != undefined && selected.length>0) {
		$(obj).children('input[name="imgtypes[]"][value="'+selected+'"]').attr("checked",1);
	    } else {
		$(obj).children('input[name="imgtypes[]"]:first').attr("checked",1);
	    }
	    
	    obj.buttonset()
		.attr("title","Select the type of images that should be returned")
		.tooltip({position:{my:"left",at:"right+10px",of:$(obj)}});
	    
	    return obj;
	},
	
	_getCamSelector: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>").addClass("argus-image-selector-cameras");
	    
	    var n = this.options.maxNrCameras;
	    for (var i=1;i<=n;i++) {
		objId = "argus-image-selector-camera-" + this._randomHash(5);
		
		$("<input>").attr("type","checkbox")
                    .attr("id", objId)
                    .attr("value", i)
                    .attr("name", "cameras[]")
                    .appendTo(obj);
		
		$("<label>").attr("for", objId)
                    .html(i)
                    .css("width", 102/n + "%")
                    .appendTo(obj)
	    }
	    
	    var selected = $.cookie("argus-image-selector-cameras");
	    
	    if (selected != undefined && selected.length>0) {
		selected = selected.split(",");
		for (var i=0;i<selected.length;i++) {
		    $(obj).children('input[name="cameras[]"][value="'+selected[i]+'"]').attr("checked",1);
		}
	    } else {
		$(obj).children('input[name="cameras[]"]:first').attr("checked",1);
	    }
	    
	    obj.buttonset()
		.attr("title","Select the camera numbers that should be included in the selection (double-click to toggle all)")
		.tooltip({position:{my:"left",at:"right+10px",of:$(obj)}})
		.bind("dblclick", function() { thisObject._toggleButtonset(this); });
	    
	    return obj;
	},
	
	_getSiteSelector: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>").addClass("argus-image-selector-sites")
	    
	    var objSelect = $("<select>").bind("change",function() {
                thisObject._selectSite();
            });
	    
	    var json_url = this.options.jsonHost + "table/station?callback=?"
	    
	    $.getJSON(json_url, function(data) {
		selectedSite = $.cookie("argus-image-selector-site");
		for (var i=0;i<data.length;i++) {
		    objOption = $("<option>").val(data[i]["shortName"])
                        .text(data[i]["name"])
                        .attr("startEpoch",data[i]["timeIN"])
                        .attr("endEpoch",data[i]["timeOUT"])
                        .attr("selected",data[i]["shortname"]==selectedSite);
		    objSelect.append(objOption);
		};
		
		thisObject._selectSite();
	    });
	    
	    obj.append(objSelect);
	    
	    return obj;
	},
	
	_getDateSelector: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>").addClass("argus-image-selector-date").datepicker({
		minDate: 0,
		maxDate: 0,
		changeMonth: true,
		changeYear: true,
		onSelect: function(dateText, inst) {
		    thisObject._addOrRemoveDate(dateText);
		    thisObject._selectDate();
		},
		beforeShowDay: function(date) {
		    var dates = new Array();

		    for (var i = 0; i < thisObject._selectedDates.length; i++) {
			dates[i] = $.datepicker.parseDate(
			    $(this).datepicker('option','dateFormat'), thisObject._selectedDates[i]);
		    }

		    if (dates.length == 1) {
			dates[1] = dates[0];
		    }
		    
		    if (date >= dates[0] && date <= dates[1]) {
			return [true, "ui-state-highlight", "Event Name"];
		    }
		    
		    return [true, ""];
                }
	    });
	    
	    return obj;
	},
	
	_getTimeSelector: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>").addClass("argus-image-selector-time")
	    var objSelect = $("<ol>").selectable();
	    
	    if (!this.options.showSelectButton) {
		objSelect.selectable("option","stop",function() { thisObject._selectTime(); });
	    }
	    
	    obj.append(objSelect)
		.attr("title","Select one or multiple sets of images")
		.tooltip({position:{my:"left top",at:"right+12px top",of:$(obj)}});
	    
	    return obj
	},
	
	_getSelectButton: function() {
	    var thisObject = this;
	    
	    var obj = $("<input>").addClass("argus-image-selector-button")
                .attr("type","button")
                .attr("value",this.options.selectButtonText)
                .bind("click",function() {
                    thisObject._selectTime();
                });
            
	    $(obj).button();
	    
	    return obj
	},
	
	_getRandomButton: function() {
	    var thisObject = this;
	    
	    var obj = $("<input>").addClass("argus-image-selector-button")
                .attr("type","button")
                .attr("value",this.options.randomButtonText)
                .bind("click",function() {
                    thisObject._getRandomSet();
                });
	    
	    $(obj).button()
		.attr("title","Select a random set of images from the selected site, type and camera(s)")
		.tooltip({position:{my:"left",at:"right+12px",of:$(obj)}});
	    
	    return obj
	},
	
	/*****************************************************************************
	 ** ACTION HANDLERS                                                         **
	 *****************************************************************************/
	
	_selectSite: function() {
	    var site  = this._objSelectedSite();
	    var start = this._epochToDate($(site).attr("startEpoch"));
	    var end   = this._epochToDate($(site).attr("endEpoch"));
	    
	    $(this._objDateSelector).datepicker("option","minDate",start)
                .datepicker("option","maxDate",end)
            
	    $.cookie("argus-image-selector-site", $(site).val());
            
	    this._selectDate();
	},
	
	_selectDate: function() {
	    var thisObject = this;
	    var dates = thisObject._objSelectedDate();
	    
	    if (dates.length > 0) {
		var json_url = this.options.jsonHost + "table/imagesets?site=" + this._objSelectedSite().val()
                    + "&type=" + this._getSelectedType()
                    + "&startEpoch=" + this._dateToEpoch(dates[0])
                    + "&endEpoch=" + this._dateToEpoch(dates[1])
                    + "&limit=0"
                    + "&callback=?"
	    
		$.getJSON(json_url, function(data) {
		    $(thisObject._objTimeSelector).children("ol").html("");
		
		    var times = new Array();

		    for (var i = 0; i < data.length; i++) {
			var date = thisObject._epochToDate(data[i]);
			var txt = thisObject._formatTime(date);

			times[i] = txt;
		    }

		    times = times.reverse().filter(
			function (e, i, arr) {
			    return times.indexOf(e, i+1) === -1;
			}).sort();

		    for (var i = 0; i < times.length; i++) {			
			objOption = $("<li>").text(times[i])
			    .attr('addEpoch', 
				  parseInt(times[i].split(":")[0]) * 3600 + 
				  parseInt(times[i].split(":")[1]) * 60);
			
			$(thisObject._objTimeSelector).children("ol").append(objOption);
		    }

		    if ($(thisObject._objTimeSelector).children("ol").children("li").length == 0) {
			$(thisObject._objTimeSelector).children("ol").html(
			    thisObject.options.noImageSetsMessage);
		    }
		});
	    } else {
		$(thisObject._objTimeSelector).children("ol").html(
		    thisObject.options.noImageSetsMessage);
	    }
	},
	
	_selectTime: function() {
	    var thisObject = this;
	    var date = this._objSelectedDate();
	    var time = this._objSelectedTime();

	    var currentDate = date[0];

	    while (currentDate.getTime() <= date[1].getTime()) {
		for (var i=0;i<time.length;i++) {
		    var timeBase = parseInt(thisObject._dateToEpoch(currentDate) + parseInt($(time[i]).attr("addEpoch")));
		    var start = parseInt(timeBase - thisObject.options.marginSet/2);
		    var end   = parseInt(timeBase + thisObject.options.marginSet/2);

		    this._getImages(start, end);
		}

		currentDate.setDate(currentDate.getDate() + 1);
	    }
	},
	
	_getImages: function(start, end) {
	    var thisObject = this;
	    
	    var cam = this._getSelectedCameras();
	    if (cam.length==this.options.maxNrCameras) {
		cam = new Array("");
	    }
	    
	    var json_url = this.options.jsonHost + "table/images?site=" + this._objSelectedSite().val()
                + "&type=" + this._getSelectedType()
                + "&startEpoch=" + start
                + "&endEpoch=" + end
                + "&limit=0"
                + "&callback=?"
            
	    for (var i=0;i<cam.length;i++) {
		if (cam[i].length == 0) {
		    json_url_cam = json_url;
		} else {
		    json_url_cam = json_url + "&camera=" + cam[i];
		}
		
		$.getJSON(json_url_cam, function(data) {
		    var img_urls = new Array();
		    for (var i=0;i<data.length;i++) {
			img_urls[i] = data[i]["path"];
		    }
		    thisObject.options.onSelect(img_urls);
		});
	    }
	    
	    $.cookie("argus-image-selector-type", this._getSelectedType());
	    $.cookie("argus-image-selector-cameras", this._getSelectedCameras());
	},
	
	_getRandomSet: function() {
	    var site  = this._objSelectedSite();
	    var start = parseInt($(site).attr("startEpoch"));
	    var end   = parseInt($(site).attr("endEpoch"));
	    
	    epoch = start + Math.random() * (end - start);
	    
	    epoch1 = parseInt(epoch - this.options.marginSet/2);
	    epoch2 = parseInt(epoch + this.options.marginSet/2);
	    
	    this._getImages(epoch1, epoch2);
	},
  
	/*****************************************************************************
	 ** HELPER FUNCTIONS                                                        **
	 *****************************************************************************/
	
	_toggleButtonset: function(obj) {
	    var objs = $(obj).children('input');
	    var val  = typeof $(obj).children('input:first').attr("checked") === "undefined";
	    for (var i=0;i<objs.length;i++) {
		if (val) {
		    $(objs[i]).attr("checked",true);
		} else {
		    $(objs[i]).removeAttr("checked");
		}
	    }
	    $(obj).buttonset("refresh");
	},
	
	_getSelectedType: function() {
	    return this._objSelectedType().val();
	},
	
	_objSelectedType: function() {
	    return $(this._objTypeSelector).children("input:checked")
	},
	
	_getSelectedCameras: function() {
	    var cam = this._objSelectedCamera();
	    var nrs = new Array();
	    for (var i=0;i<cam.length;i++) {
		nrs[i] = $(cam[i]).val();
	    }
	    return nrs;
	},
	
	_objSelectedCamera: function() {
	    return $(this._objCamSelector).children("input:checked")
	},
	
	_objSelectedSite: function() {
	    return $(this._objSiteSelector).children("select")
                .children("option:selected")
	},
	
	_objSelectedDate: function() {
	    var dates = new Array();

	    if ($(this._selectedDates).length > 0) {

		for (var i = 0; i < $(this._selectedDates).length; i++) {
		    dates[i] = $.datepicker.parseDate(
			$(this._objDateSelector).datepicker('option', 'dateFormat'),
			$(this._selectedDates)[i]);
		}
		
		if (dates.length == 1) {
		    dates[1] = dates[0];
		}

		dates[0] = new Date(dates[0]);
		dates[1] = new Date(dates[1]);
		
		dates[0].setHours(0, 0, 0, 0);
		dates[1].setHours(23, 59, 59, 0);
	    }

	    return dates;
	},
	
	_objSelectedTime: function() {
	    objs = $(this._objTimeSelector).children("ol")
                .children("li.ui-selected");
	    if (objs.length == 0) {
		objs = $(this._objTimeSelector).children("ol")
		    .children("li");
	    }
	    return objs;
	},
	
	_epochToDate: function(epoch) {
	    if (epoch == 0) {
		return new Date();
	    } else {
		return new Date(epoch*1000);
	    }
	},
	
	_dateToEpoch: function(date) {
	    return date.getTime()/1000;
	},
	
	_formatTime: function(date) {
	    var hours = date.getHours();
	    var minutes = date.getMinutes();
	    
	    return this._pad(hours,2,"0") + ":" + this._pad(minutes,2,"0")
	},
	
	_pad: function(str, n, s) {
	    str = ""+str;
	    while (str.length<n) {
		str = s + str;
	    }
	    return str;
	},
	
	_randomHash: function(n) {
	    var hash = "";
	    var characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
	    
	    for (var i=0;i<n;i++) {
		hash += characters.charAt(Math.floor(Math.random() * characters.length));
	    }
	    
	    return hash;
	},

	_addOrRemoveDate: function(date) {
	    var thisObject = this;
	    var index = $.inArray(date, thisObject._selectedDates); 
	    
	    if (index >= 0) {
		thisObject._selectedDates.splice(index, 1);
	    } else {
		if (thisObject._selectedDates.length < 2) {
		    thisObject._selectedDates.push(date);
		} else {
		    thisObject._selectedDates[1] = date;
		}
	    }
	    
	    thisObject._selectedDates.sort();
	}
	
    });
    
})( jQuery );
