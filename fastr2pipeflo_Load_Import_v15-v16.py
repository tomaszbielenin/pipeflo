import sys
import csv
import os

dir = os.path.dirname( os.path.abspath( __file__ ) )
data_file_path = os.path.join( dir, 'PipeFlo Extract with Modeling Factor.csv')														# EDIT THIS NAME DEPENDING ON CSV FILE NAME
doc = pipeflo().doc()
model_name = doc.get_file_name()

#Define data column positions 																				
fpoc_col = 1																								#EDIT THIS VALUE DEPENDING ON WHAT COLUMN DPSEGMENT_FPOC IS IN
start_col = 2																								#EDIT THIS VALUE DEPENDING ON WHAT COLUMN THE START OF DEMAND DATA IS IN
UPN_col = 12																								#EDIT THIS VALUE DEPENDING ON WHAT COLUMN UPN DATA IS IN

#Initialize column counter
lincount = start_col	

# Read the data file and store the system UPN
with open(data_file_path) as UPNfile:
	UPNreader = csv.reader( UPNfile )
	next(UPNreader, None)
	UPNrow = next(UPNreader, None)
	UPN = UPNrow[UPN_col]																						

#Define standard Intel PIPE-FLO lineups via array
lineupnames = ["Connected Peak", "Connected Average", "Connected Bypass", "Committed Peak", "Committed Average", "Committed Bypass", "Pending Peak", "Pending Average", "Pending Bypass" ]

#Define arrays for system modeling methodology by system UPN
SysArray_Gasses = ['212', '216', '217', '218', '221', '401', '406', '403', '407', '408', '412', '417', '409']
SysArray_Exhaust = ['132', '133', '134', '138', '142']
SysArray_Wet = ['111', '112', '113', '115', '116', '117', '118', '201', '202', '204']
SysArray_UPW = ['238', '243', '244', '245'] 

#Generate the error log
poc = open(dir + '\\POC_Errors_' + model_name + '.csv','w')
poc.write('Lineup,Error Type,POC Name,Invalid Value,POC Type,POC Error Connected Peak, POC Error Pending Peak\n')

#Routine for Wet Mech type systems:
if UPN in SysArray_Wet:
	FPOC_errors = 0
	while lincount < start_col + 8:
		lineup = lineupnames[lincount - start_col]
		doc.set_current_lineup(lineup)
		errors = 0
		updates = 0
		with open( data_file_path ) as csvfile:

			reader = csv.reader( csvfile )
			next(reader, None)
		
			for data_col in reader:
		
				if not data_col: break
				sizing_valve_name = data_col[fpoc_col]																
				flow_value = data_col[lincount]																		#EDIT THIS VALUE DEPENDING ON WHAT COLUMN THE DEMANDS ARE IN
				if len(flow_value) == 0: flow_value = "0"															#checks the length of the string, if the string length is 0, then a 0 will be put in its place
						
				try:											 													#set environment to test values without aborting the rest of the script when errors are encountered
					p = doc.get_sizing_valve( sizing_valve_name )	 												#assign demand name to the variable 'p'
				except RuntimeError:  																				#check for runtime error (non-existent demand name)
					if lineup == lineupnames[0]:																	#Only identify FPOC name errors for first data column, "Connected Peak" lineup
						poc.write('ALL,Did not find sizing_valve,{0},,,{1},{2}\n'.format(sizing_valve_name,data_col[start_col],data_col[start_col+6]))		#Print to poc file. For FPOC error, record Connected and Pending Peak demand for reference
						FPOC_errors += 1  																				#adds 1 to the error count - OPTIONAL
					continue																						#return to the top of the for loop and continue with the next row of data
				
				try: 																								#set environment to test values
					sizing_valve_flow = float( flow_value ) 														#assign the value as a floating point number
				except ValueError: 																					#check for value type error which indicates bad data
					poc.write('{0},Invalid value type,{1},{2}\n'.format(lineup, sizing_valve_name, flow_value))		#PRINT TO POC FILE
					errors += 1
					continue 
				
				p.set_valve_settings(valve_settings(FCV, flow_rate(sizing_valve_flow,gpm ), pressure(0,psi)))
			
				updates += 1 																						#add 1 to the count of updated demands
			lincount += 1
			# Report Import status to the output window and calculate the given lineup for evaluation
			print('The {0} Lineup import has finished with {1} items updated and {2} lineup specific errors.\n'.format(lineup, updates, errors) ) 
			if lincount == start_col + 2: lincount += 1
			elif lincount == start_col + 5: lincount += 1
	print('The Load Import has finished with {0} FPOC assignment errors\n'.format(FPOC_errors) )
	print('Please view POC_errors_' + model_name + '.csv for details on the errors mentioned above.')
	print('This new file will be found in the same folder as the PipeFlo Extract csv.')

