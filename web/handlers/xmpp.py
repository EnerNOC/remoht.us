import json
import logging
import model

import webapp2
from google.appengine.api import xmpp, channel


class ChatHandler(webapp2.RequestHandler):
    def post(self):
        logging.info('message! %s', self.request.POST)
        message = xmpp.Message(self.request.POST)

        try:
            parsed = json.loads(message.body)

        except Exception as ex:
            logging.warn("Error parsing message %s", message.body)
            return

        from_jid, resource = message.sender.split('/')
        device = model.Device.from_resource(resource, from_jid)
        if device == None: 
            logging.debug( "Message from unknown device %s/%s", from_jid, resource )    
            return

        cmd = parsed['cmd']

        if cmd == 'get_relays':

            new_relays = parsed['data']['relays']

            if device.relays is None: device.relays = {}

            for relay,state in new_relays.iteritems():
                device.relays[relay] = state

            logging.debug("Updated relays for %s : %s", from_jid, new_relays)
            device.put()

            # pass the message on to the web UI user
            channel_id = device.owner.user_id()            
            channel.send_message( channel_id, 
                    json.dumps({
                        "cmd" : cmd,
                        "data": {
                            "device_id": device.id,
                            "relays" : new_relays
                            }
                        } )
                    )

        else: 
            logging.warn("Unknown command: %s", cmd)


class PresenceHandler(webapp2.RequestHandler):
    def post(self,operation):
        logging.info('Presence! %s', self.request.POST)
        from_jid, resource = self.request.get('from').split('/')

        xmpp_user = model.XMPPUser.get_by_jid( from_jid )

        if xmpp_user is None:
            logging.debug( "Presence from unknown user %s", from_jid )
            return

        if operation == 'probe':
            xmpp.send_presence( from_jid, 
                    status="ready for action!", 
                    presence_show="available")

            return

        # else operation is 'available' or 'unavailable'
        if not resource: return

        xmpp_user.resources[resource] = operation
        xmpp_user.put()
        
        # see if we have a device for this resource:
        device = model.Device.from_resource(resource, from_jid)

        if device != None and device.presence != operation:
            device.presence = operation
            device.put()

        else:
            logging.debug( "Presence from unknown device %s/%s", from_jid, resource )

        # attempt to send presence down to the owner.  If 
        # the owner is not online, no error so no problem
        channel_id = xmpp_user.user.user_id()

        msg = { "cmd" : "presence",
                "data" : {
                    "jid" : from_jid,
                    "resource" : resource,
                    "status" : operation } 
                }
        channel.send_message(channel_id, json.dumps(msg) )


class SubscriptionHandler(webapp2.RequestHandler):
    def post(self,operation):
        logging.info("Subscribe! %s", self.request.POST)
        from_jid = self.request.get('from').split('/')[0]

        if operation == 'subscribe':
            xmpp.send_presence(from_jid, status="available")
            pass

        elif operation == 'subscribed':
            pass

        elif operation == 'unsubscribe':
            # TODO delete JID?
            pass

        elif operation == 'unsubscribed':
            # TODO delete JID?
            pass


class ErrorHandler(webapp2.RequestHandler):
    def post(self):
        logging.warn("Error! %s", self.request.POST)
        
