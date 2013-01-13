# Copyright (c) 2011 Thom Nichols

__author__ = 'Thom Nichols'

import config
import os
import sys
import logging

# Force sys.path to have our own directory first, so we can import from it.
sys.path.insert(0, config.APP_ROOT_DIR)
sys.path.insert(1, os.path.join(config.APP_ROOT_DIR, 'lib'))

import webapp2
import utils
import handlers
from handlers import xmpp, ui, channel

# Configure logging for debug if in dev environment
if config.DEBUG: logging.getLogger().setLevel(logging.DEBUG)

#logging.debug("Env: %s",os.environ)
logging.info('Loading %s, version = %s',
        os.getenv('APPLICATION_ID'),
        os.getenv('CURRENT_VERSION_ID'))


ROUTES = [
    ('/_ah/xmpp/message/chat/',       xmpp.ChatHandler),
    ('/_ah/xmpp/presence/(\w+)/',     xmpp.PresenceHandler),
    ('/_ah/xmpp/subscription/(\w+)/', xmpp.SubscriptionHandler),
    ('/_ah/xmpp/error/',              xmpp.ErrorHandler),

    ('/_ah/channel/(\w+)/',   channel.ConnectionHandler),
    ('/token/',                channel.TokenRequestHandler),

    ('/$',                        ui.RootHandler),
    ('/resources/$',              ui.ResourcesHandler),
    ('/device/(\d+)/relay/(.*)$', ui.RelayHandler),
    ('/device/',                  ui.DeviceHandler),

    ('/logout',          handlers.LogoutHandler),
    ]


APP_CONFIG= {
    'webapp2_extras.sessions' : {
        'secret_key' : 'askdfs',
        'session_max_age' : 60*60*12 # 12 hours
    },
    'webapp2_extras.jinja2' : {
        'template_path' : 'views',
        'globals' : config.PAGE,
        'environment_args' : {
            'auto_reload' : config.DEBUG,
            'autoescape' : handlers.guess_autoescape, 
            'extensions' : ['jinja2.ext.autoescape']
        }
    }
}

app = webapp2.WSGIApplication(ROUTES, debug=config.DEBUG, config=APP_CONFIG)

def main(): app.run()

if __name__ == "__main__": main()
