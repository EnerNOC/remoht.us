# Remoht.us

This project is a cloud-based interface to a home automation system based on 
the Raspberry Pi.  It is a proof-of-concept written for a presentaiton at the 
[Boston Google Developers meetup](http://www.meetup.com/gdg-boston/).  The 
project demonstrates a number of interesting technologies including XMPP, 
AppEngine's Channel API, and the [Raspberry Pi](http://raspberrypi.org/).

Conceptual block diagram:

<a href='../../raw/master/block-diagram.png' target='_new'>
	<img src='../../raw/master/block-diagram.png' title='Block diagram' 
	style='max-width:600px'/>
</a>

The components of the project are outlined below:


## Web

<a href='../../raw/master/screenshot.png' target='_new' style='float:right'>
	<img src='../../raw/master/screenshot.png' title='Screenshot' 
	style='max-width:200px'/>
</a>

It's possible that anyone can use the live app at http://remoht.us/ - since you login
with your own Google credentials and use those same credentials for your sensor 
clusters (the Raspberry Pi(s)) there's no way for a user to view someone else's
sensor data.  

This is a [Google AppEngine](https://developers.google.com/appengine/) app that 
serves as the web UI.  The benefit to being on AppEngine is that it is 
universally accessible without having to deal with connecting through a NAT 
firewall to the HAN-side device.

Install this by [deploying it](https://developers.google.com/appengine/docs/python/gettingstartedpython27/uploading) to AppEngine.

Note you should run `minify.sh` prior to uploading to AppEngine as the deployed
version will look for minified CSS and JS assets.



## Pi

This is the client code that runs locally on the Raspberry Pi and performs local
data collection.  The Pi uses [SleekXMPP](http://sleekxmpp.org) to maintain a 
connection with AppEngine's XMPP service.  This allows for bidirectional communication
(server-to-client and client-to-server) without any sort of ugly HTTP polling.

The Pi also interfaces via [serial](http://pyserial.sourceforge.net/) to an Arduino.  
While the Pi has some GPIOs, it is not ideally suited for low-level hardware 
interaction and cannot do any analog I/O.  Thus, that work is left up to a separate
microcontroller, in our case an Arduino.

Your distro should have python installed already; if so you can use [Pip]() to install
the dependencies.
 
    # get Pip installed:
    curl -O http://python-distribute.org/distribute_setup.py
    python distribute_setup.py
    easy_install pip

    # install dependencies
    pip install < requirements.txt

Then run by calling
    
    python remoht.py # use --help to see command line options


## Arduino

This code runs on an [Arduino](http://arduino.cc) an collects data from a number of
hardware peripherals.  In the first incarnation, this includes:

* a [Photocell](https://www.sparkfun.com/products/8630) to measure light levels,
* a [LM36](http://learn.adafruit.com/tmp36-temperature-sensor/using-a-temp-sensor) 
  temperature sensor
* a [PIR](https://www.sparkfun.com/products/8630) motion sensor
* [relays](http://jeelabs.net/projects/hardware/wiki/Relay_Plug) to control lights, 
  small electronics, etc.

And this could easily be expanded to include other hardware peripherals as well. The
Arduino acts as a "bus" and uses a simple serial protocol to transmit the low-level
hardware readings to the Raspberry Pi.  The project source contains a 
[schematic diagram](arduino/remoht-arduino.fzz) that can be viewed in 
[Fritzing](http://fritzing.org).


### Connecting the Arduino to the Raspberry Pi

There are a couple options here.  If you have an Arduino with an on-board USB port, 
simply connect the Arduino to your Raspberry Pi's USB powered hub.  The Arduino should
then enumerate as `/dev/ttyUSB0`.  You would then run the Raspberry Pi client as follows:

    python remoht.py --tty=/dev/ttyUSB0 # plus additional parameters

If you are using an Arduino Pro Mini or any other chip that does not have built-in USB
interface or FTDI usb-to-serial converter, you can connect the serial and power pins 
directly to the Pi's [GPIO header](http://elinux.org/RPi_Low-level_peripherals) which 
is exposed as `/dev/ttyAMA0`.  In that case, note that the TX pin on the Ardunio 
connects to the RX (pin 15) on the Raspberry Pi and vice versa.  The 5v or 3v3 
should also be able to power the Arduino and sensors, but probably not the relays.  


## About XMPP

The system assumes you will use the same GMail/ Google Talk account for both your web login 
and the XMPP credentials on the Raspberry Pi.  This makes it a bit easier to auto-detect
clients without requiring you to type in the JID that your Raspberry Pi is using.  If
you're not comfortable re-using your Gmail password in the hardware, you can use
[AuthSub](https://accounts.google.com/IssuedAuthSubTokens) from your Google account to 
issue passwords for specific uses and revoke them later if necessary.


## To Do

* add interrupt-driven events to the Pi rather than polling
* Local web UI on the Raspberry Pi
* Local logging on the Raspberry Pi, push readings to the cloud on change-of-value 
* Support multiple Arduino-based sensors (e.g. communicating via xbee)

## Legal 

Copyright 2013 EnerNOC Inc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
