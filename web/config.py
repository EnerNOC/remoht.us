import os
import logging

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# If we're debugging, turn the cache off, etc.
# Set to true if we want to have our webapp print stack traces, etc
DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')

APP = {
#    "version": "0.1",
#    "html_type": "application/xhtml+xml",
#    "charset": "utf-8",
    "root_url": "http://remohte.appspot.com" if not DEBUG else 'http://localhost:8080',
    "cache_time": 60*20,   # 20 minutes
    'jid' : 'tmnichols@gmail.com',
}

# static values that go into view templates
PAGE = {
    'root_url': APP['root_url'],
    'debug': DEBUG
}
