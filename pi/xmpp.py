import logging
import sleekxmpp
import json

class RemohtXMPP(sleekxmpp.ClientXMPP):

    def __init__( self, *args, **kwargs ):
        self.op_map = kwargs.get('op_map',{})
        del kwargs['op_map']

        sleekxmpp.ClientXMPP.__init__(self, *args, **kwargs )

        self.add_event_handler( "session_start", self.on_start )
        self.add_event_handler( "message", self.on_message )


    def on_start(self,evt):
        self.send_presence()
#        self.get_roster()


    def on_message(self,msg):
        logging.debug("[%s] << %s", msg['from'], msg['body'])
        try:
            parsed = json.loads( msg['body'] )
        except Exception as ex:
            logging.warn("Can't parse message %r", msg['body'])

        cmd = parsed.get('cmd',None)
        result = {"msg":"OK","status":0}
        if cmd is None:
            result = {"msg":"Error: no 'cmd'", 'status':1}
            msg.reply( json.dumps(result) ).send()
            return 

        op = self.op_map.get(cmd,None)
        if op is None:
            logging.warn( "Unknown command: %s", cmd )
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


    def add_task(self, freq, task, repeat=False, name=None):
        if name == None: name= str(task)
        self.schedule( name, freq, task, repeat=repeat )
