var remoht = {
	init : function() {
		$(document)
	   .ajaxStart( function(e) { $('.spinner').fadeIn() })
		 .ajaxStop(  function(e) { $('.spinner').fadeOut() })

		if ( remoht.logged_in ) {
			remoht.get_devices()
			remoht.open_channel()
			remoht.get_resources()
		}

		$('#resources-refresh').bind('click',function(e) {
			e.preventDefault()
			remoht.get_resources()
		})

		remoht.setup_chart()
		if ( ! remoht.logged_in ) remoht.start_demo()
	},

	logged_in : false,

	/* Resources are the list of available JID resources to choose from.
	 * Not all of them will be devices (TODO we should look for a specific
	 * pattern, e.g. "remoht_device1" or something similar.)
	 */
	resources : {},

	get_resources : function() {
		$.ajax('/resources/', {
			success : function(data,stat,xhr) {
				remoht.resources = data.resources
				// clear list
				$('#resource_list li').each( function(i,item) {
					if (i == 0) return
					$(item).remove() // clear list except for header
				})
				// iterating over a dict of resource:presence items
				for ( i in data.resources ) {
					remoht.add_resource(i, data.resources[i] )
				}
			}
		})
	},

	add_resource : function(resource,presence) {
		var element = ich.resource_line({resource:resource,presence:presence})
					
		remoht.toggle_presence(element, presence)
		
		$('#resource_list').append(element)

		element.bind('click', function(e) {
			e.preventDefault()
			$.ajax('/device/', {
				type : "POST",
				data : {resource:resource},
				success : function(data,stat,xhr) {
					console.debug("Created device!", data.device)
					// TODO ensure it doesn't already exist.
					remoht.add_device_to_list( data.device )
				}
			})
		})
	},

	/* Devices are essentially resources that have been chosen as beloning
	 * to an actual RPi, so we should expect to see readings & responses
	 * when it is selected.
	 */
	get_devices : function() {
		$.ajax('/device/', {
			success: function(data,stat,xhr) {
				$('#device_list').find('li').each(function(i,item) {
					item = $(item)
					if ( ! item.hasClass('nav-header') ) item.remove() 
				})
				for( i in data.devices ) {
					remoht.add_device_to_list( data.devices[i] )
				}
			}
		})
	},

	add_device_to_list : function(device) {
		var element = ich.device_line(device)

		remoht.toggle_presence(element, device.presence)

		$('#device_list').append(element)

		element.bind('click',function(e) {
			e.preventDefault()
			$('#device_header .device_name').text(device.jid+'/'+device.resource)
			remoht.current_device_id = device.id
			remoht.get_relays(device.id)
		})
	},

	toggle_presence : function(elem,presence) {
		if ( ! elem ) return
		if ( presence == 'available' ) {
			elem.find('.label-important').hide()
			elem.find('.label-success').show()
		}
		else {
			elem.find('.label-important').show()
			elem.find('.label-success').hide()
		}
	},
	
	get_relays : function(device_id) {
		$.ajax('/device/'+device_id+"/relay/", {
			success : function(data,stat,xhr) { 
				remoht.show_relays(device_id, data.relays)
			}
		})
	},

	show_relays: function(device_id, relays) {
		var target_list = $('#relay_list').text('') // clear the existing content

		for( key in relays ) {
			
			var relay_button = app.n('a', {
					href : '/device/'+device_id+'/relay/'+key,
					'class' : 'btn btn-large' }, 
				key )

			var state = relays[key]
			if ( state ) relay_button.addClass('btn-primary')
			else relay_button.removeClass('btn-primary')

			relay_button.bind( 'click', function(e) {
				remoht.toggle_relay(device_id, key, state)
				e.preventDefault()
			})

			target_list.append(relay_button)
		}
	},

	toggle_relay : function(device_id, relay, fromState) {
		$.ajax('/device/'+device_id+"/relay/"+relay, {
			type : "POST",
			dataType : 'json',
			data : { state : fromState == 0 ? 1 : 0 },
			success : function(data,stat,xhr) {
				// wait for callback over socket
			}
		})
	},

	last_reading : {}, // gets populated from channel push

	cubism_source : function(context) {
		var source = {};
		source.metric = function(prop, title) {
			var metric = context.metric(function(start, stop, step, callback) {
				var vals = [function(e) { return e[prop] }(remoht.last_reading)]
				// callback expects this many elements, just duplicate the last val:
				var elements = (stop - start) / step
				for( var i=1; i<elements; i++ ) vals.push(vals[0])
				callback(null, vals)
			});
			metric.toString = function() { return title; }
			return metric
		}
		return source
	},

	setup_chart : function() {
		var context = cubism.context()
			.serverDelay(0) 
			.clientDelay(0)
			.step(2e3)
			.size($('#chart').width()) // TODO dynamically resize

		var chartHeight= 50
		var source = remoht.cubism_source(context)
		var temp = source.metric('temp_c', 'Temp °C')
		var light = source.metric('light_pct', 'Light')
		var occupancy = source.metric('pir', 'Occupied')

		var horizonTemp = context.horizon()
			.height(chartHeight).mode("offset")
			.extent([5.0, 40.0])
			.colors(["#08519c","#3182bd","#bdd7e7","#6baed6"])
//			.colors(["#bae4b3","#74c476",'#79f17c',"#ca7eff","#ba57ff","#9a0aff"])

		var horizonLight = context.horizon()
			.height(chartHeight).mode("offset")
			.extent([0, 100])
			.colors(["#ea9611","#f3ba5f","#f3ba5f","#ea9611"])

		var horizonOccupancy = context.horizon()
			.height(chartHeight).mode("offset")
			.extent([0, 1])
			.colors(['#e82f2f', '#e82f2f'])

		d3.select('#chart').call(function(div) {
			div.append("div").attr("class", "axis")
				.call( context.axis()
					.orient("top")
					.ticks(d3.time.minutes, 5)
					.tickSubdivide(5) )

			div.append("div").datum(temp)
				.attr("class", "horizon")
				.call(horizonTemp)

			div.append("div").datum(light)
				.attr("class", "horizon")
				.call(horizonLight)

			div.append("div").datum(occupancy)
				.attr("class", "horizon")
				.call(horizonOccupancy)

			div.append("div")
				.attr("class", "rule")
				.call(context.rule()); 
		})

		context.on("focus", function(i) {
			d3.selectAll(".value").style(
				"right", i == null ? null : context.size() - i + "px");
		})
	},

	// These commands should correspond to the XMPP commands sent from 
	// a device - see handlers/xmpp.ChatHandler#post()
	channel_commands : {

		presence : function(params) {
			console.debug("Presence!", params)
			if ( remoht.resources[params.resource] == null )
				remoht.add_resource( params.resource, params.presence )
			remoht.resources[params.resource] = params.presence

			// update device & resources list
			remoht.toggle_presence(
					$('.resource.res-'+params.resource).parent(), 
					params.presence)
		},

		// response from get_relays ajax request above
		get_relays : function(params) {
			remoht.show_relays(params.device_id, params.relays)
			// TODO hide spinner
		},

		relay_result : function(params) {
		},

		list_data_streams : function(params) {
		},

		readings : function(params) {
			if ( remoht.current_device_id != params.device_id ) {
				console.debug("Not current device")
				return
			}

			params.light_pct = parseInt(params.light_pct*100)
			$('#temp').text(params.temp_c)
			$('#light').text(params.light_pct)
			$('#pir').text(params.pir)

			remoht.last_reading = params // store only the last value
		}
	},

	open_channel : function() {
		$.ajax('/token/', {
			success: function(data,stat,xhr) {
				remoht.token = data.token
				remoht.channel = new goog.appengine.Channel(remoht.token)

				remoht.channel.open({
					onopen : function() {
						console.debug("Channel opened", arguments)
					},

					onmessage : function(msg) {
						console.debug("Channel message", msg)
						try {
							data = JSON.parse(msg.data)
							remoht.channel_commands[data.cmd](data.data)
						}
						catch(e) { console.warn("Channel onmessage error", e) }
					},

					onerror : function(err) {
						console.warn(err)
						remoht.open_channel() // re-open channel
					},

					onclose : function() {
						console.debug("Channel closed")
					}
				})	
			}
		})
	},

	start_demo : function() {
		remoht.current_device_id = "DUMMY"
		$('#device_header .device_name').text("(this is demo mode!)")

		remoht.add_device_to_list({
			id : "DUMMY",
			resource : "dummy_device",
			presence : "available"
		})

		remoht.show_relays( "DUMMY", {
			relay_1 : 0,
			relay_2 : 1
		})

		var last_vals = {
			device_id : "DUMMY",
			light_pct : 80.0,
			temp_c : 23.4, 
			pir : 0
		}

		rand = function(min, max) {
			return Math.random() * (max - min) + min;
		}

		window.setInterval( function() {
			last_vals.light_pct = Math.max( 0, Math.min( 
					1, last_vals.light_pct/ 100.0 + rand( -.03, .03 ) ) )
			last_vals.temp_c = Math.round(Math.max( 5, Math.min( 
					40, last_vals.temp_c + rand( -2, 2 ) ) ) * 100 ) / 100
			if ( rand( 0, 10 ) > 9.5 ) // toggle last_vals
				last_vals.pir = last_vals.pir == 1 ? 0 : 1

			remoht.channel_commands.readings( last_vals )
		}, 2000 )
	}
}
