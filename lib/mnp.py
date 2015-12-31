#!/usr/bin/python
# -*- coding: utf-8 -*-

import json, logging, datetime, sys, urllib2
import multiprocessing as mp
import time

from AsteriskRESTActions import asteriskRESTActions
	
class mnp_provider:
	src = ''
	url = None
	
	
	def get_info(self, number, channel_id):
		info = self.get_new_info(number)
		info_str = {}
		info_str['info'] = info
		info_str['number'] = number
		info_str['src'] = self.src
		info_str['channel'] = channel_id
		return info_str
		
	def get_new_info(self, number):
		try:
			
			req = urllib2.Request(self.url.format(number))
			logging.error( u'url {0}'.format(self.url.format(number)) )
			response = urllib2.urlopen(req)
			return response.read()
		except urllib2.HTTPError as e:
			logging.error( 'MNP error code:{0}\n'.format(e.code) )
		except urllib2.URLError as e:
			logging.error( "Error get mnp data. With code {0}. \n{1}".format(e.code, e.reason) )
		except:
			logging.error( 'Erorr requesting mnp data:{0}'.format(sys.exc_info()[0]) )
		
		return None
	
	def __init__(self):
		self.url = None

class megafon_mnp(mnp_provider):
	def __init__(self):
		mnp_provider.__init__(self)
		self.src = 'mf'
		self.url = "http://moscow.shop.megafon.ru/get_ajax_page.php?msisdn={0}&action=getMsisdnInfo"
		
	
	def get_new_info(self, number):
		info = None
		mnp = json.loads(mnp_provider.get_new_info(self, number).decode('windows-1251'))
		if mnp != None:
			info = {}
			info['oid'] =  mnp.get('operator_id')
			info['rid'] =  mnp.get('region_id')
	
		return info
	
class tele2_mnp(mnp_provider):
	def __init__(self):
		mnp_provider.__init__(self)
		self.src = 'tl'
		self.url = "http://mnp.tele2.ru/gateway.php?{0}"
	
	def get_new_info(self, number):
		info = None
		mnp = json.loads(mnp_provider.get_new_info(self, number).decode('utf-8'))
		if mnp != None:
			res = mnp.get('response')
			info = {}
			
			info['oid'] =  int(res.get('mnc').get('code').encode('utf-8'))
			info['rid'] =  int(res.get('geocode').get('code').encode('utf-8'))
	
		return info

		
class nmp_info:
	buffer = {}
	bufferExpireMins = 43200 #30 дней
	providers = []
	action = None
	
	def set_channel_info(self, channel_id, info):
		if (self.action <> None):
			self.action.set_channel_operator(channel_id, info.get('oid'))
			self.action.set_channel_region(channel_id, info.get('rid'))
			self.action.set_continue(channel_id)
	
	def get_info(self, number, channel_id):
		type = ''
		info = {}
		infoBuff = nmp_info.buffer.get(number)
		if infoBuff is not None:
			logging.debug( 'Mnp info found in buffer' )
			if (datetime.datetime.now()  <= infoBuff.get('exp')):
				info = infoBuff.get('info')
				set_channel_info(channel_id, info)
					
		if info == {}:
			self.get_new_info(number, channel_id)
			
		return info
	
	def get_new_info(self, number, channel_id):
		pool = mp.Pool()
		
		for p in self.providers:
			pool.apply_async(get_provider_info, args = (p, number, channel_id ), callback = get_provider_info_callback)
#		pool.close()
	
			
	def __init__(self, action=None):
		self.providers.append(tele2_mnp())
		self.providers.append(megafon_mnp())
		self.action = action
	

def get_provider_info(provider, number, channel_id):
	return provider.get_info(number, channel_id)

def get_provider_info_callback(info_str):
#	print info_str
	
	if info_str.get('info') <> None:
		nmp_info.set_channel_info(info_str.get('channel'), info_str.get('info'))
		if nmp_info.bufferExpireMins > 0:
			logging.debug( 'Mnp info save to buffer' )
			if nmp_info.buffer.get(info_str.get('number')) == None:
				nmp_info.buffer[info_str.get('number')] = {}
			nmp_info.buffer[info_str.get('number')]['info'] = info_str.get('info')
			nmp_info.buffer[info_str.get('number')]['exp'] = datetime.datetime.now() + datetime.timedelta(minutes = nmp_info.bufferExpireMins)
			
		
		
	print '--> {0}-{1}-{2}'.format(info_str.get('info'), info_str.get('number'), info_str.get('src'))
	
		
if __name__ == "__main__":
	
	
	info = nmp_info()
	
	info.get_info('555555555555555555', '000')
	time.sleep(5)
	
	
	
	
	
