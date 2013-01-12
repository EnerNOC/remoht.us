
import json
import logging
import model

import webapp2
from google.appengine.api import xmpp, channel, users
from . import BaseHandler


class ConnectionHandler(webapp2.RequestHandler):
    def post(self,action):
        logging.debug("Channel %s : %s", action, self.request.POST)
        client_id = self.request.get('from')


class TokenRequestHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if not user: return self.unauthorized()

        token = channel.create_channel( user.user_id() )
        response = { "msg": "OK",
                     "token": token }
        self.render_json( response )
