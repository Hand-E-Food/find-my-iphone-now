import json
import requests
import sys


class InvalidStateError(Exception):
	"""The object is in an invalid state to perform the operation."""


class FindMyIphone:
	def __init__(self):
		self.headers = {
			'User-Agent': 'FindMyiPhone/472.1 CFNetwork/711.1.12 Darwin/14.0.0',
			'X-Apple-Realm-Support': '1.0',
			'X-Apple-Find-API-Ver': '3.0',
			'X-Apple-AuthScheme': 'UserIdGuest'
		}
		self.signed_in = False
	
	
	def sign_in(self, username, password):
		try:
			self.auth = requests.auth.HTTPBasicAuth(username, password)
			self.username = username
			self.base_url = 'https://fmipmobile.icloud.com/fmipservice/device/{0}/'.format(username)
			
			response = self._get(self.base_url + 'initClient')
			if response.status_code >= 400:
				response.raise_for_status()
			
			if all (key in response.headers for key in ('X-Apple-MMe-Host', 'X-Apple-MMe-Scope')):
				self.base_url = 'https://{0}/fmipservice/device/{1}/'.format(response.headers['X-Apple-MMe-Host'], response.headers['X-Apple-MMe-Scope'])
			
			self.signed_in = True
		
		except:
			self.sign_out()
			raise
	
	
	def sign_out(self):
		self.signed_in = False
		self.base_url = None
		self.username = None
		self.auth = None
		self.devices = None
	
	
	def init_devices(self):
		self._raise_if_not_signed_in()
		response = self._post(self.base_url + 'initClient')
		if response.status_code >= 300:
			response.raise_for_status()
		
		self._load_devices(response)
	
	
	def refresh_devices(self, id = None):
		self._raise_if_not_signed_in()
		
		response = self._post(self.base_url + 'refreshClient', None if id == None else {
			'appVersion': '4.0',
			'shouldLocate': True,
			'selectedDevice': id,
			'fmly': True,
		})
		if response.status_code >= 300:
			response.raise_for_status()
		
		self._load_devices(response)
	
	
	def play_sound(self, id, message):
		self._raise_if_not_signed_in()
		response = self._post(self.base_url + 'playSound', {
			'device': id,
			'subject': message,
		})
		if response.status_code >= 300:
			response.raise_for_status()
	
	
	def activate_lost_mode(self, id, message, phoneNumber = ''):
		self._raise_if_not_signed_in()
		response = self._post(self.base_url + 'lostDevice', {
			'device': id,
			'ownerNbr': phoneNumber,
			'text': message,
			'lostModeEnabled': True,
		})
		if response.status_code >= 300:
			response.raise_for_status()
	
	
	def _get(self, url):
		response = requests.get(
			url,
			headers = self.headers,
			auth = self.auth,
			verify = True
		)
		return response
	
	
	def _post(self, url, data = None):
		response = requests.post(
			url,
			headers = self.headers,
			auth = self.auth,
			verify = True,
			data = None if data == None else json.dumps(data)
		)
		return response
	
	
	def _raise_if_not_signed_in(self):
		if self.signed_in == False:
			raise InvalidStateError
	
	
	def _load_devices(self, response):
		self.devices = json.loads(response.text)['content']
