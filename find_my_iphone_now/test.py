from RPi import GPIO
import time


def main():
	LED_OFF = 0
	LED_ON = 1 - LED_OFF
	
	button_pins = [17, 13, 20, 23]
	led_pins = [27, 19, 21, 24]
	
	for pin in button_pins:
		GPIO.setup(
			pin,
			GPIO.IN,
			pull_up_down = GPIO.PUD_DOWN
		)
	
	for pin in led_pins:
		GPIO.setup(
			pin,
			GPIO.OUT,
			initial = LED_OFF
		)
	
	led = 0
	while True:
		text = ''
		for pin in [0,1,2,3]:
			text += '{0}'.format(pin) if GPIO.input(button_pins[pin]) else ' '
		print(text)
		
		GPIO.output(led_pins[led], LED_OFF)
		led += 1
		if led == 4:
			led = 0
		GPIO.output(led_pins[led], LED_ON)
		time.sleep(0.5)


if __name__ == '__main__':
	try:
		GPIO.setmode(GPIO.BCM)
		main()
	finally:
		GPIO.cleanup()
