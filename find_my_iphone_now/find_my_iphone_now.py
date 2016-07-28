import config
import datetime
from find_my_iphone import FindMyIphone 
import json
import random
import re
from RPi import GPIO
import sys
from threading import Thread
import time
import traceback


class IphoneUser:
	LED_OFF = 0
	LED_ON  = 1 - LED_OFF
	
	STATE_IDLE = 0
	STATE_RUNNING = 1
	STATE_ERROR = 2

	def __init__(self, user):
		self.running = True
		self.state = self.STATE_IDLE
		self.user = user
		GPIO.setup(
			user['button_pin'],
			GPIO.IN,
			pull_up_down = GPIO.PUD_UP
		)
		GPIO.setup(
			user['led_pin'],
			GPIO.OUT,
			initial = self.LED_OFF
		)
	
	
	def run(self):
		while self.running:
			if self._is_button_pressed(500):
				self.state = self.STATE_RUNNING
				
				log_message("Activated on GPIO{button_pin}!".format(**self.user))
				
				thread = Thread(target = self._find_iphone)
				thread.start()
				while self.state == self.STATE_RUNNING:
					self._set_led(self.LED_ON)
					time.sleep(0.5)
					self._set_led(self.LED_OFF)
					time.sleep(0.5)
				
				if self.state == self.STATE_ERROR:
					self._set_led(self.LED_ON)
					time.sleep(5.0)
					self._set_led(self.LED_OFF)
					self.state = self.STATE_IDLE
	
	
	def stop(self):
		self.running = False
	
	
	def _find_iphone(self):
		try:
			proxy = FindMyIphone()
			log_message('Logging in {username} ...'.format(**self.user))
			proxy.sign_in(
				self.user['username'],
				config.decode(self.user['password'])
			)
			log_message('Requesting sound for {display_name} ...'.format(**self.user))
			proxy.play_sound(self.user['id'], get_random_message())
			log_message('Signing out ...'.format(**self.user))
			proxy.sign_out()
			log_message('Done!')
			self.state = self.STATE_IDLE
		except:
			log_message('ERROR!')
			self.state = self.STATE_ERROR
			log_error()
	
	
	def _is_button_pressed(self, timeout):
		pin = self.user['button_pin']
		
		trigger = datetime.datetime.now() + datetime.timedelta(milliseconds = timeout)
		while not GPIO.input(pin):
			if datetime.datetime.now() >= trigger:
				return False
			time.sleep(0.1)
		
		trigger = datetime.datetime.now() + datetime.timedelta(milliseconds = 300)
		while GPIO.input(pin) and datetime.datetime.now() < trigger:
			time.sleep(0.1)
		return GPIO.input(pin)
	
	
	def _set_led(self, value):
		GPIO.output(self.user['led_pin'], value)


def get_random_message():
	today = datetime.date.today().strftime('%Y-%m-%d %a')

	with open('messages.json', encoding = 'utf-8-sig') as file:
		messages = [message for message in json.load(file) if re.match(message['date'], today) != None]
	
	return random.choice(messages)['text']
	

def log_message(message):
	print('{0} {1}'.format(datetime.datetime.now(), message))
	try:
		with open(log_filename(), "a") as file:
			file.write('{0} {1}\n'.format(datetime.datetime.now(), message))
	except:
		pass

def log_error():
	try:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		print('{0}'.format(datetime.datetime.now()))
		for line in lines:
			print(lines)
		print('----------------------------------------')
		with open(log_filename(), "a") as file:
			file.write('{0}\n'.format(datetime.datetime.now()))
			for line in lines:
				file.write(line)
			file.write('----------------------------------------\n')
	except:
		pass


def log_filename():
	return '{0}.log'.format(datetime.date.today())

def validate(users):
	pins = list(config.PINS)
	
	for user in users:
		for pin in [user['button_pin'], user['led_pin']]:
			if pin not in pins:
				raise Error('Pin {0} does not exist.'.format(pin))
	
	for user in users:
		for pin in [user['button_pin'], user['led_pin']]:
			if pin in pins:
				pins.remove(pin)
			else:
				raise Error('Pin {0} is used twice.'.format(pin))


def main():
	GPIO.setmode(GPIO.BCM)
	log_message('Loading config ...')
	users = config.load()
	iphone_users = []
	threads = []
	log_message('Validating config ...')
	validate(users)
	for user in users:
		iphone_user = IphoneUser(user)
		iphone_users.append(iphone_user)
		thread = Thread(target = iphone_user.run)
		threads.append(thread)
		thread.start()
	log_message('Initialised:\n' + config.format(users))
	
	print('Press ENTER to quit.')
	print('')
	try:
		input('')
	except:
		while True:
			time.sleep(5)
	
	for iphone_user in iphone_users:
		iphone_user.stop()
	for thread in threads:
		thread.join()

	log_message('All threads stopped.')


if __name__ == '__main__':
	try:
		log_message('Started!')
		main()
	except:
		log_error()
	finally:
		GPIO.cleanup()