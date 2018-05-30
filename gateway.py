import time
import sys
import urllib2
import crcmod
import json
from base64 import b64encode
from hashlib import sha256
from datetime import datetime
from pygsm import GsmModem

def crc16_ccitt(data):
    crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')
    return hex(crc16(data))[2:].upper().zfill(4)


def UploadTelemetry(Callsign, Sentence):
        sentence_b64 = b64encode(Sentence.encode())

        date = datetime.utcnow().isoformat("T") + "Z"

        data = {"type": "payload_telemetry", "data": {"_raw": sentence_b64.decode()}, "receivers": {Callsign: {"time_created": date, "time_uploaded": date,},},}
        data = json.dumps(data)

        url = "http://habitat.habhub.org/habitat/_design/payload_telemetry/_update/add_listener/%s" % sha256(sentence_b64).hexdigest()
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        try:
                response = urllib2.urlopen(req, data.encode())
        except Exception as e:
                pass

gsm = GsmModem(port="/dev/ttyUSB0")
gsm.boot()

print "Modem details ..."
reply = gsm.hardware()
print "Manufacturer = " + reply['manufacturer']
print "Model = " + reply['model']
print

# Try and get phone number
reply = gsm.command('AT+CNUM')
if len(reply) > 1:
	list = reply[0].split(",")
	phone = list[1].strip('\"')
	print "Phone number = " + phone
	print

print "Waiting for messages ..."
while True:
	message = gsm.next_message()
	if message:
		print message
		text = message.text
		if text[0:4] == 'HAB:':
			packet = text[4:]
			sentence = '$$' + packet + '*' + crc16_ccitt(packet.encode()) + '\n'
			print "Uploading sentence: " + sentence
			UploadTelemetry('SMS_Gateway', sentence)
	else:
		time.sleep(1)