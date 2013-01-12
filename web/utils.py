import urlparse, urllib
import webapp2

def urlencode(uri):
    '''
    Jinja template filter.  See:
    https://github.com/mitsuhiko/jinja2/issues/17
    '''
    return urllib.quote(uri,safe='')
#    return urllib.urlencode( uri_part )
#    parts = list(urlparse.urlparse(uri))
#    q = urlparse.parse_qs(parts[4])
#    q.update(query)
#    parts[4] = urllib.urlencode(q)
#    return urlparse.urlunparse(parts)


def is_mobile(_):
    '''
    Custom jinja2 test.  Use like this:
    {% if _ is mobile %}  (it expects some variable...
    '''
    req = webapp2.get_request()
#    logging.debug( "UA ----------- %s", handler.request.user_agent )
    for ua in ('iPhone','Android','iPod','iPad','BlackBerry','webOS','IEMobile'):
        try: 
            if req.user_agent.index(ua) >= 0: return True
        except ValueError: pass # substring not found, continue
    return False
