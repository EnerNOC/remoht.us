# Copyright (c) 2011 Thom Nichols

from google.appengine.ext import ndb
from google.appengine.api import users

class Device(ndb.Model):
    owner = ndb.UserProperty(default=users.get_current_user())
    jid = ndb.StringProperty(required=True)
    resources = ndb.JsonProperty(default=dict())    # dict of {resource:presence} items
    relays = ndb.JsonProperty(default=dict())  # dict of {relay_name:state} items
    id = ndb.ComputedProperty( lambda self: self.key.id() if self.key else None )

    @classmethod
    def from_jid(cls, jid, current_user=True):
        if current_user:
            q = cls.query( cls.jid == jid, 
                cls.owner == users.get_current_user() )
        else:
            q = cls.query( cls.jid == jid )
        return q.get()
    
    @classmethod
    def all(cls,limit=20,offset=None):
        return cls.query(
                cls.owner == users.get_current_user()
                ).fetch(limit=limit,offset=offset)

    def add_resource(self,resource,presence='available'):
        self.resources[resource] = presence

    def get_resources(self):
        return self.resources.keys()

    def get_available_resource(self):
        for res,presence in self.resources.iteritems():
            if presence == "available": return res
        return None


class Reading(ndb.Model):
    source = ndb.StringProperty(required=True)
    data_type = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    values = ndb.FloatProperty(repeated=True,indexed=False)
    timestamps = ndb.DateTimeProperty(repeated=True,indexed=False)
