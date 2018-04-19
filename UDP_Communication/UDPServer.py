import socket
import requests
import json

print 'UDP Server Starts.'

# specify robot
robot = 'robot4'
url = 'http://172.24.1.8:8080/restconf/config/robotApp/'
# retrieve last command from this url
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


addr = ('', 2002)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(addr)


# main loop
try:
    while True:
        msg, addr = s.recvfrom(2048)
        if msg != None:
	        print('received message from', addr)
	        print(msg.decode())
	        denm_type = json.loads(msg.decode())
	        if denm_type['Termination']:
	        	sendSTOP()
	        else:
	        	sendCONTINUE()
finally:
    s.close()
