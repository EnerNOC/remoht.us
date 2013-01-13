var remoht = {
	init : function() {
		remoht.get_devices()
		remoht.open_channel()
		remoht.get_resources()

		$('#resources-refresh').bind('click',function(e) {
			e.preventDefault()
			remoht.get_resources()
		})
	},

	resources : {},

	get_resources : function() {
		$.ajax('/resources/', {
			success : function(data,stat,xhr) {
				remoht.resources = data.resources
				// clear list
				$('#resource_list li').each( function(i,item) {
					console.debug(i,item)
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
		
		$('#resource_list').append(element)

		element.bind('click', function(e) {
			e.preventDefault()
			$.ajax(e.target.href, {
				type : "POST",
				data : {resource:resource},
				success : function(data,stat,xhr) {
					console.debug("Created device!")
					// TODO ensure it doesn't already exist.
					remoht.add_device_to_list( data.device )
				}
			})
		})
	},

	get_devices : function() {
		$.ajax('/device/', {
			success: function(data,stat,xhr) {
				for( i in data.devices ) {
					remoht.add_device_to_list( data.devices[i] )
				}
			}
		})
	},

	add_device_to_list : function(device) {
		var element = ich.device_line(device)

		if ( device.presence == 'available' ) {
			element.find('.label-important').toggle()
			element.find('.label-ok').toggle()
		}

		$('#device_list').append(element)

		element.bind('click',function(e) {
			e.preventDefault()
			$('#device_header .device_name').text(device.jid+'/'+device.resource)
			remoht.get_relays(device.id)
		})
	},
	
	get_relays : function(device_id) {
		// TODO show spinner
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
					'class' : 'btn' }, 
				key )

			state = relays[key]
			relay_button.addClass( state == 0 ? 'btn-success' : 'btn-warn' )

			relay_button.bind( 'click',
					remoht.toggle_relay.partial(device_id, key) )

			target_list.append(relay_button)
		}
	},

	toggle_relay : function(device_id, relay, e) {
		// TODO show spinner
		$.ajax('/device'+device_id+"/relay/"+relay, {
			type : "POST",
			dataType : 'json',
			data : { state : 1 }, // FIXME
			success : function(data,stat,xhr) {
				// wait for callback over socket
			}
		})
	},

	// These commands should correspond to the XMPP commands sent from 
	// a device - see handlers/xmpp.ChatHandler#post()
	channel_commands : {

		presence : function(params) {
			console.debug("Presence!", params)
			if ( remoht.resources[params.resource] == null )
				remoht.add_resource( params.resource, params.status )
			remoht.resources[params.resource] = params.status
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

		telemetry : function(params) {
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
					},

					onclose : function() {
						console.debug("Channel closed")
					}
				})
			}
		})
	},
}
