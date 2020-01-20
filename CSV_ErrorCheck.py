#The first step is to load some standard Python modules to read the .csv file and perform the file operations:

import sys
import csv
import os

#With the modules loaded, we can define variables for the file path. In this case, to look in the directory where
#this .py file is and find a file named UPW_Data.csv.

dir = os.path.dirname( os.path.abspath( __file__ ) )
data_file_path = os.path.join( dir, 'UPW_Data.csv' )

#The script counts and reports the number of updates performed and errors encountered while running. These count
#variables need to be initialized to 0.

errors = 0
updates = 0

#Note: From this point forward, pay attention to the tabbing in the file. It indicates what statements are included
#in the various statement and loops.

#The file then needs to be opened by the script using the csv reader module:

with open( data_file_path ) as csvfile:
	reader = csv.reader( csvfile )    

#The FOR loop is used to read each row of the file, and assign the values from those rows to variables. This loop will
#end when it runs out of data rows in the .csv file:

	for data_row in reader:
		name = data_row[0]
		flow = data_row[1]
		elevation = data_row[2]   

#The try function will test the values, without causing an error that will abort the script. In this case, testing the name:
 
		try:
			name_test = pipeflo().doc().get_flow_demand( name )            

#If there is an exception (the name does not exist in the model) the script will print a line to the Output tab with the name
#of the device, add 1 to the error count variable and continue back to the top of the for loop:

		except RuntimeError:
			print( 'Did not find device', name )
			errors += 1
			continue

#The next try block tests to see that the flow variable value is valid by assigning it to a new variable as a floating point
#number. If the value is the wrong type, it is reported and the rest of that row is skipped by the continue statement. If it is a
#valid number, it is imported to the model and 1 is added to the update variable. This process is repeated for the elevation value.

		try:
			flow_tested = float( flow )

		except ValueError:
			print( 'Invalid flow value type: ', 'Device:', name,', Value:', flow )
			errors += 1
			continue
		
		pipeflo().doc().get_flow_demand( name ).set_flow_demand_operation( flow_demand_operation( set_flow_fd, flow_rate(flow_tested , gpm) ) )
		updates += 1

#NOTE: To set the flow demand values with PIPE-FLO 14 use the commented out function below instead:
		#pipeflo().doc().get_flow_demand( name ).set_flow( flow_tested)
		 
		try:
			elevation_tested = float( elevation )

		except ValueError:
			print( 'Invalid elevation value type: ', 'Device:', name,', Value:', elevation )
			errors += 1
			continue

		pipeflo().doc().get_flow_demand( name ).set_elevation( elevation_tested )
		updates += 1

#Once every row in the .csv file has been tested and imported, a summary is printed to the Data Import Output dialog:
 
print( 'Import finished.' )
if updates > 0:
	print( updates, 'items updated.' )
if errors > 0:
	print( errors, 'errors.' )