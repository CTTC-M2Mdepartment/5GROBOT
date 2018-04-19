import socket
import json
import time
import RPi.GPIO as GPIO
import requests

print 'UDP Client Starts.'

# GPIO setup for ultrasonic sensor
TRIG = 17
ECHO = 5

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIG,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(ECHO,GPIO.IN)

# define IP and port
addr = ('<broadcast>', 2002)

# init broadcast socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def sendUDP(msg):
	s.sendto(msg.decode(), addr)
	print 'UDP sent: ', msg


# specify robot
robot = 'robot2'
url = 'http://172.24.1.6:8080/restconf/config/robotApp/'
# retrieve last command from this url.
# I record the latest command in the control app.
log_url = 'http://172.24.1.249:8848/log'

def sendSTOP():
	msg = {
		'robotId': robot,
		'command': 'STOP',
		'speed': 15,
		'angle': 0,
		'TrackStatus': 0
	}
	try:
		res = requests.put(url, json=msg, timeout=0.1)
	except Exception:
		print 'Failed to connect robot server.'
	else:
		print 'STOP sent.'

def sendCONTINUE():
	msg = requests.get(log_url).text
	msg = json.loads(msg)
	msg['robotId'] = robot
	try:
		res = requests.put(url, json=msg, timeout=0.1)
	except Exception:
		print 'Failed to connect robot server.'
	else:
		print 'CONTINUE sent.'


def measureDistance():
	GPIO.output(TRIG,GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(TRIG,GPIO.LOW)
	while not GPIO.input(ECHO):
		pass
	t1 = time.time()
	while GPIO.input(ECHO):
		pass
	t2 = time.time()
	distance =  (t2-t1)*34000/2
	# print 'distance: %.2f' % distance
	return distance


# define DENM_type 
denm_type = {}
denm_type['SourceRobotID'] = robot
denm_type['EventType'] = 1

stop_status = False

# main loop
try:
	while True:
		time.sleep(0.1)
		distance = measureDistance()
		if distance < 15 and not stop_status:
			detectTime = time.time()
			print'obstacle find at: ', detectTime
			sendSTOP()
			stop_status = True
			# construct STOP DENM
			denm_type['EventPosition'] = distance
			denm_type['DetectionTime'] = detectTime
			denm_type['Termination'] = True
			msg = json.dumps(denm_type)
			sendUDP(msg)

		if distance > 20 and stop_status:
			detectTime = time.time()
			print'obstacle remove at: ', detectTime
			sendCONTINUE()
			stop_status = False
			# construct CONTINUE DENM
			denm_type['EventPosition'] = distance
			denm_type['DetectionTime'] = detectTime
			denm_type['Termination'] = False
			msg = json.dumps(denm_type)
			sendUDP(msg)
finally:
	s.close()
