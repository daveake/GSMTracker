import time
import math
import sys
from pygsm import GsmModem

def CalculateDistance(Latitude1, Longitude1, Latitude2, Longitude2):
	Latitude1 = Latitude1 * math.pi / 180
	Longitude1 = Longitude1 * math.pi / 180
	Latitude2 = Latitude2 * math.pi / 180
	Longitude2 = Longitude2 * math.pi / 180

	return 6371000 * math.acos(math.sin(Latitude2) * math.sin(Latitude1) + math.cos(Latitude2) * math.cos(Latitude1) * math.cos(Longitude1-Longitude1))
	
if len(sys.argv) < 3:
	print ""
	print "Usage: python gsmtrack.py <payload_ID> <phone_number> [gateway_number]"
	print ""
	print "payload_ID is the payload ID to include in text messages."
	print "phone_number is the number of a mobile phone to send texts to."
	print "gateway_number (optional) is the number of a gateway to send texts to."
	print ""
	print "Texts to phone_number will contain the GPS position including a Google map link"
	print "Texts to gateway_number are intended to be processed by a script (e.g. uploaded to the HAB map)"
	print ""
	print "Example: python gsmtrack.py 07000987621 07000987622"
	print ""
	quit()
	
PayloadID = sys.argv[1]
MobileNumber = sys.argv[2]
print "Texts will be sent to mobile phone " + MobileNumber
if len(sys.argv) > 3:
	GatewayNumber = sys.argv[3]
	print "Texts will be sent to gateway number " + GatewayNumber
else:
	GatewayNumber = None


SendTimeout = 5			# Send position every x minutes regardless of movement
HorizontalDelta = 50	# Send position if it moves horizontally by at keast this many metres
VerticalDelta = 50		# Send position if it moves vertically by at least this many metres
MaxGSMAltitude = 2000	# Don't try to send above this altitude

PreviousSeconds = 0
PreviousAltitude = 0
PreviousLatitude = 0
PreviousLongitude = 0

gsm = GsmModem(port="/dev/ttyAMA0")
gsm.boot()

print "GPS/GSM UKHAS Tracker"
print "====================="
print

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

# Switch GPS on
print "Switching GPS on ..."
reply = gsm.command('AT+CGNSPWR=1')
print reply

while True:
	# Get position
	reply = gsm.command('AT+CGNSINF')
	list = reply[0].split(",")
	if len(list[2]) > 14:
		UTC = list[2][8:10]+':'+list[2][10:12]+':'+list[2][12:14]
		Latitude = list[3]
		Longitude = list[4]
		Altitude = list[5]
		print 'Position: ' + UTC + ', ' + Latitude + ', ' + Longitude + ', ' + Altitude
		Seconds = int(UTC[0:2]) * 3600 + int(UTC[3:5]) * 60 + int(UTC[6:8])
		
		if Altitude <> '':
			Latitude = float(Latitude)
			Longitude = float(Longitude)
			Altitude = float(Altitude)
			
			if Seconds < PreviousSeconds:
				PreviousSeconds = PreviousSeconds - 86400
			
			# Send now ?
			if Altitude <= MaxGSMAltitude:
				# Low enough
				Send = False
				if Seconds > (PreviousSeconds + SendTimeout * 60):
					Send = True
					print("Send because of timeout")
					
				Distance = abs(CalculateDistance(Latitude, Longitude, PreviousLatitude, PreviousLongitude))
				if Distance >= HorizontalDelta:
					Send = True
					print("Send because of horizontal movement")
					
				if abs(Altitude - PreviousAltitude) >= VerticalDelta:
					Send = True
					print("Send because of vertical movement")
						
				if Send:
					PreviousSeconds = Seconds
					PreviousAltitude = Altitude
					PreviousLatitude = Latitude
					PreviousLongitude = Longitude
			
					# Text to my mobile
					Message = PayloadID + ' position: ' + UTC + ', ' + str(Latitude) + ', ' + str(Longitude) + ', ' + str(int(Altitude)) + ' http://maps.google.com/?q=' + str(Latitude) + ',' + str(Longitude)
					print "Sending to mobile " + MobileNumber + ": " + Message
					gsm.send_sms(MobileNumber, Message)

					# Text to my gateway
					if GatewayNumber:
						print ("Sending text to gateway")
						Message = 'HAB:' + PayloadID + ',1,' + UTC + ',' + str(Latitude) + ',' + str(Longitude) + ',' + str(int(Altitude))
						print "Sending to gateway " + GatewayNumber + ": " + Message
						gsm.send_sms(GatewayNumber, Message)
				
	time.sleep(1)
