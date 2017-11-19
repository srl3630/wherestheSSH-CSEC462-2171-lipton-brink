#!/usr/bin/env python
#
# File: parser.py
#
# Purpose: Parse through /var/log/auth.log file in order to determine successful or unsuccessful SSH connections.
#
# Author: Scott Brink
#
import sys
import re
import datetime
import pygeoip
from time import strptime
import time
import psycopg2
from tailf import tailf
from sys import argv

# Runs through the entire /var/log/auth.log file, parses it, and places the results into a database
def initial():
	# Database of IP to geographical locations
	rawdata = pygeoip.GeoIP('/home/botmenow/Documents/netforprojcode/geolocate/GeoLiteCity.dat')
	a = []
	f = open("/var/log/auth.log", "r")
	contents=f.readlines()
	for line in contents:
		# If the line is ssh, parse.  Otherwise, skip.
		if "sshd" in line:
			# If the line is a failed connection
			if "preauth" in line and "port" in line:
				# Grab the IP
				ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",line)
				# If IP exists, use GeoIP to grab the other attributes
				if ip != a:
					data = rawdata.record_by_name(ip[0])
					state = data['region_code']
					city = data['city']
					longi = data['longitude']
					lat = data['latitude']

				# Grab the connection time
				time = re.findall(r"\b\d{1,3}:\d{2}:\d{2}\b",line)
				b = line[0:3]
				c = strptime(b,'%b').tm_mon
				d = line[4:7].strip()
				now = datetime.datetime.now()
				date = str(now.year)+"-"+str(c)+"-"+str(d)

				# Connect to the database and insert the data
				conn=psycopg2.connect("host = 'localhost' dbname='mynetprojdb' user='netproj' password='default'")
				cur = conn.cursor()
				cur.execute("INSERT INTO logs (time,date,city,state,ip,lat,long,auth) VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)", (time[0], date, str(city), str(state), ip[0], lat, longi))
				conn.commit()
				cur.close()
				conn.close()  
						
			# If the line is a working connection
			if "publickey" in line:
				# Grab the IP
				ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",line)			
				# If IP exists, use GeoIP to grab the other attributes
				if ip != a:
					data = rawdata.record_by_name(ip[0])
					state = data['region_code']
					city = data['city']
					longi = data['longitude']
					lat = data['latitude']

				# Grab the connection time
				time = re.findall(r"\b\d{1,3}:\d{2}:\d{2}\b",line)
				b = line[0:3]
				c = strptime(b,'%b').tm_mon
				d = line[4:7].strip()
				now = datetime.datetime.now()
				date = str(now.year)+"-"+str(c)+"-"+str(d)

				# Connect to the database and insert the data
				conn=psycopg2.connect("host = 'localhost' dbname='mynetprojdb' user='netproj' password='default'")
				cur = conn.cursor()
				cur.execute("INSERT INTO logs (time,date,city,state,ip,lat,long,auth) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)", (time[0], date, str(city), str(state), ip[0], lat, longi))
				conn.commit()
				cur.close()
				conn.close()  

# Watches the end of the file for new additions
def watch():
	# Database of IP to geographical locations	
	rawdata = pygeoip.GeoIP('/home/botmenow/Documents/netforprojcode/geolocate/GeoLiteCity.dat')
	a = []
	# Watch loop
	for line in tailf("/var/log/auth.log"):
		# If the line is ssh, parse.  Otherwise, skip.
		if "sshd" in line:
			# If the line is a failed connection 
			if "preauth" in line and "port" in line:
				# Grab the IP
				ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",line)
				# If IP exists, grab the geographical data
				if ip != a:
					data = rawdata.record_by_name(ip[0])
					state = data['region_code']
					city = data['city']
					longi = data['longitude']
					lat = data['latitude']

				# Grab the connection time
				time = re.findall(r"\b\d{1,3}:\d{2}:\d{2}\b",line)
				b = line[0:3]
				c = strptime(b,'%b').tm_mon
				d = line[4:7].strip()
				now = datetime.datetime.now()
				date = str(now.year)+"-"+str(c)+"-"+str(d)

				# Connect to the database and insert the data
				conn=psycopg2.connect("host = 'localhost' dbname='mynetprojdb' user='netproj' password='default'")
				cur = conn.cursor()
				cur.execute("INSERT INTO logs (time,date,city,state,ip,lat,long,auth) VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)", (time[0], date, str(city), str(state), ip[0], lat, longi))
				conn.commit()
				cur.close()
				conn.close()  
	
			# If the line is a successful connection						
			if "publickey" in line:
				# Grab the IP 
				ip = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",line)
				# If IP exists, grab the geographical data
				if ip != a:
					data = rawdata.record_by_name(ip[0])
					state = data['region_code']
					city = data['city']
					longi = data['longitude']
					lat = data['latitude']

				# Grab the connection time
				time = re.findall(r"\b\d{1,3}:\d{2}:\d{2}\b",line)
				b = line[0:3]
				c = strptime(b,'%b').tm_mon
				d = line[4:7].strip()
				now = datetime.datetime.now()
				date = str(now.year)+"-"+str(c)+"-"+str(d)

				# Connect to the database and insert the data
				conn=psycopg2.connect("host = 'localhost' dbname='mynetprojdb' user='netproj' password='default'")
				cur = conn.cursor()
				cur.execute("INSERT INTO logs (time,date,city,state,ip,lat,long,auth) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)", (time[0], date, str(city), str(state), ip[0], lat, longi))
				conn.commit()
				cur.close()
				conn.close()  

if __name__ == '__main__':
	if len(argv) != 2:
		print("Usage: ./parser.py [-w watches the file] [-i is the first round]")
		sys.exit()
	else:	
		if '-w' in argv[1]:
			watch()
		if '-i' in argv[1]:
			initial()	
		else:
			print("Usage: ./parser.py [-w watches the file] [-i is the first round]")