#Routine for UPW Type systems:
elif UPN in SysArray_UPW:
	FPOC_errors = 0
	bypass_col = start_col + 2
	while lincount < start_col + 8:
		lineup = lineupnames[lincount - start_col]
		doc.set_current_lineup(lineup)
		errors = 0
		updates = 0
		with open( data_file_path ) as csvfile:

			reader = csv.reader( csvfile )
			next(reader, None)
		
			for data_col in reader:
		
				if not data_col: break
				fpoc_name = data_col[fpoc_col]																			#EDIT THIS VALUE DEPENDING ON WHAT COLUMN DPOC_SEGMENT_FPOC IS
				if "BYPASS" in fpoc_name:																				#check to see if a UPW bypass valve
				
					sizing_valve_name = fpoc_name
					flow_value = data_col[bypass_col]																	#EDIT THIS VALUE DEPENDING ON WHAT COLUMN THE DEMANDS ARE IN
					if len(flow_value) == 0: flow_value = "0"															#checks the length of the string, if the string length is 0, then a 0 will be put in its place
						
					try:											 													#set environment to test values without aborting the rest of the script when errors are encountered
						b = doc.get_sizing_valve( sizing_valve_name )	 												#assign demand name to the variable 'p'
					except RuntimeError:  																				#check for runtime error (non-existent demand name)
						if lineup == lineupnames[0]:
							poc.write('ALL,Did not find sizing_valve,{0},,,{1},{2}\n'.format(sizing_valve_name,data_col[start_col],data_col[start_col+6]))				#Print to poc file. For FPOC error, record Connected and Pending Peak demand for reference
							FPOC_errors += 1  																					#adds 1 to the error count - OPTIONAL
						continue																						#return to the top of the for loop and continue with the next row of data
					
					try: 																								#set environment to test values
						sizing_valve_flow = float( flow_value ) 														#assign the value as a floating point number
					except ValueError: 																					#check for value type error which indicates bad data
						poc.write('{0},Invalid value type,{1},{2}\n'.format(lineup,sizing_valve_name, flow_value))		#PRINT TO POC FILE
						errors += 1
						continue 
					
					b.set_valve_settings(valve_settings(FCV, flow_rate(sizing_valve_flow,gpm ), pressure(0,psi)))
				
					updates += 1 																						#add 1 to the count of updated demands
				
				else:
				
					flow_demand_name = fpoc_name
					flow_value = data_col[lincount]																		#Average values are one column left of bypass values
					if len(flow_value) == 0: flow_value = "0"															#checks the length of the string, if the string length is 0, then a 0 will be put in its place
					bypass_name = fpoc_name + "-BY"
					bypass_value = data_col[bypass_col]
					if len(bypass_value) == 0: bypass_value = "0"														#checks the length of the string, if the string length is 0, then a 0 will be put in its place
				
					try:
						p = doc.get_flow_demand( flow_demand_name )
					except RuntimeError:
						if lineup == lineupnames[0]:
							poc.write('ALL,Did not find flow_demand,{0},,,{1},{2}\n'.format(flow_demand_name,data_col[start_col],data_col[start_col+6]))					#Print to poc file. For FPOC error, record Connected and Pending Peak demand for reference
							FPOC_errors += 1
						continue
				
					try: 																								#set environment to test values
						flow_demand_flow = float( flow_value ) 															#assign the value as a floating point number
					except ValueError: 																					#check for value type error which indicates bad data
						poc.write('{0},Invalid value type,{1},{2}\n'.format(lineup,flow_demand_name, flow_value))		#PRINT TO POC FILE
						errors += 1
						continue 
					
					p.set_flow_demand_operation( flow_demand_operation( set_flow_fd, flow_rate(flow_demand_flow, gpm ) ) )
				
					updates += 1 																						#add 1 to the count of updated demands
				
					try:											 													#set environment to test values without aborting the rest of the script when errors are encountered
						pb = doc.get_sizing_valve( bypass_name )	 													#assign demand name to the variable 'p'
					except RuntimeError:  																				#check for runtime error (non-existent demand name)
						if lineup == lineupnames[0]:
							poc.write('ALL,Did not find tool_bypass_valve,{0}\n'.format(bypass_name))					#PRINT TO POC FILE
							FPOC_errors += 1  																			#adds 1 to the error count - OPTIONAL
						continue																						#return to the top of the for loop and continue with the next row of data
					
					try: 																								#set environment to test values
						bypass_valve_flow = float( bypass_value ) 														#assign the value as a floating point number
					except ValueError: 																					#check for value type error which indicates bad data
						poc.write('{0},Invalid value type,{1},{2}\n'.format(lineup,bypass_name,bypass_value))			#PRINT TO POC FILE
						errors += 1
						continue 
					
					pb.set_valve_settings(valve_settings(FCV, flow_rate(bypass_valve_flow,gpm ), pressure(0,psi)))
				
			lincount += 1
			# Report Import status to the output window and calculate the given lineup for evaluation
			print('The {0} Lineup import has finished with {1} items updated and {2} lienup specifc errors.\n'.format(lineup, updates, errors) ) 
			if lincount == start_col + 2:                                                                               #If counter is on bypass column, skip column and set bypass column index to next data set
				lincount += 1
				bypass_col = start_col + 5
			elif lincount == start_col + 5: 
				lincount += 1 
				bypass_col = start_col + 8
	print('The Load Import has finished with {0} FPOC assignment errors\n'.format(FPOC_errors) )
	print('Please view POC_errors_' + model_name + '.csv for details on the errors mentioned above.')
	print('This new file will be found in the same folder as the PipeFlo Extract csv.')

