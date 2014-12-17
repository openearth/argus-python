(function( $, undefined ) {
    
    var thisObject = this;
    
    $.widget( "ui.argusImagePlugins", {
	version: "0.0.1",
	options: {
	    jsonHost: "http://dtvirt61.deltares.nl/argusplugins/",
	    applyButtonText: "Apply plugins",
	    getCurrentFigure: null,
	    setCurrentFigure: null,
	},

	_objPluginSelector: null,
	
	_create: function() {
	    var thisObject = this;
	    
	    objClr = '<div style="clear:both;">';
	    
	    $(window).bind("load", function() { thisObject._resize(); })
		.bind("resize", function() { thisObject._resize(); });
	    
	    $(this.element).addClass("argus-image-plugins");
	    
	    this._objPluginSelector = this._getPluginSelector();

	    $(this.element).append(this._objPluginSelector)
    
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

	_getPluginSelector: function() {
	    var thisObject = this;
	    
	    var obj = $("<div>").addClass("argus-image-plugins-selector");	    
	    var objPlugins = $("<div>");

	    // add plugin list
	    var json_url = this.options.jsonHost + "plugins?callback=?";
	    $.getJSON(json_url, function(data) {
		for (var i=0;i<data.length;i++) {
		    var plugin = data[i];

		    var objGroup = $("<div>").addClass("group");
		    var objHeader = $("<h3>").text(plugin)
		    var objBody = $("<div>");

		    $("<label>")
			.text("enable plugin")
			.attr("for","enable_" + plugin)
			.appendTo(objBody);

		    $("<input>")
			.attr("type","checkbox")
			.attr("id","enable_" + plugin)
			.attr("name","enable[]")
			.attr("value",plugin)
			.css("float","right")
			.appendTo(objBody);

		    $("<div>")
			.addClass("hline")
			.appendTo(objBody);
		    
		    // add settings for current plugin
		    var json_url = thisObject.options.jsonHost + 
			"plugins/" + plugin + "?callback=?";

		    $.getJSON(json_url, function(data) {
			for (var item in data) {
			    objBody.append(
				thisObject._option2html(plugin, item, data[item]));
			}
		    });

		    objHeader.appendTo(objGroup);
		    objBody.appendTo(objGroup);
		    objGroup.appendTo(objPlugins);
		};
		
		objPlugins.accordion({
		    header: "> div > h3",
		    heightStyle: "content"
		}).sortable({
		    axis: "y",
		    handle: "h3",
		});
	    });

	    objPlugins
		.appendTo(obj);

	    // add slice spinner
	    objSlice = $("<div>")
		.addClass("argus-image-plugins-slice")
		.appendTo(obj);

	    $("<label>")
		.attr("for","slice")
		.text("slice:")
		.appendTo(objSlice);

	    $("<br>").appendTo(objSlice);

	    $("<input>")
		.attr("name","slice")
		.attr("id","slice")
		.val("10")
		.appendTo(objSlice);

	    // add apply button
	    $("<input>")
		.attr("type","button")
		.attr("value",thisObject.options.applyButtonText)
		.bind("click", function() { thisObject._applyPlugin(); })
		.css("width","100%")
		.button()
		.appendTo(obj);
            
	    return obj;
	},	
	
	/*****************************************************************************
	 ** ACTION HANDLERS                                                         **
	 *****************************************************************************/
	
	_applyPlugin: function() {
	    var thisObject = this;

	    var url = thisObject.options.getCurrentFigure();
	    var plugins = $(thisObject.element).find("input[name='enable[]']:checked");
	    var pluginPath = "";
	    var pluginOptions = "";

	    for (var i=0; i<plugins.length; i++) {
		var plugin = $(plugins[i]).val();
		pluginPath = pluginPath + plugin + "/"

		var options = $(thisObject.element)
		    .find("[plugin='" + plugin + "']:input");

		for (var j=0; j<options.length; j++) {
		    var option = $(options[j]);
		    if ($(option).attr("type") == "checkbox") {
			var val = $(option).prop("checked");
		    } else {
			var val = $(option).val();
		    }

		    pluginOptions = pluginOptions + "&" + 
			$(option).attr("option") + "=" + val;
		} 
	    }

	    if (pluginPath.length > 0) {
		url = url.replace(/^.*[\\\/]/,
				  "http://dtvirt61.deltares.nl/argusplugins/plugins/" + 
				  pluginPath)

		url = url.replace(/\?.*$/, "");

		url = url + "?slice=" + parseInt(
		    $(thisObject.element).find("#slice").val());

		url = url + pluginOptions;

		thisObject.options.setCurrentFigure(url);
	    }
	},
	
	/*****************************************************************************
	 ** HELPER FUNCTIONS                                                        **
	 *****************************************************************************/

	_option2html: function(plugin, option, value) {
	    var obj = $("<div>")
		.css("width","100%")
		.css("height","25px");

	    var id = "option_" + plugin + "_" + option;
	    var name = "option[" + plugin + "][" + option + "]";

	    if (value instanceof Array) {
		objItem = $("<select>");
		for (var i=0; i<value.length; i++) {
		    objItem.append(
			$("<option>")
			    .attr("value",value[i])
			    .text(value[i]));
		}
	    } else {
		switch (typeof value) {
		case "number":
		    objItem = $("<input>")
			.attr("type","text")
			.attr("size",10)
			.attr("value",value);
		    break;
		case "boolean":
		    objItem = $("<input>")
			.attr("type","checkbox")
			.attr("value","1")
			.prop("checked",value);
		    break;
		case "string":
		    objItem = $("<input>")
			.attr("type","text")
			.attr("size",20)
			.attr("value",value);
		    break;
		}
	    }

	    $("<label>")
		.attr("for",id)
		.text(option + ":")
		.appendTo(obj);

	    objItem
		.attr("id",id)
		.attr("name",name)
		.attr("option",option)
		.attr("plugin",plugin)
		.css("float","right")
		.appendTo(obj);

	    return obj;
	},
	
    });
    
})( jQuery );
