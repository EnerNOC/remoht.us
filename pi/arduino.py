import sys, os, time, serial, logging, threading

DEFAULT_TTY = '/dev/ttyUSB0'
DEFAULT_BAUD = 9600
TIMEOUT = 3.0

log = logging.getLogger(__name__)

class ArduinoSerial(object):

    def __init__(self,tty=DEFAULT_TTY,baud=DEFAULT_BAUD):
        self._exit = threading.Event()
        self.tty = tty
        self.baud = baud
        self.serial = None # created @ beginning of `run`
        self.callbacks = []
        self._thread = None


    def start(self):
        '''
        Calls `self.run()` in a daemon thread.
        '''
        if self._thread is not None:
            raise Exception('ArduinoSerial is already started!')
        self._exit.clear()
        self._thread = threading.Thread(
                target=self.run, 
                name='ArduinoSerial @ %s' % self.tty)
        self._thread.daemon = True
        self._thread.start()


    def stop(self):
        '''
        Tell the thread to exit, and wait a moment to 
        give the thread a chance to terminate
        '''
        self._exit.set()
        if self._thread: self._thread.join(3)
        self._exit.clear()
        self._thread = None


    def run(self):
        '''
        Listen on the serial channel and pass any valid data to the callbacks
        '''
        while not self._exit.is_set():
            line = None
            try:
                if self.serial is None:
                    # allows the code to recover/ initialize if the USB device 
                    # is unplugged after this code is running:
                    if not os.path.exists( self.tty ):
                        log.debug('TTY %s does not exist; Arduino is probably not plugged in...', self.tty)
                        self._exit.wait(10) # wait before retry
                        continue

                    self.serial = serial.Serial( 
                            port=self.tty, 
                            baudrate=self.baud, 
                            timeout=TIMEOUT )
                    log.info("Opened serial port at %s", self.tty)

                line = self.serial.readline()
                if line: logging.debug("Arduino >> %s", line)
                message = _parse( line )
                if not message: continue

                log.debug( "Parsed message to %s",message )
                for cb in self.callbacks:
                    try: cb( message )
                    except: 
                        log.exception(
                            "Callback threw exception for message: %s", 
                            message )

            except serial.SerialException as ex:
                log.exception("Serial error: %s",ex)
                if self.serial is not None:
                    # allow the serial to re-initialize
                    try: self.serial.close()
                    except: pass
                    self.serial = None
                self._exit.wait(10) # sleep to avoid tight loop

            except Exception, msg:
                log.exception("Unexpected read error: %s for line: %s",msg,line)
                self._exit.wait(1)


    def add_callback(self,cb):
        '''
        Add a callback which will be fired for each valid message 
        received from the serial channel
        '''
        self.callbacks.append(cb)


    def send(self,cmd):
        '''
        Send a command to the Arduino
        '''
        logging.debug("Arduino << %s", cmd)
        if not self.serial:
            logging.warn("Serial not open! Dropped message %r", cmd)
            return

        self.serial.write(cmd+ "\n")


def _parse(line):
    '''
    Parse the command into its parts
    '''
    if not line: return 
    return line.split()


if __name__ == '__main__':
    # This is just test code to verify we can read data from the USB device.
    logging.basicConfig(level=logging.DEBUG)
    from optparse import OptionParser

    opts = OptionParser()
    opts.add_option("-t", "--tty", dest="tty",
                  help="TTY port", metavar="TTY")
    (options, args) = opts.parse_args()
    
    log.info("Starting serial on: %s", options.tty)
    channel = ArduinoSerial(options.tty)

    def callback(msg):
        print "Got message: %s" % (msg,)

    channel.add_callback(callback)
    channel.start()

    while 1: time.sleep(1)
    channel.stop()
