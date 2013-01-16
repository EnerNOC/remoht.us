import sys
import logging
import signal
import functools
import threading
import json
from argparse import ArgumentParser

import arduino, xmpp


# Defaults:
# Add a colon ':' to the end of the resource in order to make it easy to 
# parse off the hash that Google Talk tacks on the end of JID resources
USER = 'tmnichols@gmail.com/pi:'
PASS = ''
DOMAIN = 'talk.google.com'
PORT = 5222
REMOHT_SERVICE = 'xmpp@remohte.appspotchat.com'
READING_FREQ = 15 # seconds

TTY='/dev/ttyUSB0'
BAUD=9600

CMD_RELAY = 'r'
CMD_READING = 'd'

class RemohtPi(object):

    def __init__(self, jid, pwd, domain=DOMAIN, port=PORT, tty=TTY, baud=BAUD):
        self.op_map = {
            "get_relays" : self.get_relays,
            "toggle_relay" : self.toggle_relay,
            "get_readings" : self.get_readings 
            }

        self.xmpp = xmpp.RemohtXMPP( jid, pwd, op_map=self.op_map )
        self.connect_props = (domain,port)

        self.xmpp.add_task( READING_FREQ, self.data_collector_task, 
                repeat=True, name='Reading collector' )

        self.serial = arduino.ArduinoSerial( tty, baud )
        self.serial.add_callback( self.serial_callback )

        self.exit = threading.Event()


    def start(self):
        self.exit.clear()
        self.serial.start()

        if self.xmpp.connect(self.connect_props):
            logging.info('Running!')
            self.xmpp.process(block=False)
        else:
            logging.warn("XMPP connection failure!")


    def stop(self):
        logging.info("Closing serial connection...")
        self.serial.stop()
        self.xmpp.disconnect( wait=False )
        self.exit.set()


    def serial_callback(self,data):
        cmd = data[0]

        if cmd == CMD_READING: # data, format should be ... d temp_c light_pct pir_0_or_1
            cmd = "readings"
            data = {
                "temp_c"    : float(data[1]),
                "light_pct" : float(data[2]),
                "pir"       : bool(int(data[3])) }
            pass
        elif cmd == CMD_RELAY: # relay states, format should be r 0 1
            cmd = "get_relays"
            data = {
                "relay_1" : int(data[1]),
                "relay_2" : int(data[2]) }
        else:
            logging.warn("Unknown command: %s", data)
            return

        self.send_xmpp( cmd, data )

        
    def get_relays(self,relay_id=None):
        self.serial.send(CMD_RELAY) # get relays
#        self.send_xmpp("get_relays", {"


    def toggle_relay(self,relay_id=0,state=0):
        relay_id = 1 if relay_id=='relay_1' else 0
        self.serial.send('%s %d %d' % (CMD_RELAY, relay_id, state))


    def get_readings(self):
        self.serial.send(CMD_READING) # data request


    def data_collector_task(self):
        # TODO ideally the arduino could push periodic data or 
        # on delta rather than polling
        self.serial.send(CMD_READING)


    def send_xmpp(self,cmd,data):
        payload = {"cmd":cmd, "data": data}
        self.xmpp.send_message( mto = REMOHT_SERVICE,
                          mbody = json.dumps(payload),
                          mtype = 'chat')




def main(opts):
    remoht = RemohtPi( opts.jid, opts.passwd, 
                       opts.domain, opts.port, 
                       opts.tty, opts.baud )

    for s in 'SIGINT SIGHUP SIGQUIT SIGTERM'.split():
        signal.signal(getattr(signal,s), lambda sig,frame: remoht.stop())

    remoht.start()
    while not remoht.exit.is_set(): remoht.exit.wait(5)


if __name__ == '__main__':
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(levelname)-8s %(message)s' )

    optp = ArgumentParser()
    optp.add_argument("-p", "--pass", dest="passwd",
            default=PASS, help="XMPP password")

    optp.add_argument("-j", "--jid", dest="jid",
            default=USER, help="XMPP JID")

    optp.add_argument("-D", "--domain", dest="domain",
            default=DOMAIN, help="XMPP domain")

    optp.add_argument("-P", "--port", dest="port", type=int,
            default=PORT, help="XMPP server port")

    optp.add_argument("-t", "--tty", dest="tty",
            default=TTY, help="Arduino serial tty")

    optp.add_argument("-b", "--baud", dest="baud", type=int,
            default=BAUD, help="Arduino serial baud")

    args = optp.parse_args()

    if args.passwd in (None,''):
        optp.print_help()
        sys.exit(1)

    main( args )
