import urllib, urllib2, json

BASE_URL = 'http://localhost:8080/_ah/xmpp/'
CHAT_URL = BASE_URL + 'presence/available/'

TO_JID = 'rehmote@appspot.com'
FROM_JID = 'test@example.com/test_2:asdf2134'

def send_presence():

    urllib2.urlopen( CHAT_URL, 
            urllib.urlencode((
                ('to', TO_JID),
                ('from',FROM_JID),
                ('stanza','')
                ))
            )


def main():
    send_presence()


if __name__ == '__main__': main()
