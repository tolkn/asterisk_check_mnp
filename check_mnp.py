#!/usr/bin/python
# coding: utf8

import websocket
import thread
import time
import json
import sys, os
import daemon
import daemon.pidfile
import logging
import ConfigParser

from mnp import *
from AsteriskRESTActions import asteriskRESTActions
from daemon import runner
from translit import transliterate

logDir = "/var/log/check_mnp"
logFormat = "[%(asctime)s] %(levelname)s {%(filename)s:%(lineno)d} - %(message)s"
logLevel = logging.DEBUG

class daemonApp:
	stdin_path = '/dev/null'
	stdout_path = '/dev/tty'
	stderr_path = '/dev/tty'
	pidfile_path =  '/var/run/check_mnp.pid'
	pidfile_timeout = 5	
	

class check_mnp(daemonApp):

	ws = None
	mode = 0
	config = None
	check_mnp = None

	def on_message(self, ws, message):
		msg = json.loads(message)
		if msg['type'] == 'StasisStart':
			logging.debug( u"type={0}:channel_id={1}:caller_id={2}:caller_name={3}:target_number={4}".format(msg['type'], msg['channel']['id'], msg['channel']['caller']['number'], msg['channel']['caller']['name'], msg['channel']['dialplan']['exten']))
									
			number = msg['channel']['caller']['number']
			numberLen = len(number)
			if numberLen > 10:
				number = number[numberLen-10:] #Find by last 10 digit
			
			if len(number) == 10:
				logging.debug( u"Определяем направление для:{0}:{1}".format(number, msg['channel']['id']) )
				self.mnp.get_info(number, msg['channel']['id'])
			else
				logging.debug( "Set dialplan continue " )	
				self.asteriskAction.set_continue(msg['channel']['id'])
		
		elif msg['type'] == 'ChannelCallerId':
			logging.debug( u"type={0}:channel_id={1}:caller_id={2}:caller_name={3}:target_number={4}".format(msg['type'], msg['channel']['id'], msg['channel']['caller']['number'], msg['channel']['caller']['name'], msg['channel']['dialplan']['exten']))
		else:
			logging.debug( u"type={0}:channel_id={1}:caller_id={2}:caller_name={3}:target_number={4}".format(msg['type'], msg['channel']['id'], msg['channel']['caller']['number'], msg['channel']['caller']['name'], msg['channel']['dialplan']['exten']))
		

	def on_error(self, ws, error):
		logging.error( "### error ###:{0}".format(error) )

	def on_close(self, ws):
		logging.debug( "### closed ###" )

	def on_open(self, ws):
		logging.debug( "### open ###" )
		
	def run(self):
		

		if self.ws is None:
			ari_url   = self.config.get('default', 'ari_url')
			ari_login = self.config.get('default', 'ari_login')
			ari_pass = self.config.get('default', 'ari_pass')
			
			
			if self.mode == 1:
				websocket.enableTrace(True)
				
			try:
			
				self.ws = websocket.WebSocketApp("ws://{0}/ari/events?api_key={1}:{2}&app=check_mnp".format(ari_url, ari_login, ari_pass),
									  on_message = self.on_message,
									  on_error = self.on_error,
									  on_close = self.on_close)

				self.ws.on_close = self.on_close

				logging.info( "Service start " )
				logging.info( "-=============================================================================================-" )
				
				
				self.ws.run_forever()
			
			except:
				logging.debug( 'Erorr websocket:' )
			finally:
				if self.ws is not None:
					logging.debug( "Socket close" )
					self.ws.close()
					self.ws = None

	
	
	def __init__(self, config=None, action=None):
	
		self.mnp = mnp.nmp_info( action )
		self.asteriskAction = action
				
		if config is not None:
			self.config = config
			
			
					
		
	def __enter__(self):
		return self
	

	def __exit__(self, exc_type, exc_value, traceback):
		logging.debug( "Service exit " )
		
	def __del__(self):
		
		if self.asteriskAction <> None:
			del self.asteriskAction
			self.asteriskAction = None
		
			if self.ws is not None:
				logging.debug( "Socket close" )
				self.ws.close()
				del self.ws
				self.ws = None
			logging.info( "-=============================================================================================-" )
			logging.info( "Service destruct" )


if __name__ == "__main__":
	
	config = ConfigParser.RawConfigParser()
	config.read(os.path.dirname(__file__)+'/check_mnp.config')
	
	if	config.get('default', 'log_level') == 'INFO':
		logLevel = logging.INFO
		
	
	if len(sys.argv) > 1:
	
		if not os.path.exists(logDir):
			os.makedirs(logDir)

		handler = logging.FileHandler(logDir+'/message.log', "a", encoding = "UTF-8")
		formatter = logging.Formatter(logFormat)
		handler.setFormatter(formatter)
		root_logger = logging.getLogger()
		root_logger.addHandler(handler)
		root_logger.setLevel(logLevel)
	
		if sys.argv[1] == 'start':
					
			action = asteriskRESTActions(config)
			with check_mnp(config, action) as instance:
				daemon_runner = runner.DaemonRunner(instance)
				daemon_runner.daemon_context.files_preserve=[handler.stream]
				daemon_runner.do_action()
				
		elif sys.argv[1] == 'stop':
	
			instance = daemonApp()
			daemon_runner = runner.DaemonRunner(instance)
			daemon_runner.daemon_context.files_preserve=[handler.stream]
			daemon_runner.do_action()


	else:
		logging.basicConfig(format = logFormat, level = logLevel)
		action = asteriskRESTActions(config)
		with check_mnp(config, action) as instance:
			instance.mode = 1
			instance.run()


