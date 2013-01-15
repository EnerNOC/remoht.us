# Remoht.us

This project is a web-based interface to a home automation system based on 
the Raspberry Pi.  It has several components outlined below:



## Web

This is a [Google AppEngine](https://developers.google.com/appengine/) app that 
serves as the web UI.  The benefit to being on AppEngine is that it is 
universally accessible without having to deal with connecting through a NAT 
firewall to the HAN-side device.

Install this by [deploying it](https://developers.google.com/appengine/docs/python/gettingstartedpython27/uploading) to AppEngine.



## Pi

This is the client code that runs locally on the Raspberry Pi and performs local
data collection.  The Pi uses [SleekXMPP](http://sleekxmpp.org) to maintain a 
connection with AppEngine's XMPP service.  This allows for bidirectional communication
(server-to-client and client-to-server) without any sort of ugly HTTP polling.

The Pi also interfaces via [serial](http://pyserial.sourceforge.net/) to an Arduino.  
While the Pi has some GPIOs it is not ideally suited for low-level hardware 
interaction.  Thus, that work is left up to an Arduino.

Your distro should have python installed already; if so you can use [Pip]() to install
the dependencies.
 
    # get Pip installed:
    curl -O http://python-distribute.org/distribute_setup.py
    python distribute_setup.py
    easy_install pip

    # install dependencies
    pip install < requirements.txt

Then run by calling
    
    python remoht.py



## Arduino

This code runs on an [Arduino](http://arduino.cc) an collects data from a number of
hardware peripherals.  In the first incarnation, this includes:

* an LDR,
* a temperature sensor
* a PIR
* relays

And this could easily be expanded to include other hardware peripherals as well. The
Arduino acts as a "bus" and uses a simple serial protocol to translate the low-level
hardware readings to the Raspberry Pi.
