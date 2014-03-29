/*
 * jquery.flot.tooltip
 * 
 * description: easy-to-use tooltips for Flot charts
 * version: 0.6.4
 * author: Krzysztof Urbas @krzysu [myviews.pl]
 * website: https://github.com/krzysu/flot.tooltip
 * 
 * build on 2014-01-20
 * released under MIT License, 2012
*/ 
(function ($) {

    // plugin options, default values
    var defaultOptions = {
        tooltip: false,
	tooltipText: null,
        tooltipOpts: {
            content: "%s | X: %x | Y: %y",
            // allowed templates are:
            // %s -> series label,
            // %x -> X value,
            // %y -> Y value,
            // %x.2 -> precision of X value,
            // %p -> percent
            xDateFormat: null,
            yDateFormat: null,
            monthNames: null,
            dayNames: null,
            shifts: {
                x: 10,
                y: 20
            },
            defaultTheme: true,

            // callbacks
            onHover: function(flotItem, $tooltipEl) {}
        }
    };

    // object
    var FlotTooltip = function(plot) {

        // variables
        this.tipPosition = {x: 0, y: 0};

        this.init(plot);
    };

    // main plugin function
    FlotTooltip.prototype.init = function(plot) {

        var that = this;

        plot.hooks.bindEvents.push(function (plot, eventHolder) {

            // get plot options
            that.plotOptions = plot.getOptions();

            // if not enabled return
            if (that.plotOptions.tooltip === false || typeof that.plotOptions.tooltip === 'undefined') return;

            // shortcut to access tooltip options
            that.tooltipOptions = that.plotOptions.tooltipOpts;

            // create tooltip DOM element
            var $tip = that.getDomElement();

            // bind event
            $( plot.getPlaceholder() ).bind("plothover", plothover);

			$(eventHolder).bind('mousemove', mouseMove);
        });

		plot.hooks.shutdown.push(function (plot, eventHolder){
			$(plot.getPlaceholder()).unbind("plothover", plothover);
			$(eventHolder).unbind("mousemove", mouseMove);
		});

        function mouseMove(e){
            var pos = {};
            pos.x = e.pageX;
            pos.y = e.pageY;
            that.updateTooltipPosition(pos);
        }

		function plothover(event, pos, item) {
			var $tip = that.getDomElement();
            if (item) {
                var tipText;

                // convert tooltip content template to real tipText
                tipText = that.stringFormat(that.tooltipOptions.content, item);

                $tip.html( tipText );
                that.updateTooltipPosition({ x: pos.pageX, y: pos.pageY });
                $tip.css({
                        left: that.tipPosition.x + that.tooltipOptions.shifts.x,
                        top: that.tipPosition.y + that.tooltipOptions.shifts.y
                    })
                    .show();

                // run callback
                if(typeof that.tooltipOptions.onHover === 'function') {
                    that.tooltipOptions.onHover(item, $tip);
                }
            }
            else {
                $tip.hide().html('');
            }
        }
    };

    /**
     * get or create tooltip DOM element
     * @return jQuery object
     */
    FlotTooltip.prototype.getDomElement = function() {
        var $tip;

        if( $('#flotTip').length > 0 ){
            $tip = $('#flotTip');
        }
        else {
            $tip = $('<div />').attr('id', 'flotTip');
            $tip.appendTo('body').hide().css({position: 'absolute'});

            if(this.tooltipOptions.defaultTheme) {
                $tip.css({
                    'background': '#fff',
                    'z-index': '100',
                    'padding': '0.4em 0.6em',
                    'border-radius': '0.5em',
                    'font-size': '0.8em',
                    'border': '1px solid #111',
                    'display': 'none',
                    'white-space': 'nowrap'
                });
            }
        }

        return $tip;
    };

    // as the name says
    FlotTooltip.prototype.updateTooltipPosition = function(pos) {
        var totalTipWidth = $("#flotTip").outerWidth() + this.tooltipOptions.shifts.x;
        var totalTipHeight = $("#flotTip").outerHeight() + this.tooltipOptions.shifts.y;
        if ((pos.x - $(window).scrollLeft()) > ($(window).innerWidth() - totalTipWidth)) {
            pos.x -= totalTipWidth;
        }
        if ((pos.y - $(window).scrollTop()) > ($(window).innerHeight() - totalTipHeight)) {
            pos.y -= totalTipHeight;
        }
        this.tipPosition.x = pos.x;
        this.tipPosition.y = pos.y;
    };

    /**
     * core function, create tooltip content
     * @param  {string} content - template with tooltip content
     * @param  {object} item - Flot item
     * @return {string} real tooltip content for current item
     */
    FlotTooltip.prototype.stringFormat = function(content, item) {

        var percentPattern = /%p\.{0,1}(\d{0,})/;
        var seriesPattern = /%s/;
        var xPattern = /%x\.{0,1}(\d{0,})/;
        var yPattern = /%y\.{0,1}(\d{0,})/;
        var xPatternWithoutPrecision = "%x";
        var yPatternWithoutPrecision = "%y";

        var x = item.series.data[item.dataIndex][0]; // not item.datapoint[0];
        var y = item.series.data[item.dataIndex][1]; // not item.datapoint[1];
	var l = item.series.labels[item.dataIndex];
	return l
    };

    // helpers just for readability
    FlotTooltip.prototype.isTimeMode = function(axisName, item) {
        return (typeof item.series[axisName].options.mode !== 'undefined' && item.series[axisName].options.mode === 'time');
    };

    FlotTooltip.prototype.isXDateFormat = function(item) {
        return (typeof this.tooltipOptions.xDateFormat !== 'undefined' && this.tooltipOptions.xDateFormat !== null);
    };

    FlotTooltip.prototype.isYDateFormat = function(item) {
        return (typeof this.tooltipOptions.yDateFormat !== 'undefined' && this.tooltipOptions.yDateFormat !== null);
    };

    //
    FlotTooltip.prototype.timestampToDate = function(tmst, dateFormat) {
        var theDate = new Date(tmst*1);
        return $.plot.formatDate(theDate, dateFormat, this.tooltipOptions.monthNames, this.tooltipOptions.dayNames);
    };

    //
    FlotTooltip.prototype.adjustValPrecision = function(pattern, content, value) {

        var precision;
        var matchResult = content.match(pattern);
        if( matchResult !== null ) {
            if(RegExp.$1 !== '') {
                precision = RegExp.$1;
                value = value.toFixed(precision);

                // only replace content if precision exists, in other case use thickformater
                content = content.replace(pattern, value);
            }
        }
        return content;
    };

    //
    var init = function(plot) {
      new FlotTooltip(plot);
    };

    // define Flot plugin
    $.plot.plugins.push({
        init: init,
        options: defaultOptions,
        name: 'tooltip',
        version: '0.6.1'
    });

})(jQuery);
