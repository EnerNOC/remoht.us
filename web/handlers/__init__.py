import logging
import json

import webapp2
import jinja2
from webapp2_extras import jinja2 as jinja_helper
from webapp2_extras import sessions
from google.appengine.api import memcache, users
from google.appengine.ext import db

import config
import utils
import model

DEFAULT_CONTENT_TYPE = 'text/html' #xhtml+xml'
MC_VIEW_KEY = 'view.%s'

def guess_autoescape(template_name):
    '''
    So jinja can figure out whether to auto-escape everything by default.
    See: http://jinja.pocoo.org/docs/api/#autoescaping
    '''
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')


def parse_dttm(date_str, time_str, tz='UTC'):
    '''
    returns a datetime instance from a date/time string 
    that would be sent in a form
    '''
    datetime.datetime.strptime(
                    '%s %s %s' % ( date_str, time_str, tz ),
                    "%m/%d/%Y %I:%M %p %Z" )


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try: # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally: # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session(backend='memcache')


    def handle_exception(self, exception, debug_mode):
        self.unexpected_error(exception,debug_mode)


    @webapp2.cached_property
    def jinja2(self):
        '''
        Returns a Jinja2 renderer cached in the app registry.
        Taken from http://webapp-improved.appspot.com/_modules/webapp2_extras/jinja2.html#Jinja2
        since the get_jinja2 factory doesn't allow passing a config dict.
        '''
        app = self.app or webapp2.get_app()
        key = 'webapp2_extras.jinja2.Jinja2'
        jinja = app.registry.get(key)
        if not jinja:
            jinja = app.registry[key] = jinja_helper.Jinja2(app)
            jinja.environment.filters['urlencode']= utils.urlencode
            jinja.environment.tests['mobile'] = utils.is_mobile

        return jinja


    def flush_view_cache(self,uri):
        memcache.delete(MC_VIEW_KEY % uri)


    def render( self, template=None, params={}, 
            content_type=None, 
            cache_key=None, cache_time=0 ):

        if not template:
            template = type(self).__name__.partition('Handler')[0].lower()
        
        if template.split('/')[-1].find('.') < 0:
            template += '.html'  # TODO add extension based on content-type
        
        # TODO cache by default based on URI
        data = memcache.get( cache_key ) if cache_key else None

        params['gae_users'] = users
        params['request_uri'] = self.request.uri
            
        if data is None:
            try:
                data = self.jinja2.render_template(template, **params)
                logging.debug("Template cache miss: %s",template)
            except jinja2.TemplateNotFound:
                logging.debug("Not found: %s", template)
                self.error(404)
                data = self.jinja2.render_template('notfound.html')
            except Exception as ex:
                if config.DEBUG: raise
                logging.exception("Template render error: %s",ex)
                self.error(500)
                data = self.jinja2.render_template('error.html')
                # TODO short or no cache time?

            if cache_key and not config.DEBUG: memcache.add( cache_key, data, 
                    time=(cache_time or config.APP['cache_time']) )

        self.response.headers['content-type'] = content_type or DEFAULT_CONTENT_TYPE
        self.response.write( data )


    def render_json(self,content):
        def _json_default(obj):
            '''Render model types as JSON'''
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            if isinstance(obj, users.User):
                return obj.email()  # TODO security risk?

            raise TypeError, "Don't know how to serialize %r of type %s" % (obj, type(obj))

        self.response.headers['content-type'] = 'application/json'
        content = json.dumps( content, 
                separators=(',',':'), 
                default=_json_default )
        logging.debug("JSON >> %s", content)
        self.response.out.write(content)


    def unexpected_error(self,err,debug_mode=False):
        logging.exception(err)
        self.error(500)
        if self.is_ajax():
            self.response.headers['content-type'] = 'application/json'
            self.response.out.write(json.dumps( {"msg":"Unexpected error: %s"%err} ))
            return
        elif debug_mode: #print stacktrace
            webapp2.RequestHandler.handle_exception(self, err, debug_mode)
            return
        self.render( 'error', {'msg':str(err)} )


    def unauthorized(self, msg="Unauthorized!"):
        self.error(401)
        response_data = {"msg": msg}
        # TODO cache key based on session & URI
        if self.is_ajax():
            self.render_json(response_data)
            return
        self.render('unauthorized', params=response_data, cache_time=1)


    def notfound(self, msg="Not found!"):
        self.error(404)
        response_data = {"msg": msg}
        if self.is_ajax():
            self.render_json(response_data)
            return

        self.render('notfound', params=response_data, 
                cache_key=MC_VIEW_KEY % self.request.url)


    def is_ajax(self):
        return self.request.headers.get('X-Requested-With',None) == 'XMLHttpRequest'



class CatchAllHandler(BaseHandler):
    '''
    Handler for mostly non-dynamic pages that don't require a 
    special handler.  Path is used to look up a template and
    render it.
    '''
    def get(self,path):
        if path in (None, '', '/'): path = 'index'
        logging.debug("CatchAllHandler: %s", path)
        # TODO check to make sure it's not a template for another handler.
        self.render( path )


    def render( self, path, params={} ):
        cache_key = None if self.request.get('nocache',None) else \
                MC_VIEW_KEY % self.request.url 
        BaseHandler.render(self, path, cache_key=cache_key)



class LogoutHandler(BaseHandler):
    def get(self,redir='/'):
        self.session.clear()
        self.redirect(users.create_logout_url(redir))


