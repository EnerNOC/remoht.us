import sys
import logging
import signal
import json
import functools
import sleekxmpp
from argparse import ArgumentParser


# Defaults:
USER = 'tmnichols@gmail.com/pi'
PASS = ''
DOMAIN = 'talk.google.com'
PORT = 5222
REMOHT_SERVICE = 'xmpp@remohte.appspotchat.com'
READING_FREQ = 30 # seconds

RELAYS = {
        "relay_1" : 1,
        "relay_2" : 0 }

READINGS = {
        "temp_c" : 34.5,
        "light" : 255,
        "pir" : 1 }


def get_relays():
    return RELAYS


def toggle_relay(relay_id,val=0):
    RELAYS[relay_id] = val
    return {"result": val}


def get_readings():
    return READINGS


OP_MAP = {
        "get_relays" : get_relays,
        "toggle_relay" : toggle_relay,
        "get_readings" : get_readings 
        }


class RemohtXMPP(sleekxmpp.ClientXMPP):

    def __init__( self, *args, **kwargs ):
        sleekxmpp.ClientXMPP.__init__(self, *args, **kwargs )

        self.add_event_handler( "session_start", self.on_start )
        self.add_event_handler( "message", self.on_message )


    def on_start(self,evt):
        self.send_presence()
#        self.get_roster()


    def on_message(self,msg):
        logging.debug("[%(from)s] << %(body)s", msg)
        parsed = json.loads( msg['body'] )

        cmd = parsed.get('cmd',None)
        result = {"msg":"OK",status:0}
        if cmd is None:
            result = {"msg":"Error: no 'cmd'", 'status':1}
            msg.reply( json.dumps(result) ).send()
            return 

        op = OP_MAP.get(cmd,None)
        if op is None:
            result = {"msg":"Error: unknown command: %s" % cmd, 'status':1}
            msg.reply( json.dumps(result) ).send()
            return 

        params = parsed.get('params',None)
        try:
            result_data = op(**params) if params else op()
            result['data'] = result_data
        except Exception as ex:
            logging.exception("Error executing op %s : %s", op, ex)
            result["msg"] = "Unexpected error: %s" % ex
            result["status"] = 2

        msg.reply( json.dumps(result) ).send()
        

    def send_readings(self,readings):
        payload = {"cmd":"readings", vals: readings}
        self.send_message( mto = REMOHT_SERVICE,
                          mbody = json.dumps(payload),
                          mtype = 'chat')
        

    def data_collector_task(self):
        pass

    def start_data_collector(self):
         self.schedule( 'Reading task',
              READING_FREQ, scheduled_ping,
              repeat=True )


def main(opts):
    xmpp = RemohtXMPP( opts.jid, opts.passwd )
    xmpp.start_data_collector()

    for s in 'SIGINT SIGHUP SIGQUIT SIGTERM'.split():
        signal.signal(getattr(signal,s), functools.partial(shutdown,xmpp))

    if xmpp.connect((opts.domain,opts.port)):
        logging.info('Running!')
        xmpp.process(block=True)


def shutdown(xmpp,sig,frame):
    logging.info("Quitting...")
    xmpp.disconnect(wait=False)


if __name__ == '__main__':
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(levelname)-8s %(message)s' )

    optp = ArgumentParser()
    optp.add_argument("-p", "--password", dest="passwd",
            default=PASS, help="XMPP password")

    optp.add_argument("-j", "--jid", dest="jid",
            default=USER, help="XMPP JID")

    optp.add_argument("-D", "--domain", dest="domain",
            default=DOMAIN,help="XMPP domain")

    optp.add_argument("-P", "--port", dest="port", type=int,
            default=PORT,help="XMPP server port")

    args = optp.parse_args()

    if args.passwd in (None,''):
        optp.print_help()
        sys.exit(1)

    main( args )
