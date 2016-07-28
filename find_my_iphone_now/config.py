import base64
import json


PINS = [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
CONFIG_PATH = 'config.json'


def decode(text):
	return base64.b64decode(text.encode()).decode()


def encode(text):
	return base64.b64encode(text.encode()).decode()


def format(users):
	username_width     = max(9, max(len(user['username'    ]) for user in users))
	display_name_width = max(6, max(len(user['display_name']) for user in users))
	result = '   Button    LED   User Name' + (' '*(username_width-9)) + '  Device\n' + ('-'*(21 + username_width + display_name_width)) + '\n'
	i = 1
	for user in users:
		result += ('{0}: GPIO{button_pin:0>#2}  GPIO{led_pin:0>#2}  {username:<'+str(username_width)+'}  {display_name}\n').format(i, **user)
		i += 1
	return result


def load():
	try:
		with open(CONFIG_PATH) as file:
			return json.load(file)
	except:
		return []

		
def save(configuration):
	with open(CONFIG_PATH, 'w') as file:
		json.dump(configuration, file, indent = 2)


def validate_pin(pin):
	if pin not in PINS:
		raise IndexError('Pin {0} does not exist.'.format(pin))
