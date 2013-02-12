import json
import logging
import model

import webapp2
from google.appengine.api import xmpp, channel

# GTalk puts a hash on the end of resources.  Look for this character to 
# remove the hash
RESOURCE_TAG = ':'

def split_jid(full_jid):
    jid, resource = full_jid.split('/')
    if  resource.find(RESOURCE_TAG) >=0:
        resource = resource.split(RESOURCE_TAG)[0] 

    return jid, resource

class ChatHandler(webapp2.RequestHandler):
    def post(self):
        logging.info('message! %s', self.request.POST)
        message = xmpp.Message(self.request.POST)

        try:
            parsed = json.loads(message.body)

        except Exception as ex:
            logging.warn("Error parsing message %s", message.body)
            return

        from_jid, resource = split_jid(message.sender)

        device = model.Device.from_resource(resource, from_jid)
        if device == None: 
            logging.debug( "Message from unknown device %s/%s", from_jid, resource )    
            return

        cmd = parsed['cmd']
        logging.debug('---- COMMAND: %s', cmd)

        if cmd == 'get_relays':
            logging.debug("NEW RELAYS: %s",parsed.get('data',None))

            data = parsed['data']

            if device.relays is None: device.relays = {}

            for relay,state in data['relays'].iteritems():
                device.relays[relay] = state

            logging.debug("Updated relays for %s : %s", message.sender, data)
            device.put()

            # pass the message on to the web UI user
            channel_id = device.owner.user_id()
            data['device_id'] = device.id
            channel.send_message( channel_id, 
                    json.dumps({
                        "cmd" : cmd,
                        "data": data
                        })
                    )

        elif cmd == 'readings':
            channel_id = device.owner.user_id()
            parsed['data']['device_id'] = device.id
            channel.send_message( channel_id,
                    json.dumps(parsed) )

        else: 
            logging.warn("Unknown command: %s", cmd)


class PresenceHandler(webapp2.RequestHandler):
    def post(self,operation):
        logging.info('Presence! %s', self.request.POST)
        from_jid, resource = split_jid( self.request.get('from') )
        full_resource = self.request.get('from').split('/')[1]

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
        if not resource: return logging.debug("No resource on %s", from_jid)

        xmpp_user.resources[resource] = operation
        xmpp_user.put()
        
        # see if we have a device for this resource:
        device = model.Device.from_resource(resource, from_jid)

        if device != None and device.presence != operation:
            device.presence = operation
            device.put()

        elif device is None:
            logging.debug( "Presence from unknown device %s/%s", from_jid, resource )

        model.cache_full_resource(from_jid, resource, full_resource)

        # attempt to send presence down to the owner.  If 
        # the owner is not online, no error so no problem
        channel_id = xmpp_user.user.user_id()

        msg = { "cmd" : "presence",
                "data" : {
                    "jid" : from_jid,
                    "resource" : resource,
                    "presence" : operation } 
                }
        channel.send_message(channel_id, json.dumps(msg) )


class SubscriptionHandler(webapp2.RequestHandler):
    def post(self,operation):
        logging.info("Subscribe! %s", self.request.POST)
        from_jid = split_jid( self.request.get('from') )[0]

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
        
