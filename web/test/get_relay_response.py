import urllib, urllib2, json

BASE_URL = 'http://localhost:8080/_ah/xmpp/'
CHAT_URL = BASE_URL + 'message/chat/'

TO_JID = 'rehmote@appspot.com'
FROM_JID = 'test@example.com/test_1'

def get_relay_response():
    response = {
            "cmd": "get_relays",
            "data": {
                    "relays": {"relay_1": 0, "relay_2": 1}
                }
            }


    urllib2.urlopen( CHAT_URL, 
            urllib.urlencode((
                ('type','chat'),
                ('to', TO_JID),
                ('id', "asdf"),
                ('from',FROM_JID),
                ('body', json.dumps(response)),
                ('stanza','')
                ))
            )


def main():
    get_relay_response()


if __name__ == '__main__': main()
