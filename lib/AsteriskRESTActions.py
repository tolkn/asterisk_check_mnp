#!/usr/bin/python

import urllib, urllib2, base64, logging, ConfigParser, os


class asteriskRESTActions:

	url = 'http://{0}/ari/channels/{1}/{2}'
	headers = { 'ContentType' : "application/json" }

	def ari_channel_action(self, channel_id, action, data=''):
			
		try:
		
			url = self.url.format(channel_id, action)	
			req = urllib2.Request(url, data, self.headers)
			
			response = urllib2.urlopen(req)
			
			logging.debug("REST Action done:{0}".format(action))
		except urllib2.HTTPError as e:
			logging.error('ARI HTTPerror')
			logging.error( 'ARI service error code:{0}\n{1}'.format(e.code, e.fp.read()) )
			
		except  urllib2.URLError as e:
			logging.error('ARI URLerror')
			logging.error( "Error ari action. With code {0}. \n{1}".format(e.code, e.reason) )
			
	def __init__(self, config):
		ari_url   = config.get('default', 'ari_url')
		ari_login = config.get('default', 'ari_login')
		ari_pass  = config.get('default', 'ari_pass')
		
		self.url = self.url.format(ari_url, '{0}', '{1}')
		
		base64string = base64.encodestring('%s:%s' % (ari_login, ari_pass)).replace('\n', '')
		self.headers["Authorization"] = "Basic %s" % base64string

	
	def set_channel_caller_name(self, channel_id, name):
		
		postData = "variable=CALLERID(name)&value={0}".format(urllib.quote_plus(name)) 
		self.ari_channel_action(channel_id, 'variable', postData)
	
	
	def set_continue(self, channel_id):
		self.ari_channel_action(channel_id, 'continue')
		
	def set_channel_operator(self, channel_id, oid):
		postData = "variable=operator&value={0}".format(oid) 
		self.ari_channel_action(channel_id, 'variable', postData)
		
	def set_channel_region(self, channel_id, rid):
		postData = "variable=region&value={0}".format(rid) 
		self.ari_channel_action(channel_id, 'variable', postData)
		
	

if __name__ == "__main__":

	os.chdir(os.path.dirname(__file__))
	os.chdir('..')

	config = ConfigParser.RawConfigParser()
	config.read(os.getcwd()+'/CallerNameResolver.config')
	
	act = asteriskRESTActions(config)

	act.set_continue('1447506846.22')
	act.set_channel_caller_name('1447506846.22', 'test')