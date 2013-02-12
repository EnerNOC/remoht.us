import urllib, urllib2, json, argparse

BASE_URL = 'http://localhost:8080/_ah/xmpp/'
CHAT_URL = BASE_URL + 'presence/%s/'

TO_JID = 'rehmote@appspot.com'
FROM_JID = 'test@example.com/%s:asdf2134'

def send_presence(status='available',resource='test_2'):

    urllib2.urlopen( CHAT_URL % status, 
            urllib.urlencode((
                ('to', TO_JID),
                ('from',FROM_JID % resource),
                ('stanza','')
                ))
            )


def main():
    parser = argparse.ArgumentParser(description='Simulate XMPP responses')
    parser.add_argument('--status', dest='status', default='available',
            type=str, help='Presence')
    parser.add_argument('--resource', dest='resource', default='test_2',
            type=str, help='Resource')

    args = parser.parse_args()
    send_presence(args.status,args.resource)


if __name__ == '__main__': main()
