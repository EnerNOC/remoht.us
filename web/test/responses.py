import urllib, urllib2, json, argparse

BASE_URL = 'http://localhost:8080/_ah/xmpp/'
CHAT_URL = BASE_URL + 'message/chat/'

TO_JID = 'rehmote@appspot.com'
FROM_JID = 'test@example.com/test_2:asdf2134'

def relay_response(vals=None):
    vals = [0,1] if vals==None else vals.split(' ')
    payload = {
        "cmd": "get_relays",
        "data": {
            "relays": {
                "relay_1": int(vals[0]), 
                "relay_2": int(vals[1])
                }
            }
        }

    _send(payload)


        
def readings_data(vals=None):
    vals = [23.4, 0.77, 0] if vals == None else vals.split(' ')
    payload = {
        "cmd": "readings",
        "data" : {
            "temp_c"    : float(vals[0]),
            "light_pct" : float(vals[1]),
            "pir"       : int(vals[2])
            }
        }

    _send(payload)


def _send(payload):
    urllib2.urlopen( CHAT_URL, 
        urllib.urlencode((
            ('type','chat'),
            ('to', TO_JID),
            ('id', "asdf"),
            ('from',FROM_JID),
            ('body', json.dumps(payload)),
            ('stanza','')
            ))
        )


def main():
    parser = argparse.ArgumentParser(description='Simulate XMPP responses')
    parser.add_argument('op', metavar='O', type=str, help='Operation')
    parser.add_argument('vals', metavar='V', type=str, help='Values')

    args = parser.parse_args()
    if args.op == "relay":
        relay_response(args.vals)
    elif args.op == "readings":
        readings_data(args.vals)


if __name__ == '__main__': main()
