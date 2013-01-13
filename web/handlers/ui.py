import webapp2
import logging
import json
from google.appengine.api import xmpp, users, channel

from . import BaseHandler
import config
import model

#base_jid = "rpc@rehmote.appspotchat.com"

class RootHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
          self.redirect(users.create_login_url(self.request.uri))
          return

        self.render('index')


class DeviceHandler(BaseHandler):

    def get(self,_id=None):
        if _id is None:
            devices = model.Device.all()

        else:
            device = model.Device.get_by_id(int(_id))
            if device.owner != users.get_current_user():
                return self.unauthorized()

            devices = [device]

        self.render_json( {"msg":"OK","devices":devices} )


    def post(self):
        resource = self.request.get('resource')

        user = users.get_current_user()
        jid = user.email()
        full_jid = '%s/%s' % (jid, resource)
        online, avail = xmpp.get_presence(full_jid, get_show=True)

        device = model.Device.from_resource(resource)

        msg = "OK"
        if device != None:
            msg = "JID %s is already added" % jid
            self.response.status = 304

        else:
            logging.debug("Adding device %s", full_jid)
            device = model.Device( 
                    owner = user,
                    jid = jid,
                    resource = resource,
                    presence = avail )
            device.put()

        self.render_json({'msg':msg,"device":device})


class ResourcesHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            return self.unauthorized()

        xmpp_user = model.XMPPUser.get_current_user()

        jid = user.email()
        if xmpp_user is None:
            xmpp_user = model.XMPPUser.new()
            xmpp_user.put()
            xmpp.send_invite(jid)

        xmpp.send_presence(jid, presence_type=xmpp.PRESENCE_TYPE_PROBE)
        self.render_json({"msg":"OK", "resources":xmpp_user.resources})


class RelayHandler(BaseHandler):

    def get(self,device_id,relay=None):
        logging.debug("Get relay %s", relay)

        user = users.get_current_user()
        if not user: return self.unauthorized()

        logging.info("Device ID: %d", int(device_id))
        device = model.Device.get_by_id(int(device_id))
        if device is None: return self.notfound()
        
        msg = { "op" : "get_relay",
                "relay" : relay }

        xmpp.send_message(device.full_jid, json.dumps(msg))
        self.render_json({"msg":"OK","relays":device.relays})


    def post(self, device_id, relay):
        logging.debug("Toggle relay %s", relay)

        user = users.get_current_user()
        if not user: return self.unauthorized()

        device = model.Device.get_by_id(int(device_id))
        if device is None: return self.notfound()

        msg = { "op" : "set_relay",
                "relay" : relay }

        to_jid = device.jid
        resource = device.get_available_resource()
        if resource != None: to_jid = '%s/%s' % (to_jid,resource)
        
#        from_jid = "%s/user-%s" % (base_jid, user.user_id())
        xmpp.send_message( to_jid, json.dumps(msg))#, from_jid=from_jid)
