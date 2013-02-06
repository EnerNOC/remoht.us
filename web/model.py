# Copyright (c) 2011 Thom Nichols

from google.appengine.ext import ndb
from google.appengine.api import users, memcache

CACHE_RESOURCE_KEY = "full-resource.%s/%s"

class XMPPUser(ndb.Model):
    user = ndb.UserProperty(required=True)
    jid = ndb.StringProperty(required=True) # TODO validate JID format
    resources = ndb.JsonProperty(default=dict()) # dict of {resource:presence} pairs

    @classmethod
    def new(cls):
        user = users.get_current_user()
        return XMPPUser(user=user, jid=user.email())

    @classmethod
    def get_current_user(cls):
        return cls.query(cls.user == users.get_current_user()).get()

    @classmethod
    def get_by_jid(cls,jid):
        return cls.query(cls.jid == jid).get()


def cache_full_resource(jid, short_resource, full_resource):
        memcache.set( CACHE_RESOURCE_KEY % (jid, short_resource), full_resource )

def get_full_resource(jid, short_resource):
        return memcache.get( CACHE_RESOURCE_KEY % (jid, short_resource) ) or short_resource




class Device(ndb.Model):
    owner = ndb.UserProperty(required=True)
    jid = ndb.StringProperty(required=True) # TODO validate JID format
    resource = ndb.StringProperty(required=True)
    presence = ndb.StringProperty(default='available')
    relays = ndb.JsonProperty(default=dict())  # dict of {relay_name:state} items
    id = ndb.ComputedProperty( lambda self: self.key.id() if self.key else None )
    
    @property
    def full_jid(self):
        return '%s/%s' % (self.jid, self.full_resource)


    @property
    def full_resource(self):
        result = memcache.get( CACHE_RESOURCE_KEY % (self.jid, self.resource) )
        return result or self.resource

    @classmethod
    def from_resource(cls,resource,jid=None):
        if jid is None:
            q = cls.query( cls.resource == resource,
                    cls.owner == users.get_current_user() )
        else:
            q = cls.query( cls.resource == resource,
                    cls.jid == jid )

        return q.get()

    @classmethod
    def all_by_jid(cls, jid):
        return cls.query( cls.jid == jid ).fetch()

    @classmethod
    def all_by_user(cls):
        return cls.query( cls.owner == users.get_current_user() ).fetch()

    @classmethod
    def all(cls,limit=20,offset=None):
        return cls.query(
                cls.owner == users.get_current_user()
                ).fetch(limit=limit,offset=offset)


class Reading(ndb.Model):
    source = ndb.StringProperty(required=True)
    data_type = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    values = ndb.FloatProperty(repeated=True,indexed=False)
    timestamps = ndb.DateTimeProperty(repeated=True,indexed=False)