#Routine for Gas/Exhaust type systems:
elif UPN in SysArray_Gasses or UPN in SysArray_Exhaust:
	FPOC_errors = 0
	if UPN in SysArray_Gasses:
		lineup_skip = 1
	elif UPN in SysArray_Exhaust:
		lineup_skip = 2																							#Value is set to 2 to skip Average and Bypass data columns for Exhaust. Set to 1 to only skip Bypass data column
	while lincount < start_col + 8:
		lineup = lineupnames[lincount - start_col]
		doc.set_current_lineup(lineup)
		errors = 0
		updates = 0
		
		with open( data_file_path ) as csvfile:

			reader = csv.reader( csvfile )
			next(reader, None)
		
			for data_col in reader:
				FPOC_type = ""
				if not data_col: break
				flow_demand_name = data_col[fpoc_col]															#EDIT THIS VALUE DEPENDING ON WHAT COLUMN DPOC_SEGMENT_FPOC IS
				flow_value = data_col[lincount]																	#Read the demand value according to the current lineup in iterator 		
				if flow_demand_name.endswith(" (P)"):															#Remove hot-tap status "(P)" from FPOC and identify FPOC type
					flow_demand_name = flow_demand_name[:-4]
					FPOC_type = "(P) HOT-TAP"
				elif flow_demand_name.endswith(" (VHT)"):															
					if len(flow_value) == 0: continue															#Skip unloaded virtual hot taps "(VHT)" FPOCs
					else: flow_demand_name = flow_demand_name[:-6]												#If virtual hot-tap is loaded, remove "(VHT)" status from FPOC and FPOC identify type
					FPOC_type = "(VHT) VIRTUAL HOT-TAP"
				else: flow_demand_name = flow_demand_name	
				if len(flow_value) == 0: flow_value = "0"														#checks the length of the string, if the string length is 0, then a 0 will be put in its place
				try:											 												#set environment to test values without aborting the rest of the script when errors are encountered
					p = doc.get_flow_demand( flow_demand_name )	 												#assign demand name to the variable 'p'
				except RuntimeError:  																			#check for runtime error (non-existent demand name)
					if lineup == lineupnames[0]:
						poc.write('ALL,Did not find flow_demand,{0},,{1},{2},{3}\n'.format(flow_demand_name,FPOC_type,data_col[start_col],data_col[start_col+6]))	#Print to poc file. For FPOC error, record Connected and Pending Peak demand for reference
						FPOC_errors += 1  																		#adds 1 to the error count - OPTIONAL
					continue																					#return to the top of the for loop and continue with the next row of data
						
				try: 																							#set environment to test values
					flow_demand_flow = float( flow_value ) 														#assign the value as a floating point number
				except ValueError: 																				#check for value type error which indicates bad data
					poc.write('{0},Invalid value type,{1},{2}\n'.format(lineup,flow_demand_name_raw, flow_value))	#PRINT TO POC FILE
					errors += 1
					continue 
				#Assign flow demand with flow unit depending on Gas or Exhaust system (standard vs volumetric flow units)
				if UPN in SysArray_Gasses:		
					p.set_flow_demand_operation( flow_demand_operation( set_flow_fd, flow_rate(flow_demand_flow, scfm ) ) )
				elif UPN in SysArray_Exhaust:
					p.set_flow_demand_operation( flow_demand_operation( set_flow_fd, flow_rate(flow_demand_flow, ft3pm ) ) )
				updates += 1 																					#add 1 to the count of updated demands
			lincount += 1
			# Report Import status to the output window and calculate the given lineup for evaluation
			print('The {0} Lineup import has finished with {1} items updated and {2} lineup specifc errors.\n'.format(lineup, updates, errors) ) 
			if lincount == start_col + 3 - lineup_skip: lincount += lineup_skip
			elif lincount == start_col + 6 - lineup_skip: lincount += lineup_skip
			elif lincount == start_col + 9 - lineup_skip: lincount += lineup_skip
	print('The Load Import has finished with {0} FPOC assignment errors\n'.format(FPOC_errors) )
	print('Please view POC_errors_' + model_name + '.csv for details on the errors mentioned above.')
	print('This new file will be found in the same folder as the PipeFlo Extract csv.')

else: print('System UPN is not recognized. Verify UPN {0} and see Help file for procedure to add UPN to script file.'.format(UPN))