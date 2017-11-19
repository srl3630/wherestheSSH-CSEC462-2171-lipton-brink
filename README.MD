Dependencies:
	1. Python 2.7
	2. Pygeoip
		a. wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
		b. gunzip GeoLiteCity.dat.gz
		c. pip install pygeoip
	3. Psycopg2
		a. pip install psycopg2
	4. Pytailf
		a. pip install pytailf
	5. Postgresql
		a. apt-get install postgresql

Initial setup:
	1. Create a database in postgresql named 'mynetprojdb'
		a. 'CREATE DATABASE mynetprojdb;'
	2. Import the tables to your new database using the following command:
		a. 'psql -U USERNAME mynetprojdb < dbexport.pgsql'
	3. Modify the first lines of each of the two functions to include the correct path to GeoLiteCity.dat
	 
To run the script:
	1. 'python2.7 parser.py -i' to go through the entire file one time and parser the output.
	2. 'python2.7 parser.py -w' to watch the file for new input and add any new connections to the database as they come in. 

Contact information:
	If there are any problems or you would like to comment on this project our emails are here:
		Scott Brink: seb3684@rit.edu
		Samuel Lipton: srl3630@rit.edu
