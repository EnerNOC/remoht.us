var remoht = {
	init : function() {
		remoht.get_devices()
		remoht.open_channel()
	},

	get_devices : function() {
		$.ajax('/device/', {
			success: function(data,stat,xhr) {
				for( i in data.devices ) {
					var device = data.devices[i]
					var element = ich.device_line(device)

					var resource = ''
					for ( resource in device.resources ) {
						var presence = device.resources[resource]
						if ( presence == 'available' ) {
							console.debug("Found available resource: ", resource)
							element.find('.label-important').toggle()
							element.find('.label-ok').toggle()
							element.find('.resource').text(resource)
							break
						}
					}

					$('#device_list').append(element)

					element.bind('click',function(e) {
						e.preventDefault()
						$('#device_header .device_name').text(device.jid+'/'+resource)
						remoht.get_relays(device.id)
					})
				}
			}
		})
	},

	get_relays : function(device_id) {
		// TODO show spinner
		$.ajax('/device/'+device_id+"/relay/", {
			success : function(data,stat,xhr) { 
				// wait for the callback over the channel
			}
		})
	},

	toggle_relay : function(device_id, relay, e) {
		// TODO show spinner
		$.ajax('/device'+device_id+"/relay/"+relay, {
			type : "POST",
			data : { state : 1 }, // FIXME
			dataType : 'JSON',
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

		},

		// response from get_relays ajax request above
		get_relays : function(params) {
			var target_list = $('#relay_list').text('') // clear the existing content

			for( key in params.relays ) {
				
				var relay_button = app.n('a', {
					href : '/device/'+params.id+'/relay/'+key,
					'class' : 'btn'}, 
					"Relay " + key )

				state = params.relays[key]
				relay_button.addClass( state == 0 ? 'btn-success' : 'btn-warn' )

				relay_button.bind( 'click',
						remoht.get_relays.partial( params.device_id, key ) )

				target_list.append(relay_button)
			}
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
						data = JSON.parse(msg.data)
						remoht.channel_commands[data.command](data.data)
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
