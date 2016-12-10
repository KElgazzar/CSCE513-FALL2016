
import pexpect
import sys
import time
from sensor_calcs import *
import json
import select
from Sensortag_classes import *
import requests
import warnings
import datetime
import traceback
import httplib
import math
from pymongo import MongoClient
import ouimeaux
from ouimeaux.environment import Environment
from time import sleep


now = time.strftime("%c")
Sending = True #if user needs sending to DB
Number_of_reading = 10 #number of reading to read data from the TAG
    
def hexTemp2C(raw_temperature):
	
	string_temp = raw_temperature[0:2]+' '+raw_temperature[2:4]+' '+raw_temperature[4:6]+' '+raw_temperature[6:8] #add spaces to string	
	#TODO:Fix the following line so that I don't have to add and to remove spaces
	raw_temp_bytes = string_temp.split() # Split into individual bytes
	raw_ambient_temp = int( '0x'+ raw_temp_bytes[3]+ raw_temp_bytes[2], 16) # Choose ambient temperature (reverse bytes for little endian)
	raw_IR_temp = int('0x' + raw_temp_bytes[1] + raw_temp_bytes[0], 16)
	IR_temp_int = raw_IR_temp >> 2 & 0x3FFF
	ambient_temp_int = raw_ambient_temp >> 2 & 0x3FFF # Shift right, based on from TI
	ambient_temp_celsius = float(ambient_temp_int) * 0.03125 # Convert to Celsius based on info from TI
	IR_temp_celsius = float(IR_temp_int)*0.03125
	ambient_temp_fahrenheit = (ambient_temp_celsius * 1.8) + 32 # Convert to Fahrenheit

	
	print "INFO: IR Celsius:    %f" % IR_temp_celsius
	print "INFO: Ambient Celsius:    %f" % ambient_temp_celsius
        return (IR_temp_celsius, ambient_temp_celsius)

def hexLum2Lux(raw_luminance):
	
	m ="0FFF"
	e ="F000" 
	raw_luminance = int(raw_luminance,16)
	m = int(m, 16) #Assign initial values as per the CC2650 Optical Sensor Dataset
	exp = int(e, 16) #Assign initial values as per the CC2650 Optical Sensor Dataset	
	m = (raw_luminance & m) 		#as per the CC2650 Optical Sensor Dataset
	exp = (raw_luminance & exp) >> 12 	#as per the CC2650 Optical Sensor Dataset
	luminance = (m*0.01*pow(2.0,exp)) 	#as per the CC2650 Optical Sensor Dataset
	print "INFO: Light Intensity:    %f" % luminance
	return luminance #returning luminance in lux

def hexHum2RelHum(raw_humidity):

    humidity = float((int(raw_humidity,16)))/65536*100 #get the int value from hex and divide as per Dataset.
    print "INFO: Relative Humidity:    %f" % humidity
    return humidity


def main():
# Wemo switch discover 
    wemo = Environment()
    wemo.start()
    wemo.discover(5)
    print wemo.list_switches()
    wemoSw = wemo.get_switch('WeMo Insight')
# Connection to database    
    connection = MongoClient("mongodb://hgamalm:Hisham123@ds139937.mlab.com:39937/firstdb")
    db = connection.firstdb.Temp # Connect to temperature collection
    db2 = connection.firstdb.Lux # Connect to Light Intensity collection
    db3 = connection.firstdb.Hum # Connect to Humidity collection
    global datalog
    global barometer
    
    bluetooth_adr = sys.argv[1]
    print "INFO: [re]starting.."
    tag  = SensorTag(bluetooth_adr) #pass the Bluetooth Address
    tag.char_write_cmd(0x24,01) #Enable temperature sensor
    tag.char_write_cmd(0x44,01) #Enable Light sensor
    tag.char_write_cmd(0x2C,01) #Enable Humidity sensor
    count = 0
    count2 = 0
    count3 = 0
    """GETTING THE IR AND AMBIENT TEMPERATURE"""
    while count < Number_of_reading:
		IR_temp_celsius, Ambient_temp_celsius = hexTemp2C(tag.char_read_hnd(0x21, "temperature")) #get the hex value and parse it to get Celcius
		if Sending == True:	
			print "INFO: Sending Temperature to Database..." 
                        new_record = {'Temperature IR':str(int(IR_temp_celsius)),'unit':"celsius",'Time':now}
                        # insert the record to DB
                        db.insert(new_record)
                        new_record_2 = {'Temperature Amb':str(int(Ambient_temp_celsius)),'unit':"celsius",'Time':now}
                        # insert the record to DB
                        db.insert(new_record_2)

		time.sleep(0.5) #wait for a while
		count =count +1
    """GETTING THE LUMINANCE"""
    while count2 < Number_of_reading:
     tag2 = SensorTag(bluetooth_adr)
     tag.char_write_cmd(0x44,01)
                 lux_luminance = hexLum2Lux(tag.char_read_hnd(0x41, "luminance")) #get the hex value and parse it to get Lux
                 if  lux_luminance < 20:# Threshold for triggering lamp to turn on
                      wemoSw.on() # turn on the switch
                 else:
                      wemoSw.off()    # turn off the switch
                 if Sending == True:	
	                 print "INFO: Sending Luminance to Database..." 
	                 new_record_3 = {'luminance':str(int(lux_luminance)),'unit':"Lux",'Time':now}
                     db2.insert(new_record_3)
	         time.sleep(0.5) #wait for a while
		 count2 =count2 +1
    
      
    """GETTING THE HUMIDITY"""
    while count3 < Number_of_reading:
     tag.char_write_cmd(0x2C,01)
                 rel_humidity = hexHum2RelHum(tag.char_read_hnd(0x29, "humidity"))
                 if Sending == True:	
                         print "INFO: Sending Humidity to Database..."
                         new_record_4 = {'Humidity':str(int(rel_humidity)),'unit':"%",'Time':now}
	                 db3.insert(new_record_4)
	         time.sleep(0.5) #wait for a while
		 count3 =count3 +1
    connection.close()
if __name__ == "__main__":
    main()

