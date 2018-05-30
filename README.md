# GSM/GPS Tracker And HAB Gateway #

This system consists of 2 Raspberry Pi boards, one as a tracker with GSM/GPS board, and the other as a gateway with GSM modem.  The tracker gets its position from the GSM/GPS device, and sends it as text messages to your phone and the gateway.

There are 2 Python 2 scripts, one for the tracker and one for the gateway, that together place the position of the tracker on the live HAB map (https://tracker.habhub.org).

See my [blog post](http://www.daveakerman.com/?p=2324 "blog post") for more information.

# Tracker #

## Hardware ##

The tracker requires a combined GSM/GPS device e.g. SIM868.  I used the [Waveshare HAT](https://www.waveshare.com/gsm-gprs-gnss-hat.htm "Waveshare HAT") and a PI Zero.  You also need a suitable power supply for these; remember that GSM can briefly take a lot of current so dont skimp here.


## Software ##

The gsmtrack.py script connects to the GSM/GPS device, firstly to retrieve the current position and secondly to send that position to your mobile phone and (optionally) the gateway (see below).  It is written in Python 2 and uses the [https://github.com/adammck/pygsm](https://github.com/adammck/pygsm "PyGSM") library.

You should autostart the script so that it runs after power-up.

The script takes two or three parameters:

1. - Payload ID, which is what the payload will appear on the map as
1. - Number of your mobile phone
1. - (optional) Number of your gateway.
 

There are some hard-coded parameters near the top of the script to help it decide when to send texts to the above number(s) - e.g. on movement, or after a timeout.  Adjust as required.

Remember to disable serial login on the Pi, but keep the serial port enable, in raspi-config.

Remember to switch the Pi HAT on after the Pi is powered up - hold the button for a second - because it DOES NOT AUTOSTART.

Remember to use a SIM card with enough credit for the number of texts you expect to be sent.

# Gateway #

## Hardware ##

The gateway needs an internet connection and a GSM modem - e.g. a USB dongle. I used a Huawei E173 which is very common, but pretty much anything will do.  That needs a SIM card but as it only receives then you can use a card with no credit on it.  Many carriers give these away for free.

## Software ##

The gateway.py script connects to the GSM modem, polling it for incoming messages.  Each received message is checked for format and, if it looks like a position message from the tracker, a UKHAS-standard message is created and uploaded to habhub.org.

## Payload Document ##

As with other trackers uploaded tohabhub.org, you need to have a payload document to match what is uploaded.  Use [http://habitat.habhub.org/genpayload/](http://habitat.habhub.org/genpayload/ "http://habitat.habhub.org/genpayload/") to create a document, with the "callsign" set to the "payload ID" you used for the tracker, plus the following fields:

- sentence_id: Integer
- time: Time
- latitude: Coordinate (dd.dddd)
- longitude: Coordinate (dd.dddd)
- altitude:  Integer
- 
-  

