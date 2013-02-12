var app = {
	/**
	 * Node builder.  Call like:
	 * n('div',{class:'top'},'inner text') // or:
	 * n('div',{class:'top'},[n('p',{},'nested element'])
	 */
	n: function(e,attrs,inner) {
		if(typeof(e)=='string') e = document.createElement(e);
		if (attrs) for (var k in attrs) e.setAttribute(k,attrs[k]);
		if (inner) {
			if (typeof(inner)=='string') e.textContent = inner;
			else if (inner.call) inner.call(e);
			else for (var i in inner) e.appendChild(inner[i]);
		}
		return $(e);
	},

	/**
	 * Tweet tmpl:
	 * http://mir.aculo.us/2011/03/09/little-helpers-a-tweet-sized-javascript-templating-engine/
	 * Call it like this:
	 * t("Hello {who}!", { who: "JavaScript" });
	 */ 
	t: function(s,d) {
		for(var p in d)
			s=s.replace(new RegExp('{'+p+'}','g'), d[p]);
		return s;
	},

	relativeTime : function( from ) {
		var MIN = 60;
		var HOUR = MIN * 60;
		var DAY = HOUR * 24;
		var WEEK = DAY * 7;
		var MONTH = DAY * 30;
		var YEAR = DAY * 365;
		if (typeof(from) == 'string') from = new Date(from).getTime();
		else if (typeof(from) == 'object') from = from.getTime();
		var diff = (new Date().getTime() - from)/1000;
		var pastPresent = ' ago';
		if ( diff < 0 ) {
			pastPresent = ' from now';
			diff = Math.abs(diff);
		}
		if ( diff < 1 ) return "just now";
		if ( diff < MIN ) 
			var amount = diff, unit = ' second';
		else if ( diff < HOUR ) 
			var amount = diff/MIN, unit = ' minute';
		else if ( diff < DAY ) 
			var amount = diff/HOUR, unit = ' hour';
		else if ( diff < WEEK ) 
			var amount = diff/DAY, unit = ' day';
		else if ( diff < MONTH ) 
			var amount = diff/WEEK, unit = ' week';
		else if ( diff < YEAR ) 
			var amount = diff/MONTH, unit = ' month';
		else 
			var amount = diff/YEAR, unit = ' year';
		return "" + Math.floor(amount) + unit + (amount < 2 ? "" : "s") + pastPresent;
	},

	scrollTo : function(selector) {
		var offset = $(selector).offset();
		$('html, body').animate({
				scrollTop: offset.top-30,
				scrollLeft: offset.left-20
		});
	}
}

if ( typeof(Function.prototype.partial) == "undefined" ) {
	Function.prototype.partial = function() {
    var fn = this, args = Array.prototype.slice.call(arguments);
    return function(){
      var arg = 0;
      for ( var i = 0; i < args.length && arg < arguments.length; i++ )
        if ( args[i] === undefined )
          args[i] = arguments[arg++];
      return fn.apply(this, args);
    };
  };
}

// Stub for conole.log for browsers that don't have support
if ( ! window.console ) {
	var methods = "debug,error,exception,info,log,trace,warn".split(","),
	    console = {},
	    l = methods.length,
	    fn = function() {}

	while (l--) console[methods[l]] = fn
	window.console = console
}
