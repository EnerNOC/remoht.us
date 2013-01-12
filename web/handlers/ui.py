import webapp2
import logging
import json
from google.appengine.api import xmpp, users, channel

from . import BaseHandler
import config
import model

base_jid = "rpc@rehmote.appspotchat.com"

class RootHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
          self.redirect(users.create_login_url(self.request.uri))
          return

#        devices = model.Device.all()
        self.render('index')


class DeviceHandler(BaseHandler):

    def get(self,_id=None):
        if _id is None:
            devices = model.Device.all()

        else:
            devices = [model.Device.get_by_id(int(_id))]

        if not len(devices):
            return self.notfound()

        self.render_json( {"msg":"OK","devices":devices} )


    def post(self):
        jid = self.request.get('jid',None)
        xmpp.send_invite(jid)
        xmpp.get_presence(jid, get_show=True)

        result = model.Device.from_jid(jid)

        msg = "OK"
        if result != None:
            msg = "JID %s is already added" % jid

        else:
            logging.debug("Added JID %s", jid)
            model.Device(jid=jid).put()

        if self.is_ajax():
            self.render_json({'msg':msg})
            return

        self.redirect('/')


class RelayHandler(BaseHandler):

    def get(self,device_id,relay=None):
        logging.debug("Get relay %s", relay)

        user = users.get_current_user()
        if not user: return self.unauthorized()

        device = model.Device.get_by_id(int(device_id))
        if device is None: return self.notfound()
        
        msg = { "op" : "get_relay",
                "relay" : relay }

        to_jid = device.jid
        resource = device.get_available_resource()
        if resource != None: to_jid = '%s/%s' % (to_jid,resource)

        from_jid = "%s/user-%s" % (base_jid, user.user_id())
        xmpp.send_message(to_jid, json.dumps(msg), from_jid=from_jid)


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
        
        from_jid = "%s/user-%s" % (base_jid, user.user_id())
        xmpp.send_message( to_jid, json.dumps(msg), from_jid=from_jid)
