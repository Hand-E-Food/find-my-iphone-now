import config
from find_my_iphone import FindMyIphone
import os
import sys
import traceback


def main():
	users = config.load()
	running = True
	while running:
		_clear_console()
		
		print(config.format(users))
		print('{0}: New...'.format(len(users) + 1))
		print('S: Save and exit')
		print('X: Exit without saving')
		text = input('? ').upper()
		print('')
		
		try:
			if text == 'X':
				running = False
			elif text == 'S':
				config.save(users)
				running = False
			else:
				i = _try_parse_int(text, default = 0) - 1
				if i >= 0 and i < len(users):
					users[i] = _config_user()
				elif i == len(users):
					users.apppend(_config_user())
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
			for line in lines:
				print(lines)
			print('')
			input('Press ENTER ...')


def _config_user():
	username   = input('Username  : ')
	password   = input('Password  : ')
	print('')

	proxy.sign_in(username, password)
	proxy.init_devices()
	i = 0
	for device in proxy.devices:
		i += 1
		print('Device {0}  = {1}'.format(i, _get_display_name(device)))
	device_index = int(input('Device    : ')) - 1
	device_id    = proxy.devices[device_index]['id']
	proxy.sign_out()
	print('')

	button_pin   = int(input('Button pin: '))
	validate_pin(button_pin)
	led_pin      = int(input('LED pin   : '))
	validate_pin(led_pin)
	return {
		'username': username,
		'password': encode(password),
		'id': device_id,
		'display_name': _get_display_name(device),
		'button_pin': button_pin,
		'led_pin': led_pin,
	}


def _clear_console():
	os.system('cls' if os.name == 'nt' else 'clear')

	
def _get_display_name(device):
	return '{0} ({1})'.format(device['name'], device['deviceDisplayName'])


def _try_parse_int(text, base = 10, default = None):
	try:
		return int(text, base)
	except ValueError:
		return default


if __name__ == '__main__':
	main()
