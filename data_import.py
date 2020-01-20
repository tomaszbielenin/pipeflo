# Import Python standard modules for use in the script
 
import csv  #Used for reading csv file
 
import os   #Used for path operations
 
 
# With the modules loaded, we can define variables for the file path. In this case, the script will look in the directory
# where this .py file is and find a file named pipe_data.csv.
 
dir = os.path.dirname( os.path.abspath( __file__ ) )
 
data_file_path = os.path.join( dir, 'pipe_data.csv' )
 
 
# NOTE: From this point forward, pay attention to the tabbing in the file. It indicates what statements are included
# in the various statement and loops.
 
# Read the pipe_data.csv file using the csv module that we imported above.
 
with open( data_file_path ) as csvfile:
 
    reader = csv.reader( csvfile )
 
 
#Process data for each row in the csv file, and assign it to variables. The FOR loop will end with the last row of the .csv file
 
    for data_row in reader:
        pipe_name = data_row[0]
        pipe_length = float( data_row[1] )
        pipe_size = data_row[2]
         
# Import the values for length and size for the current row of the .csv file. The length has no units specified, so it will be set in the
# same units that are currently in use for that field. These import functions can be found in the Data Import section of the help file.
 
        pipeflo().doc().get_pipe( pipe_name ).set_length(pipe_length)
        pipeflo().doc().get_pipe( pipe_name ).set_pipe_size(pipe_size)
 
 
# Print the pipe name, length and size for each row to the Output tab of the Data Import dialog.
 
        print( 'Pipe: {}\tLength: {}\tSize: {}'.format( pipe_name, pipe_length, pipe_size ) )
