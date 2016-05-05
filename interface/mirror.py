#!/usr/bin/python

import cgi, cgitb
import json


###########################################################
##################### The main controller code starts here.
###########################################################

# Create instance of FieldStorage and get data
form = cgi.FieldStorage()
receivedMarkerData = form.getvalue('useTheseMarkers')
## convert the received json string into a Python object
#receivedGeoJson = json.loads(receivedMarkerData)

# place the magic here...


# prepare for output... the GeoJSON should be returned as a string
print "Content-type:text/html\r\n\r\n"
print receivedMarkerData
