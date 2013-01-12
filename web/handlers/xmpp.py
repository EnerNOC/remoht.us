import json
import logging
import model

import webapp2
from google.appengine.api import xmpp, channel


class ChatHandler(webapp2.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        logging.info('message! %s', message)

        try:
            parsed = json.loads(message.body)

        except Exception as ex:
            logging.warn("Error parsing message %s", message.body)
            return

        cmd = parsed['cmd']

        if cmd == 'get_relay_result':
            jid, resource = message.sender.split('/')
            device = model.Device.from_jid(jid)

            new_relays = parsed['relays']

            if device.relays is None: device.relays = {}

            for relay,state in new_relays:
                device.relays[relay] = state

            logging.debug("Updated relays for %s : %s", jid, new_relays)
            device.put()

            # pass the message on to the web UI user
            to_jid, to_resource = message.to.split('/')
            if to_resource.find('user-') == 0:
                channel_id = to_resource.split('-')
            channel.send_message(channel_id, message.body)

        else: 
            logging.warn("Unknown command: %s", cmd)


class PresenceHandler(webapp2.RequestHandler):
    def post(self,operation):
        logging.info('Presence! %s', self.request.POST)
        sender, resource = self.request.get('from').split('/')
        
        device = model.Device.from_jid(sender)

        if device == None: 
            logging.debug( "Presence from unknown device %s", sender )    
            return

        if operation in ('available', 'unavailable'):
            device.resources[resource] = operation
            device.put()

            to_jid = self.request.get('to')
            if '/' in to_jid:
                # pass the presence update to the web UI user
                to_jid, to_resource = to_jid.split('/')
                if to_resource.find('user-') == 0:
                    channel_id = to_resource.split('-')

                    msg = { "cmd" : "presence",
                            "params" : {
                                "jid" : sender,
                                "resource" : resource,
                                "status" : operation } 
                            }
                    channel.send_message(channel_id, json.dumps(msg) )

        elif operation == 'probe':
            xmpp.send_presence( sender, 
                    status="available", 
                    presence_show=self.request.get('show'))
            


class SubscriptionHandler(webapp2.RequestHandler):
    def post(self,operation):
        logging.info("Subscribe! %s", self.request.POST)
        sender = self.request.get('from').split('/')[0]

        if operation == 'subscribe':
            xmpp.send_presence(sender, status="available")
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
        
