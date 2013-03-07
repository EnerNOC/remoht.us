# Simulating Devices

The scripts in this folder are meant to simulate responses & telemetry from a connected
device.  Once the app in running (via `dev_appserver.py`) do the following:

Announce an online device by running `presence.py`:

    python presence.py  

    # specify multiple devices by running the script multiple times, 
    # specifying a different resource each time like so:

    python presence.py --resource=office


The resource should then appear under "Add a device" in the UI.  Choose that device, 
then click it again in the "Devices" list.  This will cause the app to query the device 
for its current relay status & start accepting readings.

    # this will tell the app what the device's current relay status is
    python responses.py relay "0 1" 


Now start sending dummy data to the app and "Current Readings" should appear:

    python random_data.py
