import numpy as np
import matplotlib.pyplot as plt
import configparser
import os

######################      Default Values       ######################
class Case():
	def __init__(self, name):
		self.filename = name

	def write_config_file_from_GUI(self, inp_data):

		config = configparser.ConfigParser()

		config.add_section('inputs')

		config['inputs']['nseat_max'] = str(inp_data["nseat_max"])                         # Maximum number of seats
		config['inputs']['Range_MPL'] = str(inp_data['maximum range'])                     # Maximum range @ maximum payload
		config['inputs']['mass_OE'] = str(inp_data['empty mass'])                          # Operating empty mass
		config['inputs']['mass_Fuel_trip'] = str(inp_data['fuel'])                         # Burned ? mass @ average flight distance
		config['inputs']['mass_bat'] = str(inp_data['batteries'])                          # Battery mass needed
		config['inputs']['n_cycle_bat'] = str(inp_data['battery cycles'])                  # Battery cycles
		config['inputs']['Ebat_trip'] = str(inp_data['battery energy'])                    # Electric energy consumption @ average distance traveled
		config['inputs']['time_f_av'] = str(inp_data['flight time'])                       # Flight time @ average distance traveled 
		config['inputs']['FL'] = str(int(inp_data['flight level'])/100)                    # Flight level
		config['inputs']['time_taxi'] = str(float(inp_data['taxi time'])/60)               # Taxi time
		config['inputs']['time_TA'] = str(float(inp_data['turnaround time'])/60)             # Turnaround time

		config['inputs']['mass_wing'] = str(inp_data['main wing'])                         # Wing mass
		config['inputs']['mass_MLG'] = str(inp_data['main landing gear'])                  # Main landing gear mass
		config['inputs']['mass_NLG'] = str(inp_data['nose landing gear'])                  # Nose landing gear mass
		config['inputs']['mass_F'] = str(inp_data['fuselage'])                             # Fuselage mass
		config['inputs']['mass_V'] = str(inp_data['vertical stabilizer'])                  # Vertical Stabilizer mass
		config['inputs']['mass_H'] = str(inp_data['horizontal stabilizer'])                # Horizontal Stabilizer mass
		config['inputs']['mass_E'] = str(inp_data['engines'])                              # Engines mass

		config['inputs']['p_dist'] = str(float(inp_data['avg distance travel'])/100)         # Average distance traveled compared to RMPL
		config['inputs']['p_lfact'] = str(float(inp_data['avg load factor'])/100)            # Average load factor (suggested value)
		config['inputs']['numb_airc_build'] = str(inp_data['number of aircraft built'])    # Total number of aircraft built
		config['inputs']['Airc_life'] = str(inp_data["Airc_life"])                         # Number of years in the operational phase
		config['inputs']['dev_costs'] = str(inp_data["dev_costs"])                         # Development costs [IN BILLIONS]

		config['inputs']['mass_f_cruise'] = str(inp_data['fuel at cruise'])                # Burned kerosene mass for cruise flight
		config['inputs']['t_app'] = str(float(inp_data['approach time'])*60)                      # IN SECONDS
		config['inputs']['F_Flow_app'] = str(inp_data['approach fuel'])
		config['inputs']['t_TO'] = str(float(inp_data['take-off time'])*60)
		config['inputs']['F_Flow_TO'] = str(inp_data['take-off fuel'])
		config['inputs']['t_idl'] = str(float(inp_data['idle time'])*60)
		config['inputs']['F_Flow_idl'] = str(inp_data['idle fuel'])
		config['inputs']['t_Climb'] = str(float(inp_data['climb time'])*60)
		config['inputs']['F_Flow_Climb'] = str(inp_data['climb fuel'])

		config['inputs']['Elec_prod_mtd'] = str(inp_data["Elec_prod_mtd"])
		
		eis_date = int(inp_data["EIS_date"])

		if eis_date < 2030:
			config['inputs']['material_dist'] = str(1)                                  # material distribution selection. 1 for more aluminum, 2 for more composites
		else:
			config['inputs']['material_dist'] = str(2)

		config['inputs']['palo_PAX'] = str(float(inp_data["palo_PAX"])/100)             # Percentage of passenger mass on total payload mass of passenger aircraft [%]	
		config['inputs']['palo_PAX_FH'] = str(float(inp_data["palo_PAX_FH"])/100)       # Percentage of passengers mass on total payload mass at airports [%]
		config['inputs']['p_seat'] = str(float(inp_data["p_seat"])/100)                 # Average number of PAX per flight [%]	
		config['inputs']['num_flights_y'] = str(inp_data["num_flights_y"])              # Number of flights per year (on average distance traveled) [-]


		config['inputs']['type_of_analys'] = str(1)                                     # egaliterian, hierarhist or individualist and europe or world  1, 2, 3 and 4, 5, 6 respectively
		config['inputs']['type_of_weight'] = str(inp_data["type_of_weight"])            # egaliterian, hierarhist or individualist 1, 2, 3

		with open("{0}.config".format(self.filename), 'w') as configfile:
			config.write(configfile)

		return -1

	def Write_config_file(self, elec_prod_mtd):
		f_name = self.filename       # your lca input file for each case
	
		with open(f_name) as f:
			data = f.readlines()
		f.close()

		inpts = {}

		for line in data:
			tmp = line.strip('\n').split(',')
			inpts[tmp[0]] = float(tmp[1])

		config = configparser.ConfigParser()

		config.add_section('inputs')
 
		config['inputs']['nseat_max'] = str(19)                                         # Maximum number of seats
		config['inputs']['Range_MPL'] = str(inpts['maximum range'])                     # Maximum range @ maximum payload
		config['inputs']['mass_OE'] = str(inpts['empty mass'])                          # Operating empty mass
		config['inputs']['mass_Fuel_trip'] = str(inpts['fuel'])                         # Burned ? mass @ average flight distance
		config['inputs']['mass_bat'] = str(inpts['batteries'])                          # Battery mass needed
		config['inputs']['n_cycle_bat'] = str(inpts['battery cycles'])                  # Battery cycles
		config['inputs']['Ebat_trip'] = str(inpts['battery energy'])                    # Electric energy consumption @ average distance traveled
		config['inputs']['time_f_av'] = str(inpts['flight time'])                       # Flight time @ average distance traveled 
		config['inputs']['FL'] = str(inpts['flight level'])                             # Flight level
		config['inputs']['time_taxi'] = str(inpts['taxi time'])                         # Taxi time
		config['inputs']['time_TA'] = str(inpts['turnaround time'])                     # Turnaround time
 
		config['inputs']['mass_wing'] = str(inpts['main wing'])                         # Wing mass
		config['inputs']['mass_MLG'] = str(inpts['main landing gear'])                  # Main landing gear mass
		config['inputs']['mass_NLG'] = str(inpts['nose landing gear'])                  # Nose landing gear mass
		config['inputs']['mass_F'] = str(inpts['fuselage'])                             # Fuselage mass
		config['inputs']['mass_V'] = str(inpts['vertical stabilizer'])                  # Vertical Stabilizer mass
		config['inputs']['mass_H'] = str(inpts['horizontal stabilizer'])                # Horizontal Stabilizer mass
		config['inputs']['mass_E'] = str(inpts['engines'])                              # Engines mass

		config['inputs']['p_dist'] = str(inpts['avg distance travel'])                  # Average distance traveled compared to RMPL
		config['inputs']['p_lfact'] = str(inpts['avg load factor'])                     # Average load factor (suggested value)
		config['inputs']['numb_airc_build'] = str(inpts['number of aircraft built'])    # Total number of aircraft built
		config['inputs']['Airc_life'] = str(20)                                         # Number of years in the operational phase
		config['inputs']['dev_costs'] = str(2)                                        	# Development costs [IN BILLIONS]

		config['inputs']['mass_f_cruise'] = str(inpts['fuel at cruise'])                # Burned kerosene mass for cruise flight
		config['inputs']['t_app'] = str(inpts['approach time']*60)                      # IN SECONDS
		config['inputs']['F_Flow_app'] = str(inpts['approach fuel'])
		config['inputs']['t_TO'] = str(inpts['take-off time']*60)
		config['inputs']['F_Flow_TO'] = str(inpts['take-off fuel'])
		config['inputs']['t_idl'] = str(inpts['idle time']*60)
		config['inputs']['F_Flow_idl'] = str(inpts['idle fuel'])
		config['inputs']['t_Climb'] = str(inpts['climb time']*60)
		config['inputs']['F_Flow_Climb'] = str(inpts['climb fuel'])

		config['inputs']['Elec_prod_mtd'] = str(elec_prod_mtd)                          # Method of electric energy production. 1 is for renewables
		eis_date = int(self.filename.split("_")[2])
		if eis_date < 2030:
			config['inputs']['material_dist'] = str(1)                                  # material distribution selection. 1 for more aluminum, 2 for more composites
		else:
			config['inputs']['material_dist'] = str(2)
		config['inputs']['palo_PAX'] = str(0.82)                                        # Percentage of passenger mass on total payload mass of passenger aircraft [%]	
		config['inputs']['palo_PAX_FH'] = str(0.7)                                      # Percentage of passengers mass on total payload mass at airports [%]
		config['inputs']['p_seat'] = str(0.85)                                          # Average number of PAX per flight [%]	
		config['inputs']['num_flights_y'] = str(1630)                                   # Number of flights per year (on average distance traveled) [-]


		config['inputs']['type_of_analys'] = str(1)                                     # egaliterian, hierarhist or individualist and europe or world  1, 2, 3 and 4, 5, 6 respectively
		config['inputs']['type_of_weight'] = str(1)                                     # egaliterian, hierarhist or individualist 1, 2, 3

		with open("{0}.config".format(self.filename), 'w') as configfile:
			config.write(configfile)

		return -1

	def Read_config_file(self):

		config = configparser.ConfigParser()

		config.read("{0}.config".format(self.filename))


		self.nseat_max= float(config['inputs']['nseat_max'])     # Maximum number of seats
		self.Range_MPL= float(config['inputs']['Range_MPL'])     # Maximum range @ maximum payload
		self.mass_OE= float(config['inputs']['mass_OE'])		    # Operating empty mass
		self.mass_Fuel_trip= float(config['inputs']['mass_Fuel_trip'])   # Burned ? mass @ average flight distance
		self.mass_bat= float(config['inputs']['mass_bat'])	    # Battery mass needed
		self.n_cycle_bat= float(config['inputs']['n_cycle_bat']) # Battery cycles
		self.Ebat_trip= float(config['inputs']['Ebat_trip'])		# Electric energy consumption @ average distance traveled
		self.time_f_av= float(config['inputs']['time_f_av'])	    # Flight time @ average distance traveled 
		self.FL= float(config['inputs']['FL'])					# Flight level
		self.time_taxi= float(config['inputs']['time_taxi'])     # Taxi time
		self.time_TA= float(config['inputs']['time_TA'])         # Turnaround time
 
		self.mass_wing= float(config['inputs']['mass_wing'])     # Wing mass
		self.mass_MLG= float(config['inputs']['mass_MLG'])	    # Main landing gear mass
		self.mass_NLG= float(config['inputs']['mass_NLG'])	    # Nose landing gear mass
		self.mass_F= float(config['inputs']['mass_F'])			# Fuselage mass
		self.mass_V= float(config['inputs']['mass_V'])			# Vertical Stabilizer mass
		self.mass_H= float(config['inputs']['mass_H'])			# Horizontal Stabilizer mass
		self.mass_E= float(config['inputs']['mass_E'])			# Engines mass

		self.p_dist= float(config['inputs']['p_dist'])           # Average distance traveled compared to RMPL
		self.p_lfact= float(config['inputs']['p_lfact'])         # Average load factor (suggested value)
		self.numb_airc_build= float(config['inputs']['numb_airc_build'])  # Total number of aircraft built
		self.Airc_life= float(config['inputs']['Airc_life'])     # Number of years in the operational phase
		self.dev_costs= float(config['inputs']['dev_costs'])     # Development costs
		self.mass_f_cruise= float(config['inputs']['mass_f_cruise'])    # Burned kerosene mass for cruise flight

		self.t_app= float(config['inputs']['t_app'])
		self.F_Flow_app= float(config['inputs']['F_Flow_app'])
		self.t_TO= float(config['inputs']['t_TO'])
		self.F_Flow_TO= float(config['inputs']['F_Flow_TO'])
		self.t_idl= float(config['inputs']['t_idl'])
		self.F_Flow_idl= float(config['inputs']['F_Flow_idl'])
		self.t_Climb= float(config['inputs']['t_Climb'])
		self.F_Flow_Climb= float(config['inputs']['F_Flow_Climb'])

		self.Elec_prod_mtd= float(config['inputs']['Elec_prod_mtd'])    # Method of electric energy production
		self.material_dist= float(config['inputs']['material_dist'])    # material distribution selection. 1 for more aluminum, 2 for more composites
		self.palo_PAX= float(config['inputs']['palo_PAX'])			   # Percentage of passenger mass on total payload mass of passenger aircraft [%]	
		self.palo_PAX_FH= float(config['inputs']['palo_PAX_FH'])		   # Percentage of passengers mass on total payload mass at airports [%]
		self.p_seat= float(config['inputs']['p_seat'])				   # Average number of PAX per flight [%]	
		self.num_flights_y= float(config['inputs']['num_flights_y'])    # Number of flights per year (on average distance traveled) [-]


		self.type_of_analys= float(config['inputs']['type_of_analys'])  # egaliterian, hierarhist or individualist and europe or world  1, 2, 3 and 4, 5, 6 respectively
		self.type_of_weight= float(config['inputs']['type_of_weight'])  # egaliterian, hierarhist or individualist  1, 2, 3 

		if self.type_of_weight == 0:
			self.weight_eco = 250
			self.weight_h = 550
			self.weight_r = 200
		elif self.type_of_weight == 1:
			self.weight_eco = 400
			self.weight_h = 300
			self.weight_r = 300
		else:
			self.weight_eco = 500
			self.weight_h = 300
			self.weight_r = 200

		return -1

	

	def Execution(self):

		n_PAX =	self.nseat_max * self.p_seat * self.p_lfact		# Average number of PAX per flight
		avg_dist_miles =self.p_dist * self.Range_MPL			# distance traveled per flight [NM]	


		PKM_f = n_PAX * avg_dist_miles * 1.852		# Average number of passenger-kilometers per flight	[PKM/flight] 1.852 is nautical mile to km	
		PKM_life = n_PAX * self.num_flights_y * avg_dist_miles*1.852 * self.Airc_life 	# Average number of passenger-kilometers in the operational life	
		self.pkm_life = PKM_life
		PKMfam = PKM_life * self.numb_airc_build			# Average number of passenger-kilometers per aircraft fleet	
						
	
						




		#######################################################################
		#######################################################################
		###############   Inventory analysis calculation   ####################
		#######################################################################
		#######################################################################



		### for the arrays in order to store the results of the inventory analysis we will follow the method below:
		### an array of 20 columns will be used and the colums will be as follows:

		### CO2 .. NOX .. CO .. SO2 .. 02 .. H20 .. HC .. CH4 .. PM10 .. Natural_gas .. cruide_oil .. hard_coal .. brown_coal .. copper_ore .. Fe .. Mn   Alum  Titanium  Nickel  Lithium
		###  0      1      2     3      4     5     6      7      8           9             10            11            12           13        14     15    16	  17		18		19
		###  .      .      .     .      .     .     .      .      .           .              .            .             .             .        .      .		.	   .		.		.
		###  .      .      .     .      .     .     .      .      .           .              .            .             .             .        .      .		.	   .		.		.
			
		### So, with matrix[0] you take CO2, with matrix[10] you get cruide oil etc.



		#######################################################################
		######################    Design/development     ######################
		#######################################################################


		######################      Computer usage       ######################
		#######################################################################
		######################      Default Values       ######################
		p_ing = 0.75						# Estimated share of engineering costs from total costs [%]
		cost_ing = 30						# cost of engineering hour [euro/hour)
		h_ing = self.dev_costs * 1E+9 * p_ing/ cost_ing	# Engineering Development Hours	[h]
		E= h_ing * 0.2			# Electric energy consumption of an office computer for the project for a 0.2 kW computer [kWh]

		IOF_CO2 = 0.56			# Emission factor CO2 [kg/kWh]
		IOF_hard_coal = 0.081	# Emission factor Hard coal; 26.3 MJ/kg	[kg/kWh]
		IOF_natural_gas = 0.041	# Emission factor Natural gas; 44.1 MJ/kg	[kg/kWh]
		IOF_brown_coal = 0.12	# Emission factor Brown coal; 11.9 MJ/kg	[kg/kWh]
		IOF_crude_oil = 0.017	# Emission factor Crude oil; 42.3 MJ/kg	[kg/kWh]
		IOF_SO2 = 0.0033		# Emission factor SO2	[kg/kWh]


		self.xPKM_computers = [0]*20
		self.xPKM_computers[0] = IOF_CO2 * E * 1000 / PKMfam * self.palo_PAX			# CO2 per PKM [g/PKM]
		self.xPKM_computers[3] = IOF_SO2 * E  * 1000 / PKMfam * self.palo_PAX		# SO2 per PKM	[g/PKM]
		self.xPKM_computers[9] = IOF_natural_gas * E  * 1000 / PKMfam * self.palo_PAX	# Natural gas; 44.1 MJ/kg per PKM [g/PKM]
		self.xPKM_computers[10] = IOF_crude_oil * E  * 1000 / PKMfam * self.palo_PAX	# Crude oil; 42.3 MJ/kg per PKM	[g/PKM]
		self.xPKM_computers[11] = IOF_hard_coal * E  * 1000 / PKMfam * self.palo_PAX 	# Hard coal; 26.3 MJ/kg per PKM [g/PKM]
		self.xPKM_computers[12] = IOF_brown_coal * E  * 1000 / PKMfam * self.palo_PAX	# Brown coal; 11.9 MJ/kg per PKM [g/PKM]



		######################    Wind tunel testing     ######################
		#######################################################################
		######################      Default Values       ######################

		nWT_d = 1671			# Number of wind tunnel test days -- STATISTICS	[days]
		IOF_CO2_eq = 18600		# Carbon footprint per wind tunnel test year --	STATISTICS[tones CO2 eq/year]

		######################   inventory calculation   ######################

		xCO2 = 	IOF_CO2_eq * nWT_d / 365		# Carbon footprint per aircraft development	[t CO2 eq/development]

		self.xPKM_windT = [0]*20
		self.xPKM_windT[0] = xCO2 * 1000000 / PKMfam * self.palo_PAX			# CO2 per PKM [g/PKM]




		
		##################### Use of Production Facilities ####################
		#######################################################################
		######################      Default Values       ######################

		IOF_CO2 = 5728			# Emission factor CO2 [kg/sold seat]
		IOF_hard_coal = 491		# Emission factor Hard coal; 26.3 MJ/kg	[kg/sold seat]
		IOF_natural_gas = 1337	# Emission factor Natural gas; 44.1 MJ/kg [kg/sold seat]
		IOF_brown_coal = 1829	# Emission factor Brown coal; 11.9 MJ/kg [kg/sold seat]
		IOF_crude_oil = 1053	# Emission factor Crude oil; 42.3 MJ/kg [kg/sold seat]
		IOF_SO2 = 68			# Emission factor SO2	[kg/kWh]


		######################   inventory calculation   ######################

		self.xPKM_Prod_fac = [0]*20
		self.xPKM_Prod_fac[0] = n_PAX * IOF_CO2 * 1000 / PKM_life * self.palo_PAX			# CO2 per PKM [g/PKM]
		self.xPKM_Prod_fac[3] = n_PAX * IOF_SO2 * 1000 / PKM_life * self.palo_PAX		# SO2 per PKM	[g/PKM]
		self.xPKM_Prod_fac[9] =  n_PAX * IOF_natural_gas * 1000 / PKM_life * self.palo_PAX	# Natural gas; 44.1 MJ/kg per PKM [g/PKM]
		self.xPKM_Prod_fac[10] = n_PAX * IOF_crude_oil * 1000 / PKM_life * self.palo_PAX	# Crude oil; 42.3 MJ/kg per PKM	[g/PKM]
		self.xPKM_Prod_fac[11] = n_PAX * IOF_hard_coal * 1000 / PKM_life * self.palo_PAX 	# Hard coal; 26.3 MJ/kg per PKM [g/PKM]
		self.xPKM_Prod_fac[12] = n_PAX * IOF_brown_coal * 1000 / PKM_life * self.palo_PAX	# Brown coal; 11.9 MJ/kg per PKM [g/PKM]




		######################    Material production    ######################
		#######################################################################
		######################      Default Values       ######################

		####	Share of						
		####						Aluminum	Steel	CFRP	Titanium	GFRP	Nickel	Misc.
		####	Wing					84%		3%		8%			5%			
		####	Main landing gear		5%		89%		1%			5%			
		####	Nose landing gear		5%		84%		7%			5%			
		####	Fuselage				85%		1%		6%			5%		0%		  0%	 3%
		####	Vertical Stabilizer		3%		0%		55%			0%		42%		
		####	Horizontal Stabilizer	5%		0%		92%			0%		3%		
		####	Engines					5%		38%		11%			2%		21%		  16%	  7%

		####	mass_wing               #Wing mass
		####	mass_MLG                #Main landing gear mass
		####	mass_NLG                #Nose landing gear mass
		####	mass_F                  #Fuselage mass
		####	mass_V                  #Vertical Stabilizer mass
		####	mass_H                  #Horizontal Stabilizer mass
		####	mass_E                  #Engines mass




		######################   inventory calculation   ######################
		# computing the mass per material of the known components based on statistical distribution 

		if(self.material_dist == 2):
				aluminum = self.mass_wing*0.55 + self.mass_MLG *0.05 + self.mass_NLG*0.05 + self.mass_F*0.7 + self.mass_V*0.03 + self.mass_H*0.05 + self.mass_E*0.05 # aluminum mass per aircraft
				steel = self.mass_wing*0.03 + self.mass_MLG *0.89 + self.mass_NLG*0.84 + self.mass_F*0.01 + self.mass_V*0 + self.mass_H*0 + self.mass_E*0.38 # steel mass
				CFRP = self.mass_wing*0.37 + self.mass_MLG *0.01 + self.mass_NLG*0.07 + self.mass_F*0.24 + self.mass_V*0.55 + self.mass_H*0.92 + self.mass_E*0.11 # CFRP mass
				Titanium = self.mass_wing*0.05 + self.mass_MLG *0.05 + self.mass_NLG*0.05 + self.mass_F*0.05 + self.mass_V*0 + self.mass_H*0 + self.mass_E*0.02 # Titanium mass
				GFRP = self.mass_V*0.42 + self.mass_H*0.03 + self.mass_E*0.21 # GFRP mass
				Nickel = self.mass_E*0.16 # Nickel mass
				Misc = self.mass_F*0.03 + self.mass_E*0.07 # Misc mass
		else:
				aluminum = self.mass_wing*0.84 + self.mass_MLG *0.05 + self.mass_NLG*0.05 + self.mass_F*0.85 + self.mass_V*0.03 + self.mass_H*0.05 + self.mass_E*0.05 # aluminum mass per aircraft
				steel = self.mass_wing*0.03 + self.mass_MLG *0.89 + self.mass_NLG*0.84 + self.mass_F*0.01 + self.mass_V*0 + self.mass_H*0 + self.mass_E*0.38 # steel mass
				CFRP = self.mass_wing*0.08 + self.mass_MLG *0.01 + self.mass_NLG*0.07 + self.mass_F*0.06 + self.mass_V*0.55 + self.mass_H*0.92 + self.mass_E*0.11 # CFRP mass
				Titanium = self.mass_wing*0.05 + self.mass_MLG *0.05 + self.mass_NLG*0.05 + self.mass_F*0.05 + self.mass_V*0 + self.mass_H*0 + self.mass_E*0.02 # Titanium mass
				GFRP = self.mass_V*0.42 + self.mass_H*0.03 + self.mass_E*0.21 # GFRP mass
				Nickel = self.mass_E*0.16 # Nickel mass
				Misc = self.mass_F*0.03 + self.mass_E*0.07 # Misc mass



		##  Copper = mass_bat * a given number

		tot_mass =aluminum + steel +  CFRP + Titanium + GFRP + Nickel + Misc   # known mass distribution
		rem_mass = self.mass_OE - tot_mass		# remaining mass undistributed

		aluminum += aluminum / tot_mass * rem_mass
		steel += steel / tot_mass * rem_mass
		CFRP += CFRP / tot_mass  * rem_mass
		Titanium += Titanium / tot_mass * rem_mass
		GFRP += GFRP / tot_mass * rem_mass
		Nickel += Nickel / tot_mass * rem_mass
		Misc += Misc / tot_mass  * rem_mass

		####	Percentage of reused aluminum	2%
		####	Percentage of reused steel		56%
		####	Percentage of reused titanium	2%
		####	Percentage of reused composites	5%
		# remove the reused material percentage
		aluminum *= (1-0.02)
		steel *= (1-0.56)
		CFRP *= (1-0.05)
		GFRP *= (1-0.05)
		Titanium *= (1-0.02)
		Misc *= (1-0.02)

		Composites = CFRP + GFRP
		############    !!!!!!!!!!!!!!!!!!!!       ##################
		############ there is no info for Titanium ##################
		############ neither for misc.             ##################
		############    !!!!!!!!!!!!!!!!!!!!       ##################

		####     aluminum    #####

		IOF_CO2_a = 2539			# Emission factor CO2 [kg/t]
		IOF_hard_coal_a = 247		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		IOF_natural_gas_a = 327	# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		IOF_brown_coal_a = 211	# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		IOF_crude_oil_a = 168 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		IOF_SO2_a = 8.7			# Emission factor SO2	[kg/t]
		IOF_PM10_a = 1.6			# Emission factor PM10  [kg/t]


		####     composites    #####

		IOF_CO2_c = 7900			# Emission factor CO2 [kg/t]
		IOF_hard_coal_c = 10656		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		IOF_natural_gas_c = 8251	# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		IOF_brown_coal_c = 15139	# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		IOF_crude_oil_c = 2263 		# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		IOF_SO2_c = 418				# Emission factor SO2	[kg/t]
		IOF_PM10_c = 0			# Emission factor PM10  [kg/t]

		####     steel    #####

		IOF_CO2_s = 1454			# Emission factor CO2 [kg/t]
		IOF_hard_coal_s = 555		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		IOF_natural_gas_s = 63		# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		IOF_fe_s = 487				# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		IOF_mn_s = 4.6			 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		IOF_PM10_s = 1.2			# Emission factor PM10  [kg/t]
		IOF_SO2_s = 0				# Emission factor SO2	[kg/t]
		IOF_crude_oil_s = 0 		# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		IOF_brown_coal_s = 0		# Emission factor Brown coal; 11.9 MJ/kg [kg/t]

		####     Titanium    #####

		IOF_CO2_t = 0			# Emission factor CO2 [kg/t]
		IOF_hard_coal_t = 0		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		IOF_natural_gas_t = 0	# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		IOF_brown_coal_t = 0	# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		IOF_crude_oil_t = 0 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		IOF_SO2_t = 0			# Emission factor SO2	[kg/t]
		IOF_PM10_t = 0			# Emission factor PM10  [kg/t]

		########################################

		###### Calculate the mass for the following and find also the emission factor in order to enhance the model. Then add the contribution to the following equations
		###### Generally to do that you will need to change all the file, especially the xPKM list will need to have extra columns.

		##Copper = 

		##Lithium = 0.084 * Ebat_trip # based on statistics see in mineral usage at the end of the file
		######      Copper     #####

		##IOF_CO2_cop = 0			# Emission factor CO2 [kg/t]
		##IOF_hard_coal_cop = 0		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		##IOF_natural_gas_cop = 0	# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		##IOF_brown_coal_cop = 0	# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		##IOF_crude_oil_cop = 0 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		##IOF_SO2_cop = 0			# Emission factor SO2	[kg/t]
		##IOF_PM10_cop = 0			# Emission factor PM10  [kg/t]

		######      Nickel     #####

		##IOF_CO2_n = 0			# Emission factor CO2 [kg/t]
		##IOF_hard_coal_n = 0		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		##IOF_natural_gas_n = 0	# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		##IOF_brown_coal_n = 0	# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		##IOF_crude_oil_n = 0 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		##IOF_SO2_n = 0			# Emission factor SO2	[kg/t]
		##IOF_PM10_n = 0			# Emission factor PM10  [kg/t]

		######      Lithium     #####

		##IOF_CO2_l = 0			# Emission factor CO2 [kg/t]
		##IOF_hard_coal_l = 0		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		##IOF_natural_gas_l = 0	# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		##IOF_brown_coal_l = 0	# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		##IOF_crude_oil_l = 0 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		##IOF_SO2_l = 0			# Emission factor SO2	[kg/t]
		##IOF_PM10_l = 0			# Emission factor PM10  [kg/t]

		## self.xPKM_materials[13] = Copper / PKM_life * self.palo_PAX			# Mn per PKM [g/PKM]


		self.xPKM_materials = [0]*20
		self.xPKM_materials[0] = (IOF_CO2_a * aluminum + IOF_CO2_c * Composites + IOF_CO2_s * steel + IOF_CO2_t * Titanium)/ PKM_life * self.palo_PAX			# CO2 per PKM [g/PKM]
		self.xPKM_materials[3] = (IOF_SO2_a * aluminum + IOF_SO2_c * Composites + IOF_SO2_s * steel + IOF_SO2_t * Titanium)/ PKM_life * self.palo_PAX			# SO2 per PKM [g/PKM]
		self.xPKM_materials[8] = (IOF_PM10_a * aluminum + IOF_PM10_c * Composites + IOF_PM10_s * steel + IOF_PM10_t * Titanium)/ PKM_life * self.palo_PAX			# PM10 per PKM [g/PKM]
		self.xPKM_materials[9] = (IOF_natural_gas_a * aluminum + IOF_natural_gas_c * Composites + IOF_natural_gas_s * steel + IOF_natural_gas_t * Titanium)/ PKM_life * self.palo_PAX			# natural gas per PKM [g/PKM]
		self.xPKM_materials[10] = (IOF_crude_oil_a * aluminum + IOF_crude_oil_c * Composites + IOF_crude_oil_s * steel + IOF_crude_oil_t * Titanium)/ PKM_life * self.palo_PAX			# cruide oil per PKM [g/PKM]
		self.xPKM_materials[11] = (IOF_hard_coal_a * aluminum + IOF_hard_coal_c * Composites + IOF_hard_coal_s * steel + IOF_hard_coal_t * Titanium)/ PKM_life * self.palo_PAX			# hard coal per PKM [g/PKM]
		self.xPKM_materials[12] = (IOF_brown_coal_a * aluminum + IOF_brown_coal_c * Composites + IOF_brown_coal_s * steel + IOF_brown_coal_t * Titanium)/ PKM_life * self.palo_PAX			# brown coal per PKM [g/PKM]
		self.xPKM_materials[14] = ( IOF_fe_s * steel )/ PKM_life * self.palo_PAX			# Fe per PKM [g/PKM]
		self.xPKM_materials[15] = ( IOF_mn_s * steel )/ PKM_life * self.palo_PAX			# Mn per PKM [g/PKM]
		
	### Christos Nasoulis https://www.fedex.com/content/dam/fedex/us-united-states/services/LithiumBattery_JobAid.pdffor 84g of lithium per kWh

		self.xPKM_materials[16] = (0.95 * aluminum )/ PKM_life * self.palo_PAX * 1000 # multiplied by 1000 to make the kg to g
		self.xPKM_materials[17] = (0.9 * Titanium)/ PKM_life * self.palo_PAX *1000
		self.xPKM_materials[18] = Nickel / PKM_life * self.palo_PAX * 1000

		# print("The electric engines are not taken into account for this")

		######################    Battery production     ######################
		#######################################################################
		######################      Default Values       ######################

		IOF_hard_coal = 1.681		# Emission factor Hard coal; 26.3 MJ/kg	[kg/kWh]
		IOF_natural_gas = 1.1	# Emission factor Natural gas; 44.1 MJ/kg [kg/kWh]
		IOF_copper_ore = 1.03	# Emission factor Brown coal; 11.9 MJ/kg [kg/kWh]
		IOF_crude_oil = 0.778 	# Emission factor Crude oil; 42.3 MJ/kg [kg/kWh]


		######################   inventory calculation   ######################
		if(self.material_dist == 2): ## Based on the fact that we are expecting more than half the weight for the same Wh in the future...
			self.xPKM_battery_prod = [0]*20 
			self.xPKM_battery_prod[9] = IOF_natural_gas * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKM_f ) * self.palo_PAX * 0.45		# natural gas per PKM [g/PKM]
			self.xPKM_battery_prod[10] = IOF_crude_oil * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKM_f ) * self.palo_PAX * 0.45			# cruide oil per PKM [g/PKM]
			self.xPKM_battery_prod[11] = IOF_hard_coal * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKM_f ) * self.palo_PAX * 0.45			# hard coal per PKM [g/PKM]
			self.xPKM_battery_prod[13] = IOF_copper_ore * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKM_f ) * self.palo_PAX * 0.45		# copper ore per PKM [g/PKM]
			self.xPKM_battery_prod[19] = 84 * self.Ebat_trip / (self.n_cycle_bat *PKM_f ) * self.palo_PAX * 0.45 ### 
		else:
			self.xPKM_battery_prod = [0]*20 
			self.xPKM_battery_prod[9] = IOF_natural_gas * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKM_f ) * self.palo_PAX 		# natural gas per PKM [g/PKM]
			self.xPKM_battery_prod[10] = IOF_crude_oil * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKM_f ) * self.palo_PAX 		# cruide oil per PKM [g/PKM]
			self.xPKM_battery_prod[11] = IOF_hard_coal * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKM_f ) * self.palo_PAX		# hard coal per PKM [g/PKM]
			self.xPKM_battery_prod[13] = IOF_copper_ore * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKM_f ) * self.palo_PAX 		# copper ore per PKM [g/PKM]
			self.xPKM_battery_prod[19] = 84 * self.Ebat_trip / (self.n_cycle_bat *PKM_f ) * self.palo_PAX * 0.45 ### 



		######################      Flight testing       ######################
		#######################################################################
		######################      Default Values       ######################

		n_airc_test = 5		# Number of test aircraft[-]
		n_test_h = 3700		# Number of total flight test hours[h]

		fuel_burned_test = self.mass_Fuel_trip/self.time_f_av * n_test_h		# total fuel burned [kg]
		elec_burned_test = self.Ebat_trip/self.time_f_av	* n_test_h			# electricity burned [kW]

		#kerosene burned
		IOF_CO2 = 3.15			# Emission factor CO2 [kg/kg of fuel]
		IOF_O2 = 3.4		
		IOF_H2O = 1.23	
		IOF_SO2 = 0.00084	
		IOF_HC = 0	
		IOF_CO = 0.00281			
		IOF_NOx = 0.01594	

		self.xPKM_test = [0]*20
		self.xPKM_test[0] = fuel_burned_test * IOF_CO2 * 1000 / PKMfam * self.palo_PAX			
		self.xPKM_test[1] = fuel_burned_test * IOF_NOx * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[2] = fuel_burned_test * IOF_CO * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[3] = fuel_burned_test * IOF_SO2 * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[4] = fuel_burned_test * IOF_O2 * 1000 / PKMfam * self.palo_PAX			
		self.xPKM_test[5] = fuel_burned_test * IOF_H2O * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[6] = fuel_burned_test * IOF_HC * 1000 / PKMfam * self.palo_PAX			


		#kerosene produced
		IOF_CO2 = 0.259		
		IOF_hard_coal = 0		
		IOF_natural_gas = 0.0579	
		IOF_brown_coal = 0	
		IOF_crude_oil = 1.11 	# Emission factor Crude oil; 42.3 MJ/kg [kg/kg]
		IOF_SO2 = 0.00158		
		IOF_CH4 = 0.0033			



		self.xPKM_test[0] += fuel_burned_test * IOF_CO2 * 1000 / PKMfam * self.palo_PAX			
		self.xPKM_test[11] += fuel_burned_test * IOF_hard_coal * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[9] += fuel_burned_test * IOF_natural_gas * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[3] += fuel_burned_test * IOF_SO2 * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[12] += fuel_burned_test * IOF_brown_coal * 1000 / PKMfam * self.palo_PAX			
		self.xPKM_test[7] += fuel_burned_test * IOF_CH4 * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[10] += fuel_burned_test * IOF_crude_oil * 1000 / PKMfam * self.palo_PAX	


		#electricity produced
		## 1 is for renewables
		if self.Elec_prod_mtd == 1:
				IOF_CO2 = 0.029		
				IOF_hard_coal = 0.00055		
				IOF_natural_gas = 0.0018	
				IOF_brown_coal = 0.00045	
				IOF_crude_oil = 0.0024 	# Emission factor Crude oil; 42.3 MJ/kg [kg/kW]
				IOF_SO2 = 0		
				IOF_CH4 = 0.000048			
		else:
				IOF_CO2 = 0.56		
				IOF_hard_coal = 0.081	
				IOF_natural_gas = 0.041	
				IOF_brown_coal = 0.12	
				IOF_crude_oil = 0.017 	# Emission factor Crude oil; 42.3 MJ/kg [kg/kW]
				IOF_SO2 = 0.0033		
				IOF_CH4 = 0			


		self.xPKM_test[0] += self.Ebat_trip * IOF_CO2 * 1000 / PKMfam * self.palo_PAX			
		self.xPKM_test[11] += self.Ebat_trip * IOF_hard_coal * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[9] += self.Ebat_trip * IOF_natural_gas * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[3] += self.Ebat_trip * IOF_SO2 * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[12] += self.Ebat_trip * IOF_brown_coal * 1000 / PKMfam * self.palo_PAX			
		self.xPKM_test[7] += self.Ebat_trip * IOF_CH4 * 1000 / PKMfam * self.palo_PAX		
		self.xPKM_test[10] += self.Ebat_trip * IOF_crude_oil * 1000 / PKMfam * self.palo_PAX	



		####     aluminum    #####

		IOF_CO2_a = 2539			# Emission factor CO2 [kg/t]
		IOF_hard_coal_a = 247		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		IOF_natural_gas_a = 327	# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		IOF_brown_coal_a = 211	# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		IOF_crude_oil_a = 168 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		IOF_SO2_a = 8.7			# Emission factor SO2	[kg/t]
		IOF_PM10_a = 1.6			# Emission factor PM10  [kg/t]


		####     composites    #####

		IOF_CO2_c = 7900			# Emission factor CO2 [kg/t]
		IOF_hard_coal_c = 10656		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		IOF_natural_gas_c = 8251	# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		IOF_brown_coal_c = 15139	# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		IOF_crude_oil_c = 2263 		# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		IOF_SO2_c = 418				# Emission factor SO2	[kg/t]
		IOF_PM10_c = 0			# Emission factor PM10  [kg/t]

		####     steel    #####

		IOF_CO2_s = 1454			# Emission factor CO2 [kg/t]
		IOF_hard_coal_s = 555		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		IOF_natural_gas_s = 63		# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		IOF_fe_s = 487				# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		IOF_mn_s = 4.6			 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		IOF_PM10_a = 1.2			# Emission factor PM10  [kg/t]
		IOF_SO2_s = 0				# Emission factor SO2	[kg/t]
		IOF_crude_oil_s = 0 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]

		####     Titanium    #####

		IOF_CO2_t = 0			# Emission factor CO2 [kg/t]
		IOF_hard_coal_t = 0		# Emission factor Hard coal; 26.3 MJ/kg	[kg/t]
		IOF_natural_gas_t = 0	# Emission factor Natural gas; 44.1 MJ/kg [kg/t]
		IOF_brown_coal_t = 0	# Emission factor Brown coal; 11.9 MJ/kg [kg/t]
		IOF_crude_oil_t = 0 	# Emission factor Crude oil; 42.3 MJ/kg [kg/t]
		IOF_SO2_t = 0			# Emission factor SO2	[kg/t]
		IOF_PM10_t = 0			# Emission factor PM10  [kg/t]


		self.xPKM_test[0] += (IOF_CO2_a * aluminum + IOF_CO2_c * Composites + IOF_CO2_s * steel + IOF_CO2_t * Titanium)/ PKMfam * self.palo_PAX * n_airc_test			# CO2 per PKM [g/PKM]
		self.xPKM_test[3] += (IOF_SO2_a * aluminum + IOF_SO2_c * Composites + IOF_SO2_s * steel + IOF_SO2_t * Titanium)/ PKMfam * self.palo_PAX * n_airc_test			# SO2 per PKM [g/PKM]
		self.xPKM_test[8] += (IOF_PM10_a * aluminum + IOF_PM10_c * Composites + IOF_PM10_s * steel + IOF_PM10_t * Titanium)/ PKMfam * self.palo_PAX * n_airc_test			# PM10 per PKM [g/PKM]
		self.xPKM_test[9] += (IOF_natural_gas_a * aluminum + IOF_natural_gas_c * Composites + IOF_natural_gas_s * steel + IOF_natural_gas_t * Titanium)/ PKMfam * self.palo_PAX * n_airc_test			# natural gas per PKM [g/PKM]
		self.xPKM_test[10] += (IOF_crude_oil_a * aluminum + IOF_crude_oil_c * Composites + IOF_crude_oil_s * steel + IOF_crude_oil_t * Titanium)/ PKMfam * self.palo_PAX * n_airc_test	 		# cruide oil per PKM [g/PKM]
		self.xPKM_test[11] += (IOF_hard_coal_a * aluminum + IOF_hard_coal_c * Composites + IOF_hard_coal_s * steel + IOF_hard_coal_t * Titanium)/ PKMfam * self.palo_PAX * n_airc_test			# hard coal per PKM [g/PKM]
		self.xPKM_test[12] += (IOF_brown_coal_a * aluminum + IOF_brown_coal_c * Composites + IOF_brown_coal_s * steel + IOF_brown_coal_t * Titanium)/ PKMfam * self.palo_PAX * n_airc_test			# brown coal per PKM [g/PKM]
		self.xPKM_test[14] += ( IOF_fe_s * steel )/ PKMfam * self.palo_PAX	* n_airc_test		# Fe per PKM [g/PKM]
		self.xPKM_test[15] += ( IOF_mn_s * steel )/ PKMfam * self.palo_PAX	* n_airc_test		# Mn per PKM [g/PKM]

		self.xPKM_test[16] = (0.95 * aluminum )/ PKMfam * self.palo_PAX * n_airc_test	 # multiplied by 1000 to make the kg to g
		self.xPKM_test[17] = (0.9 * Titanium)/ PKMfam * self.palo_PAX * n_airc_test	
		self.xPKM_test[18] = Nickel / PKMfam * self.palo_PAX * n_airc_test	
		self.xPKM_test[19] = 84 * self.Ebat_trip / PKMfam * self.palo_PAX * n_airc_test	

		#### for batteries production

		IOF_hard_coal = 1.681		# Emission factor Hard coal; 26.3 MJ/kg	[kg/kWh]
		IOF_natural_gas = 1.1	# Emission factor Natural gas; 44.1 MJ/kg [kg/kWh]
		IOF_copper_ore = 1.03	# Emission factor Brown coal; 11.9 MJ/kg [kg/kWh]
		IOF_crude_oil = 0.778 	# Emission factor Crude oil; 42.3 MJ/kg [kg/kWh]


		self.xPKM_test[9] = IOF_natural_gas * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKMfam ) * self.palo_PAX	* n_airc_test		# natural gas per PKM [g/PKM]
		self.xPKM_test[10] = IOF_crude_oil * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKMfam ) * self.palo_PAX	* n_airc_test		# cruide oil per PKM [g/PKM]
		self.xPKM_test[11] = IOF_hard_coal * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKMfam ) * self.palo_PAX	* n_airc_test		# hard coal per PKM [g/PKM]
		self.xPKM_test[13] = IOF_copper_ore * 1000 * self.Ebat_trip  / (self.n_cycle_bat *PKMfam ) * self.palo_PAX	* n_airc_test		# copper ore per PKM [g/PKM]






		#######################################################################
		######################       Operation           ######################
		#######################################################################

		
		######################         flight            ######################
		#######################################################################
		######################      Default Values       ######################


		Fuel_approach = self.F_Flow_app * self.t_app
		Fuel_idle = self.F_Flow_idl * self.t_idl
		Fuel_takeoff = self.F_Flow_TO * self.t_TO
		Fuel_climb = self.F_Flow_Climb * self.t_Climb
		Fuel_cruise = self.mass_f_cruise

		if (self.mass_Fuel_trip < (Fuel_approach + Fuel_idle + Fuel_takeoff + Fuel_climb + Fuel_cruise)*0.99) or (self.mass_Fuel_trip > (Fuel_approach + Fuel_idle + Fuel_takeoff + Fuel_climb + Fuel_cruise)*1.01):
			# print("Fuel calculated from fuel flows is different from input")
			raise Exception("Fuel calculated from fuel flows is different from input")


		IOF_CO2 = 3.15			# Emission factor CO2 [kg/kg of fuel]
		IOF_O2 = 3.4		
		IOF_H2O = 1.23	
		IOF_SO2 = 0.00084	

		######################         Cruise            ######################

		IOF_HC_c = 0	
		IOF_CO_c = 0.002808			
		IOF_NOx_c = 0.0159364

		self.xPKM_Cruise = [0]*20
		self.xPKM_Cruise[0] = Fuel_cruise * IOF_CO2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_Cruise[1] = Fuel_cruise * IOF_NOx_c * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Cruise[2] = Fuel_cruise * IOF_CO_c * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Cruise[3] = Fuel_cruise * IOF_SO2 * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Cruise[4] = Fuel_cruise * IOF_O2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_Cruise[5] = Fuel_cruise * IOF_H2O * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Cruise[6] = Fuel_cruise * IOF_HC_c * 1000 / PKM_f * self.palo_PAX			

		######################        Approach           ######################

		IOF_NOx_a = 0.0104
		IOF_HC_a = 0	
		IOF_CO_a = 0.0034		

		self.xPKM_Approach = [0]*20
		self.xPKM_Approach[0] = Fuel_approach * IOF_CO2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_Approach[1] = Fuel_approach * IOF_NOx_a * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Approach[2] = Fuel_approach * IOF_CO_a * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Approach[3] = Fuel_approach * IOF_SO2 * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Approach[4] = Fuel_approach * IOF_O2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_Approach[5] = Fuel_approach * IOF_H2O * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Approach[6] = Fuel_approach * IOF_HC_a * 1000 / PKM_f * self.palo_PAX	

		######################          Idle             ######################

		IOF_NOx_i = 0.00492
		IOF_HC_i = 0.00271	
		IOF_CO_i = 0.01958		

		self.xPKM_Idle =  [0]*20
		self.xPKM_Idle[0] = Fuel_idle * IOF_CO2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_Idle[1] = Fuel_idle * IOF_NOx_i * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Idle[2] = Fuel_idle * IOF_CO_i * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Idle[3] = Fuel_idle * IOF_SO2 * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Idle[4] = Fuel_idle * IOF_O2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_Idle[5] = Fuel_idle * IOF_H2O * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Idle[6] = Fuel_idle * IOF_HC_i * 1000 / PKM_f * self.palo_PAX	

		######################       Take off             ######################

		IOF_NOx_TO = 0.0191
		IOF_HC_TO = 0	
		IOF_CO_TO = 0.002	

		self.xPKM_TO = [0]*20
		self.xPKM_TO[0] = Fuel_takeoff * IOF_CO2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_TO[1] = Fuel_takeoff * IOF_NOx_TO * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_TO[2] = Fuel_takeoff * IOF_CO_TO * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_TO[3] = Fuel_takeoff * IOF_SO2 * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_TO[4] = Fuel_takeoff * IOF_O2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_TO[5] = Fuel_takeoff * IOF_H2O * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_TO[6] = Fuel_takeoff * IOF_HC_TO * 1000 / PKM_f * self.palo_PAX	

		######################       Climb out            ######################

		IOF_NOx_CO = 0.0169
		IOF_HC_CO = 0	
		IOF_CO_CO = 0.0019	

		self.xPKM_Climb = [0]*20
		self.xPKM_Climb[0] = Fuel_climb * IOF_CO2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_Climb[1] = Fuel_climb * IOF_NOx_CO * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Climb[2] = Fuel_climb * IOF_CO_CO * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Climb[3] = Fuel_climb * IOF_SO2 * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Climb[4] = Fuel_climb * IOF_O2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_Climb[5] = Fuel_climb * IOF_H2O * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_Climb[6] = Fuel_climb * IOF_HC_CO * 1000 / PKM_f * self.palo_PAX	

		self.xKPM_flight = [self.xPKM_Climb[i] + self.xPKM_TO[i] + self.xPKM_Approach[i] + self.xPKM_Idle[i] + self.xPKM_Cruise[i]  for i in range(len(self.xPKM_Climb))]
	
		######################    Kerosene production    ######################
		#######################################################################
		######################      Default Values       ######################

		IOF_CO2 = 0.259		
		IOF_hard_coal = 0		
		IOF_natural_gas = 0.0579	
		IOF_brown_coal = 0	
		IOF_crude_oil = 1.11 	# Emission factor Crude oil; 42.3 MJ/kg [kg/kg]
		IOF_SO2 = 0.00158		
		IOF_CH4 = 0.0033			

		######################   inventory calculation   ######################
		### CO2 .. NOX .. CO .. SO2 .. 02 .. H20 .. HC .. CH4 .. PM10 .. Natural_gas .. cruide_oil .. hard_coal .. brown_coal .. copper_ore .. Fe .. Mn
		###  0      1      2     3      4     5     6      7      8           9             10            11            12           13        14     15

		self.xPKM_ker_prod = [0]*20
		self.xPKM_ker_prod[0] = self.mass_Fuel_trip * IOF_CO2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_ker_prod[11] = self.mass_Fuel_trip * IOF_hard_coal * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_ker_prod[9] = self.mass_Fuel_trip * IOF_natural_gas * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_ker_prod[3] = self.mass_Fuel_trip * IOF_SO2 * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_ker_prod[12] = self.mass_Fuel_trip * IOF_brown_coal * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_ker_prod[7] = self.mass_Fuel_trip * IOF_CH4 * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_ker_prod[10] = self.mass_Fuel_trip * IOF_crude_oil * 1000 / PKM_f * self.palo_PAX	




		######################  Electricity production   ######################
		#######################################################################
		######################      Default Values       ######################

		## 1 is for renewables
		if self.Elec_prod_mtd == 1:
				IOF_CO2 = 0.029		
				IOF_hard_coal = 0.00055		
				IOF_natural_gas = 0.0018	
				IOF_brown_coal = 0.00045	
				IOF_crude_oil = 0.0024 	# Emission factor Crude oil; 42.3 MJ/kg [kg/kW]
				IOF_SO2 = 0		
				IOF_CH4 = 0.000048			
		else:
				IOF_CO2 = 0.56		
				IOF_hard_coal = 0.081	
				IOF_natural_gas = 0.041	
				IOF_brown_coal = 0.12	
				IOF_crude_oil = 0.017 	# Emission factor Crude oil; 42.3 MJ/kg [kg/kW]
				IOF_SO2 = 0.0033		
				IOF_CH4 = 0			

		######################   inventory calculation   ######################

		self.xPKM_elec_prod = [0]*20
		self.xPKM_elec_prod [0] = self.Ebat_trip * IOF_CO2 * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_elec_prod [11] = self.Ebat_trip * IOF_hard_coal * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_elec_prod [9] = self.Ebat_trip * IOF_natural_gas * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_elec_prod [3] = self.Ebat_trip * IOF_SO2 * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_elec_prod [12] = self.Ebat_trip * IOF_brown_coal * 1000 / PKM_f * self.palo_PAX			
		self.xPKM_elec_prod [7] = self.Ebat_trip * IOF_CH4 * 1000 / PKM_f * self.palo_PAX		
		self.xPKM_elec_prod [10] = self.Ebat_trip * IOF_crude_oil * 1000 / PKM_f * self.palo_PAX	


		######################     Airports / Ground	 ######################
		#######################################################################
		######################      Default Values       ######################

		IOF_CO2 =  0
		IOF_hard_coal =  0	
		IOF_natural_gas =  0
		IOF_brown_coal =  0
		IOF_crude_oil =  0
		IOF_SO2 =  		0
		IOF_CH4 =  0


		######################   inventory calculation   ######################

		self.xPKM_airports = [0]*20

		########     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!############
		########    !!!!!!!!!!!! this is totally irrelevant of the coniguration  !!!!!############ 




		######################       End of Life         ######################
		#######################################################################
		######################      Default Values       ######################

		##############  there is nothing to do here... ########################## 


		#######################################################################
		######################     Overall Inventory     ######################
		#######################################################################

		self.xPKM_overall = [self.xPKM_test[i] + self.xPKM_airports[i] + self.xPKM_elec_prod [i] + self.xPKM_ker_prod[i] + self.xKPM_flight[i] + self.xPKM_battery_prod[i]  +\
						self.xPKM_materials[i]  + self.xPKM_Prod_fac[i]  + self.xPKM_windT[i]  + self.xPKM_computers[i]  for i in range(len(self.xPKM_Climb))]
		#print("CO2 .. NOX .. CO .. SO2 .. 02 .. H20 .. HC .. CH4 .. PM10 .. Natural_gas .. cruide_oil .. hard_coal .. brown_coal .. copper_ore .. Fe .. Mn")
		#print(xPKM_overall)




		
		self.xPKM_overall_dic = { 'CO2' :self.xPKM_overall[0], 'NOx' :self.xPKM_overall[1], 'CO' :self.xPKM_overall[2], 'SO2' :self.xPKM_overall[3], 'O2' :self.xPKM_overall[4], \
			'H2O' :self.xPKM_overall[5],'HC' :self.xPKM_overall[6], 'CH4' :self.xPKM_overall[7], 'PM10' :self.xPKM_overall[8], 'NG' :self.xPKM_overall[9], 'OIL' :self.xPKM_overall[10], \
			'HARDC' :self.xPKM_overall[11], 'BROWNC' :self.xPKM_overall[12], 'CU' :self.xPKM_overall[13], 'FE' :self.xPKM_overall[14],'MN' :self.xPKM_overall[15], 'AL' :self.xPKM_overall[16], \
			'TI' :self.xPKM_overall[17], 'NI' :self.xPKM_overall[18], 'LI' :self.xPKM_overall[19]}
		
		return -1
	#######################################################################
	###################### input general parameters  ######################




##############################################################################################################################################
###############							  Impact Assessment							##########################################################
##############################################################################################################################################
##############################################################################################################################################


######################       Climate change      ######################
#######################################################################

def Climate_Change(xKPM_input, Altitude, Analysis, weight_h, weight_eco, xKPM_alt = [0] * 16):

	CFmidpoint_CO2 = 1

	if (Analysis == 1):
			CFmidpoint_CH4 = 84 
	elif (Analysis == 2):
			CFmidpoint_CH4 = 34
	else:
			CFmidpoint_CH4 = 4.8

	SGTP_CO2 = 3.58E-14
	SGTP_Short_O3 = 7.97E-12
	SGTP_CH4 = -3.90E-12
	SGTP_Long_O3 = -9.14E-13
	SGTP_Contrails =	2.36E-14
	SGTP_Cirrus =	7.08E-14


	if Altitude < 175:
			FLA=170
	else:
			FLA=Altitude

	S_NOx_short_O3 = (-1.6020E-6*FLA**4+0.0019067835*FLA**3-0.8084002049*FLA**2+149.1083630061*FLA-9631.4372826996)/1000
	S_NOx_long_O3_CH4 = (-2.2474E-6*FLA**4+0.0026709259*FLA**3-1.1509768569*FLA**2+213.6058584148*FLA-13567.8236978691)/1000
	S_NOx_CC = (4.6798E-10*FLA**6 - 7.39418E-7*FLA**5 + 0.0004719849*FLA**4 - 0.1561903336*FLA**3 + 28.4129780160*FLA**2 - 2708.5864628755*FLA + 106205.768586244)/1000


	CFmidpoint_CC = SGTP_Contrails * S_NOx_CC / SGTP_CO2 +  SGTP_Cirrus * S_NOx_CC / SGTP_CO2
	CFmidpoint_NOx = SGTP_Short_O3 * S_NOx_short_O3 / SGTP_CO2 + SGTP_Long_O3 * S_NOx_long_O3_CH4 / SGTP_CO2 + SGTP_CH4 * S_NOx_long_O3_CH4 / SGTP_CO2

	
######################        Human health       #####################

	if (Analysis == 1):
			#Norm_mid_h = 1.075706E+04		 # Global Warming - Human health - midpoint
			Human_h = 8.12E-08			     # Midpoint to endpoint conversion factor
			Norm_end_h = 8.73473E-04		 # Global Warming - Human health - endpoint
	elif (Analysis == 2):
			#Norm_mid_h = 7.99041E+03	     # Global Warming - Human health - midpoint
			Human_h = 9.28E-07				 # Midpoint to endpoint conversion factor
			Norm_end_h = 7.41510E-03		 # Global Warming - Human health - endpoint
	else:
			#Norm_mid_h =5.79760E+03			 # Global Warming - Human health - midpoint
			Human_h = 1.25E-05				 # Midpoint to endpoint conversion factor
			Norm_end_h = 7.24701E-02		 # Global Warming - Human health - endpoint


	#### Note that for climate change, contrails and NOx, only cruise flight is taken into account since the emission must be made in high altitude

	Midpoint_Climate = CFmidpoint_CO2 * xKPM_input[0] + CFmidpoint_CH4 * xKPM_input[7] + CFmidpoint_NOx * xKPM_alt[1] + CFmidpoint_CC * xKPM_alt[5] 

	Endpoint_Climate_h = Midpoint_Climate * Human_h / Norm_end_h * weight_h / 1000   # it is / 1000 to make the g into kg.


	######################    Ecosystem diversity    #####################

	if (Analysis == 1):
			Eco_s = 5.32E-10			     # Midpoint to endpoint conversion factor
			Norm_end_eco = 5.72276E-06		 # Global Warming - ecosystem - endpoint
	elif (Analysis == 2):
			Eco_s = 2.80E-09				 # Midpoint to endpoint conversion factor
			Norm_end_eco =	2.23731E-05		 # Global Warming - ecosystem - endpoint
	else:
			Eco_s = 2.50E-08				 # Midpoint to endpoint conversion factor
			Norm_end_eco = 1.44940E-04		 # Global Warming - ecosystem - endpoint

	Endpoint_Climate_eco = Midpoint_Climate * Eco_s / Norm_end_eco * weight_eco / 1000

	Endpoint_Climate_res = 0
	######################    Climate change total    #####################

	Endpoint_Climate_tot = Endpoint_Climate_h + Endpoint_Climate_eco

	#print("Climate Change = ",Midpoint_Climate ,Endpoint_Climate_h, Endpoint_Climate_eco, Endpoint_Climate_res, Endpoint_Climate_tot)
	
	return [Endpoint_Climate_h, Endpoint_Climate_eco, Endpoint_Climate_res, Endpoint_Climate_tot,  Midpoint_Climate]

#################### Stratospheric Ozone depletion ####################
#######################################################################
## There are no calculated emissions that can be used for this midpoint category for our analysis

def Ozone_depletion(xKPM_input = [0]*16, Analysis = 0):
	Midpoint_ozone_depl = 0
	Endpoint_ozone_depl_h = 0 / 1000
	Endpoint_ozone_depl_eco = 0
	Endpoint_ozone_depl_res = 0
	Endpoint_ozone_depl_tot = Endpoint_ozone_depl_h + Endpoint_ozone_depl_eco + Endpoint_ozone_depl_res

	#print("Ozone Depletion is not calculated for the moment ",Midpoint_ozone_depl ,Endpoint_ozone_depl_h, Endpoint_ozone_depl_eco, Endpoint_ozone_depl_res, Endpoint_ozone_depl_tot)

	return [Endpoint_ozone_depl_h, Endpoint_ozone_depl_eco, Endpoint_ozone_depl_res, Endpoint_ozone_depl_tot]

###################### Terrestrial acidification ######################
#######################################################################

def Terrestrial_Acidification(xKPM_input, weight_eco, Analysis = 0):

	CFmidpoint_NOx = 3.60E-01	
	CFmidpoint_SO2 = 1.00E+00	

	acid_eco = 2.12E-07			     # Midpoint to endpoint conversion factor
	norm_end_acid =	8.419892E-06	 # Acidification - Ecosystem - endpoint

	Midpoint_Acidification = CFmidpoint_NOx * xKPM_input[1] + CFmidpoint_SO2 * xKPM_input[3]
	
	Endpoint_Acidification_h = 0
	Endpoint_Acidification_eco = Midpoint_Acidification * acid_eco / norm_end_acid * weight_eco / 1000
	Endpoint_Acidification_res = 0
	Endpoint_Acidification_tot = Endpoint_Acidification_h + Endpoint_Acidification_eco + Endpoint_Acidification_res
	
	#print("Acidification = ",Midpoint_Acidification,Endpoint_Acidification_h, Endpoint_Acidification_eco, Endpoint_Acidification_res, Endpoint_Acidification_tot)

	return [Endpoint_Acidification_h, Endpoint_Acidification_eco, Endpoint_Acidification_res, Endpoint_Acidification_tot]

###################### Freshwater eutrophication ######################
#######################################################################

## There are no calculated emissions that can be used for this midpoint category for our analysis

def Water_eutrophication(xKPM_input = [0]*16, Analysis = 0):
	Midpoint_Water_eutrop = 0
	Endpoint_Water_eutrop_h = 0 / 1000
	Endpoint_Water_eutrop_eco = 0
	Endpoint_Water_eutrop_res = 0
	Endpoint_Water_eutrop_tot = Endpoint_Water_eutrop_h + Endpoint_Water_eutrop_eco + Endpoint_Water_eutrop_res

	#print("Water eutrophication is not calculated for the moment ",Midpoint_Water_eutrop ,Endpoint_Water_eutrop_h, Endpoint_Water_eutrop_eco, Endpoint_Water_eutrop_res, Endpoint_Water_eutrop_tot)

	return [Endpoint_Water_eutrop_h, Endpoint_Water_eutrop_eco, Endpoint_Water_eutrop_res, Endpoint_Water_eutrop_tot]

######################   Marine eutrophication   ######################
#######################################################################
## There are no calculated emissions that can be used for this midpoint category for our analysis

def Marine_eutrophication(xKPM_input = [0]*16, Analysis = 0):
	Midpoint_Marine_eutrop = 0
	Endpoint_Marine_eutrop_h = 0 / 1000
	Endpoint_Marine_eutrop_eco = 0
	Endpoint_Marine_eutrop_res = 0
	Endpoint_Marine_eutrop_tot = Endpoint_Marine_eutrop_h + Endpoint_Marine_eutrop_eco + Endpoint_Marine_eutrop_res

	#print("Marine eutrophication is not calculated for the moment ",Midpoint_Marine_eutrop ,Endpoint_Marine_eutrop_h, Endpoint_Marine_eutrop_eco, Endpoint_Marine_eutrop_res, Endpoint_Marine_eutrop_tot)

	return [Endpoint_Marine_eutrop_h, Endpoint_Marine_eutrop_eco, Endpoint_Marine_eutrop_res, Endpoint_Marine_eutrop_tot]

######################         Toxicity          ######################
#######################################################################

def Toxicity(xKPM_input, weight_h, weight_eco, Analysis = 0):

	CFmidpoint_Human_HC = 1.8574E-01
	CFmidpoint_Terrestrial_HC = 5.75064E-01
	CFmidpoint_FreshWater_HC = 6.16E-04
	CFmidpoint_Marine_HC = 2.455E-04


	Toxic_h = 2.280E-07		     # Midpoint to endpoint conversion factor
	Toxic_t = 1.14E-11			 # Midpoint to endpoint conversion factor
	Toxic_fw = 6.95E-10			 # Midpoint to endpoint conversion factor
	Toxic_m =1.05E-10			 # Midpoint to endpoint conversion factor


	if (Analysis == 1):
			Norm_end_h = 3.3882E-07			 # Human health - endpoint
			Norm_end_eco = 3.6242E-04		 # ecosystem - endpoint
			Norm_end_fw = 8.74E-09			 # fresh water - endpoint
			Norm_end_m = 9.24E-10			 # marine - endpoint
	elif (Analysis == 2):
			Norm_end_h = 2.078248E-04		 # Human health - endpoint
			Norm_end_eco =	8.1881E-04		 # ecosystem - endpoint
			Norm_end_fw = 1.75E-08			 # fresh water - endpoint
			Norm_end_m = 4.5615E-09			 # marine - endpoint
	else:
			Norm_end_h = 1.4791922E-02		 # Human health - endpoint
			Norm_end_eco = 8.8150E-04		 # ecosystem - endpoint
			Norm_end_fw = 2.02E-07			 # fresh water - endpoint
			Norm_end_m = 2.58626E-04		 # marine - endpoint
		

	Midpoint_Human = CFmidpoint_Human_HC * xKPM_input[6] 
	Midpoint_Terrestrial = CFmidpoint_Terrestrial_HC * xKPM_input[6] 
	Midpoint_FreshWater = CFmidpoint_FreshWater_HC * xKPM_input[6] 
	Midpoint_Marine = CFmidpoint_Marine_HC * xKPM_input[6] 

	Endpoint_Toxicity_h = Midpoint_Human * Toxic_h / Norm_end_h * weight_eco / 1000
	Endpoint_Toxicity_eco = Midpoint_Terrestrial * Toxic_t / Norm_end_eco * weight_h / 1000
	Endpoint_Toxicity_fw = Midpoint_Human * Toxic_fw / Norm_end_fw * weight_eco / 1000
	Endpoint_Toxicity_m = Midpoint_Terrestrial * Toxic_m / Norm_end_m * weight_eco / 1000
	Endpoint_Toxicity_res = 0

	######################       Tocixity total       #####################

	Endpoint_Toxicity_tot = Endpoint_Toxicity_h + Endpoint_Toxicity_eco + Endpoint_Toxicity_fw + Endpoint_Toxicity_m + Endpoint_Toxicity_res

	#print("Toxicity =  ","four mids ",Endpoint_Toxicity_h, Endpoint_Toxicity_eco + Endpoint_Toxicity_fw + Endpoint_Toxicity_m , Endpoint_Toxicity_res, Endpoint_Toxicity_tot)

	return [Endpoint_Toxicity_h, Endpoint_Toxicity_eco + Endpoint_Toxicity_fw + Endpoint_Toxicity_m , Endpoint_Toxicity_res, Endpoint_Toxicity_tot]

#################### Photochemical oxidant formation ##################
#######################################################################
### this comes from mix from old files and new files

def Photochemical(xKPM_input, weight_h, weight_eco, Analysis = 0):

	CFmidpoint_NOx = 1
	CFmidpoint_HC = 0.10
	CFmidpoint_SO2 = 0 #0.081
	CFmidpoint_CO = 0#0.046
	CFmidpoint_CH4 = 0.0101

	Photoch_h = 9.10E-07
	Photoch_eco = 1.29E-07

	Norm_end_h= 1.802273E-05
	Norm_end_eco = 2.238762E-06


	Midpoint_Photoch = CFmidpoint_NOx * xKPM_input[1] + CFmidpoint_HC * xKPM_input[6] + CFmidpoint_SO2 * xKPM_input[3] + CFmidpoint_CO * xKPM_input[2] + CFmidpoint_CH4 * xKPM_input[7] 

	Endpoint_Photoch_h = Midpoint_Photoch * Photoch_h / Norm_end_h * weight_h / 1000
	# we use 1.2 since the actual effecto is more important than for humans, but i was not able to find values for CF
	Endpoint_Photoch_eco = Midpoint_Photoch * Photoch_eco / Norm_end_eco * weight_eco / 1000  
	Endpoint_Photoch_res = 0  

	######################     Photochemical total     #####################

	Endpoint_Photoch_tot = Endpoint_Photoch_h + Endpoint_Photoch_eco + Endpoint_Photoch_res
	#Endpoint_Photoch_tot = 0
	#print("Photochemical =  ",Midpoint_Photoch, Endpoint_Photoch_h, Endpoint_Photoch_eco, Endpoint_Photoch_res, Endpoint_Photoch_tot)

	return [Endpoint_Photoch_h, Endpoint_Photoch_eco, Endpoint_Photoch_res, Endpoint_Photoch_tot]

####################  Particulate matter formation   ##################
#######################################################################

def Particulate_matter(xKPM_input, weight_h, Analysis = 0):
	Particulate_h = 6.2900E-04

	if (Analysis == 1):
			CFmidpoint_NOx = 0
			CFmidpoint_PM10 = 1
			CFmidpoint_SO2 = 0
			Norm_end_h= 1.00092E-02
	else:
			CFmidpoint_NOx = 0.11
			CFmidpoint_PM10 = 1
			CFmidpoint_SO2 = 0.29
			Norm_end_h= 1.60948E-02


	Midpoint_Particulate  = CFmidpoint_NOx * xKPM_input[1] + CFmidpoint_PM10 * xKPM_input[8] + CFmidpoint_SO2 * xKPM_input[3]  

	Endpoint_Particulate_h = Midpoint_Particulate * Particulate_h / Norm_end_h * weight_h / 1000
	Endpoint_Particulate_eco = 0
	Endpoint_Particulate_res = 0

	Endpoint_Particulate_tot = Endpoint_Particulate_h + Endpoint_Particulate_eco + Endpoint_Particulate_res
	#print("Particulate matter =  ",Midpoint_Particulate, Endpoint_Particulate_h, Endpoint_Particulate_eco, Endpoint_Particulate_res, Endpoint_Particulate_tot)

	return [Endpoint_Particulate_h, Endpoint_Particulate_eco, Endpoint_Particulate_res, Endpoint_Particulate_tot]

####################        Ionising radiation       ##################
#######################################################################

## There are no calculated emissions that can be used for this midpoint category for our analysis

def Ionasing(xKPM_input = [0]*15, Analysis = 0):
	Midpoint_Ionasing = 0
	Endpoint_Ionasing_h = 0 / 1000
	Endpoint_Ionasing_eco = 0
	Endpoint_Ionasing_res = 0
	Endpoint_Ionasing_tot = Endpoint_Ionasing_h + Endpoint_Ionasing_eco + Endpoint_Ionasing_res

	#print("Marine eutrophication is not calculated for the moment ",Midpoint_Ionasing ,Endpoint_Ionasing_h, Endpoint_Ionasing_eco, Endpoint_Ionasing_res, Endpoint_Ionasing_tot)

	return [Endpoint_Ionasing_h, Endpoint_Ionasing_eco, Endpoint_Ionasing_res, Endpoint_Ionasing_tot]

#################### Land occupation/transformation  ##################
#######################################################################

## There are no calculated emissions that can be used for this midpoint category for our analysis
def Land(xKPM_input = [0]*15, Analysis = 0):
	Midpoint_Land = 0
	Endpoint_Land_h = 0 / 1000
	Endpoint_Land_eco = 0
	Endpoint_Land_res = 0
	Endpoint_Land_tot = Endpoint_Land_h + Endpoint_Land_eco + Endpoint_Land_res

	#print("Land is not calculated for the moment ",Midpoint_Land ,Endpoint_Land_h, Endpoint_Land_eco, Endpoint_Land_res, Endpoint_Land_tot)

	return [Endpoint_Land_h, Endpoint_Land_eco, Endpoint_Land_res, Endpoint_Land_tot]

####################        Water consumption        ##################
#######################################################################

## There are no calculated emissions that can be used for this midpoint category for our analysis

def Water(xKPM_input = [0]*15, Analysis = 0):
	Midpoint_Water = 0
	Endpoint_Water_h = 0 / 1000
	Endpoint_Water_eco = 0
	Endpoint_Water_res = 0
	Endpoint_Water_tot = Endpoint_Water_h + Endpoint_Water_eco + Endpoint_Water_res

	#print("Water is not calculated for the moment ",Midpoint_Water ,Endpoint_Water_h, Endpoint_Water_eco, Endpoint_Water_res, Endpoint_Water_tot)

	return [Endpoint_Water_h, Endpoint_Water_eco, Endpoint_Water_res, Endpoint_Water_tot]

####################          Mineral usage          ##################
#######################################################################
##we could calculate also aluminum and titanium by assuming the purity of them. 95% for aluminum and 90% for titanium, nickel is pure

def Mineral_extr(xKPM_input, weight_r, Analysis = 0):

	if (Analysis == 1):
			CFmidpoint_Cu = 1
			CFmidpoint_Ti = 6.88651E-01
			CFmidpoint_Al = 1.00740E-01
			CFmidpoint_Fe = 3.81732E-02
			CFmidpoint_Mn = 3.76250E-02
			CFmidpoint_Ni = 1.85086E+00
			CFmidpoint_Li = 2.41821E+00
			mineral_end = 1.594383E-01
			norm_end = 3.079937E+04
	else:
			CFmidpoint_Cu = 1
			CFmidpoint_Ti = 8.78770E-01
			CFmidpoint_Al = 1.69339E-01
			CFmidpoint_Fe = 6.19366E-02
			CFmidpoint_Mn = 8.22722E-02
			CFmidpoint_Ni = 2.89235E+00
			CFmidpoint_Li = 4.85921E+00
			mineral_end = 2.310844E-01
			norm_end = 2.774196E+04



	Midpoint_Mineral = CFmidpoint_Cu * xKPM_input[13] + CFmidpoint_Fe * xKPM_input[14] + CFmidpoint_Mn * xKPM_input[15] + \
				CFmidpoint_Ti *  xKPM_input[17] + CFmidpoint_Al *  xKPM_input[16] + CFmidpoint_Ni *  xKPM_input[18] + CFmidpoint_Li *  xKPM_input[19]

	Endpoint_Mineral_res = Midpoint_Mineral * mineral_end / norm_end * weight_r / 1000

	Endpoint_Mineral_h = 0
	Endpoint_Mineral_eco = 0
	Endpoint_Mineral_tot = Endpoint_Mineral_h + Endpoint_Mineral_eco + Endpoint_Mineral_res

	#print("Mineral matter =  ",Midpoint_Mineral, Endpoint_Mineral_h, Endpoint_Mineral_eco, Endpoint_Mineral_res, Endpoint_Mineral_tot)

	return [Endpoint_Mineral_h, Endpoint_Mineral_eco, Endpoint_Mineral_res, Endpoint_Mineral_tot]

####################          Fossils usage          ##################
#######################################################################

def Fossils_extr(xKPM_input, Analysis = 0):

	CFmidpoint_Crude_oil = 1.0
	CFmidpoint_Natural_gas = 8.40E-01
	CFmidpoint_Hard_coal = 4.20E-01
	CFmidpoint_Brown_coal = 2.20E-01

	Crude_oil_end = 0.46
	Hard_coal_end = 0.03
	Natural_gas_end = 0.30
	Brown_coal_end = 0.03

	norm_end = 2.91352139678E+02

	Midpoint_fossils = (CFmidpoint_Crude_oil * xKPM_input[10] + CFmidpoint_Natural_gas * xKPM_input[9] + CFmidpoint_Hard_coal * xKPM_input[11] + CFmidpoint_Brown_coal * xKPM_input[12] )

	Endpoint_fossils_res = (CFmidpoint_Crude_oil * xKPM_input[10] * Crude_oil_end + CFmidpoint_Natural_gas * xKPM_input[9] * Natural_gas_end +\
						CFmidpoint_Hard_coal * xKPM_input[11] * Hard_coal_end + CFmidpoint_Brown_coal * xKPM_input[12] * Brown_coal_end) / 1000 / norm_end

	
	Endpoint_fossils_h = 0
	Endpoint_fossils_eco = 0
	Endpoint_fossils_tot = Endpoint_fossils_h + Endpoint_fossils_eco + Endpoint_fossils_res

	
	#print("fossils matter =  ",Midpoint_fossils, Endpoint_fossils_h, Endpoint_fossils_eco, Endpoint_fossils_res, Endpoint_fossils_tot)

	return [Endpoint_fossils_h, Endpoint_fossils_eco, Endpoint_fossils_res, Endpoint_fossils_tot]


###########################################################################
###########################################################################
###########################################################################
###########################################################################

def Single_score_source (xKPM_in, Analysis, weight_h, weight_eco, weight_r, Altitude = 175,X_alt = [0]*16):
	Climate = Climate_Change(xKPM_in, Altitude, Analysis, weight_h, weight_eco, X_alt)
	Water_eutrop = Water_eutrophication()
	Marine_eutrop = Marine_eutrophication()
	Acidification = Terrestrial_Acidification(xKPM_in, weight_eco)
	Ozone_Depl = Ozone_depletion()
	Toxic = Toxicity(xKPM_in, weight_h, weight_eco, Analysis)
	Photoch = Photochemical(xKPM_in, weight_h, weight_eco, Analysis)
	Particulate = Particulate_matter(xKPM_in, weight_h, Analysis)
	Ionas = Ionasing()
	land = Land()
	water = Water()
	Mineral = Mineral_extr(xKPM_in, weight_r, Analysis)
	Fossils = Fossils_extr(xKPM_in, Analysis)

	Single_Score = Climate[3] + Ozone_Depl[3] + Acidification[3] + Water_eutrop[3] + Marine_eutrop[3] + Toxic[3] + Photoch[3] + Particulate[3] + Ionas[3] + land[3] + water[3] + Mineral[3] + Fossils[3]

	return Single_Score

def Single_score_emission (xKPM_in, Analysis, emission, weight_h, weight_eco, weight_r, Alt = 175,X_alt = [0]*20):
	xKPM = [0]*20
	X_add = [0] *20

	i=0
	for key in xKPM_in.copy():
		if key != emission:
			xKPM[i] = 0
		else:
			xKPM[i] = xKPM_in[key]
		i+=1
	if (emission == 'NOx'): 
			X_add[1] = X_alt[1]
	elif (emission == 'H2O'):
			X_add[5] = X_alt[5]

	return Single_score_source(xKPM, Analysis, weight_h, weight_eco, weight_r, Alt, X_add)

def make_radar_plot(ax, lbls, vals, case_names, colors, title):

	for i, lbl in enumerate(lbls):
		lb = np.linspace(start = 0, stop = 2*np.pi, num = len([*lbl, lbl[0]]))
		plt.plot(lb, [*vals[i], vals[i][0]], label = case_names[i], color = colors[i])
		plt.fill(lb, [*vals[i], vals[i][0]], colors[i], alpha = .1)
    
	plt.title(title)
	lines, labels = plt.thetagrids(np.degrees(lb), labels = [*lbl, lbl[0]])
	plt.legend(bbox_to_anchor = (1.2, 0.9))
	for label, ang in zip(ax.get_xticklabels(), lb):
		if ang == np.pi*2 or ang == 0:
			label.set_horizontalalignment('left')
		elif ang == np.pi/2 or ang == np.pi/2*3:
			label.set_horizontalalignment('center')
		elif ang == -np.pi:
			label.set_horizontalalignment('right')
		elif ang > 3*np.pi/2 or ang < np.pi/2:
			label.set_horizontalalignment('left')
		else:
			label.set_horizontalalignment('right')

	plt.tight_layout()
	plt.savefig(title+'_'+case_names[0]+'.png', dpi = 300)
	plt.close()
 	



def make_pie_plot(input, case_name, title):
	
	plt.figure(figsize = (8,8))

	explodes = [0.025]*len(input.values())  # only "explode" the 1st slice (i.e. 'Apple')
	plt.style.use('ggplot')
	plt.title(title)
	plt.pie(x=input.values(), autopct='%.2f%%', startangle=90, explode = explodes)
	plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	plt.legend(input.keys(), bbox_to_anchor=(1,0.5) , loc='center left')

	# donut
	circle = plt.Circle(xy=(0,0), radius=.8, facecolor='white')
	plt.gca().add_artist(circle)
	plt.tight_layout()
	plt.savefig('./images/' + title + '.png', dpi = 600)
	plt.close()




#### Share of Midpoint categories  ####
def Share_Midpoints(xKPM_in, Analysis, Altitude, weight_h, weight_eco, weight_r, X_alt = [0]*16 ):

	Climate = Climate_Change(xKPM_in, Altitude, Analysis, weight_h, weight_eco, X_alt)
	Water_eutrop = Water_eutrophication()
	Marine_eutrop = Marine_eutrophication()
	Acidification = Terrestrial_Acidification(xKPM_in, weight_eco)
	Ozone_Depl = Ozone_depletion()
	Toxic = Toxicity(xKPM_in, weight_h, weight_eco, Analysis)
	Photoch = Photochemical(xKPM_in, weight_h, weight_eco, Analysis)
	Particulate = Particulate_matter(xKPM_in, weight_h, Analysis)
	Ionas = Ionasing()
	land = Land()
	water = Water()
	Mineral = Mineral_extr(xKPM_in, weight_r, Analysis)
	Fossils = Fossils_extr(xKPM_in, Analysis)
	
	labels = ['Share of Climate change', 'Share of Toxicity', 'Share of Acidification', 'Share of Photochemical oxidant formation', \
		'Remaining share']
	shares = [Climate [3], Toxic[3], Acidification[3],  Photoch[3], Particulate[3] + Mineral[3] + Fossils[3] + Water_eutrop[3] + Marine_eutrop[3] + Ionas[3] + land[3] + water[3] + Ozone_Depl[3]] # sales in million units
	Results =  dict(zip(labels, shares))

	return Results

### Share of Endpoint categories  ####
def Share_Endpoints(xKPM_in, Analysis, Altitude, weight_h, weight_eco, weight_r, X_alt = [0]*16 ):
	
	Climate = Climate_Change(xKPM_in, Altitude, Analysis, weight_h, weight_eco, X_alt)
	Water_eutrop = Water_eutrophication()
	Marine_eutrop = Marine_eutrophication()
	Acidification = Terrestrial_Acidification(xKPM_in, weight_eco)
	Ozone_Depl = Ozone_depletion()
	Toxic = Toxicity(xKPM_in, weight_h, weight_eco, Analysis)
	Photoch = Photochemical(xKPM_in, weight_h, weight_eco, Analysis)
	Particulate = Particulate_matter(xKPM_in, weight_h, Analysis)
	Ionas = Ionasing()
	land = Land()
	water = Water()
	Mineral = Mineral_extr(xKPM_in, weight_r, Analysis)
	Fossils = Fossils_extr(xKPM_in, Analysis)
	
	Human_Health = Climate[0] + Ozone_Depl[0] + Acidification[0] + Water_eutrop[0] + Marine_eutrop[0] + Toxic[0] + Photoch[0] + Particulate[0] + Ionas[0] + land[0] + water[0] + Mineral[0] + Fossils[0]
	Ecosystem = Climate[1] + Ozone_Depl[1] + Acidification[1] + Water_eutrop[1] + Marine_eutrop[1] + Toxic[1] + Photoch[1] + Particulate[1] + Ionas[1] + land[1] + water[1] + Mineral[1] + Fossils[1]

	Resources = Climate[2] + Ozone_Depl[2] + Acidification[2] + Water_eutrop[2] + Marine_eutrop[2] + Toxic[2] + Photoch[2] + Particulate[2] + Ionas[2] + land[2] + water[2] + Mineral[2] + Fossils[2]

	labels = ['Share of Human Health', 'Share of Ecosystem', 'Share of Resources']
	shares = [Human_Health, Ecosystem, Resources] # sales in million units
	Results =  dict(zip(labels, shares))

	return Results

def Share_sources(object):
	SS_Cruise = Single_score_source (object.xPKM_Cruise, object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r, object.FL, object.xPKM_Cruise)
	SS_LTO = Single_score_source ([object.xPKM_Climb[i] + object.xPKM_TO[i] + object.xPKM_Approach[i] + object.xPKM_Idle[i]   for i in range(len(object.xPKM_Climb))], object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)
	SS_Test = Single_score_source (object.xPKM_test, object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)
	SS_Prod_fac = Single_score_source (object.xPKM_Prod_fac, object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)
	SS_Materials = Single_score_source (object.xPKM_materials, object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)
	SS_WindT = Single_score_source (object.xPKM_windT, object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)
	SS_Keros = Single_score_source (object.xPKM_ker_prod, object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)
	SS_Elect = Single_score_source (object.xPKM_elec_prod , object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)
	SS_Comput = Single_score_source (object.xPKM_computers, object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)
	SS_Betteries = Single_score_source (object.xPKM_battery_prod, object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)
	SS_Airports = Single_score_source (object.xPKM_airports, object.type_of_analys, object.weight_h, object.weight_eco, object.weight_r)


	labels = ['Share of LTO', 'Share of Aircraft production', 'Share of Kerosene production', 'Share of Cruise',   'Share of Electricity production']
	shares = [SS_LTO, SS_Keros, SS_Betteries + SS_Prod_fac + SS_Materials + SS_Comput + SS_WindT + SS_Test, SS_Cruise,   SS_Elect] # sales in million units

	Results =  dict(zip(labels, shares))

	return Results

def Share_emission(object):
	CO2 = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'CO2', object.weight_h, object.weight_eco, object.weight_r, object.FL, object.xPKM_Cruise)
	NOx = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'NOx', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	CO = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'CO', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	SO2 = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'SO2', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	O2 = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'O2', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	H20 = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'H2O', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	HC = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'HC', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	CH4 = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'CH4', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	PM10 = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'PM10', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	NG = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'NG', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	OIL = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'OIL', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	HARDC = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'HARDC', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	BROWNC = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'BROWNC', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	CU = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'CU', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	FE = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'FE', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	MN = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'MN', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	AL = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'AL', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	TI = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'TI', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	NI = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'NI', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)
	LI = Single_score_emission(object.xPKM_overall_dic, object.type_of_analys, 'LI', object.weight_h, object.weight_eco, object.weight_r, object.FL,object.xPKM_Cruise)


	labels = ['Share of CO2',  'Share of Other emissions', 'Share of SO2', 'Share of HC and CH4','Share of NOx', 'Share of Fossils and Minerals']
	shares = [CO2, O2 + PM10 + CO + H20, SO2,  HC + CH4, NOx, NG + OIL + HARDC + BROWNC + CU + FE + MN + AL + TI + NI + LI] 
	

	Results =  dict(zip(labels, shares))

	return Results

def run_config(configuration, elec_prod_mtd = 0):
	Config = Case(configuration)
	Config.Write_config_file(elec_prod_mtd)
	Config.Read_config_file()
	Config.Execution()
	global weight_eco 
	global weight_h 
	global weight_r
	if (Config.type_of_weight == 0):
			weight_eco = 250
			weight_h = 550
			weight_r = 200
	elif (Config.type_of_weight == 1):
			weight_eco = 400
			weight_h = 300
			weight_r = 300
	else:
			weight_eco = 500
			weight_h = 300
			weight_r = 200
	return Config


def plot_bar_chart(list_of_configurations):

	results = [0]*len(list_of_configurations)
	for i, config in enumerate(list_of_configurations):
			Configuration = run_config(config+'.csv')
			results[i] = Single_score_source(Configuration.xPKM_overall, Configuration.type_of_analys, Configuration.weight_h, Configuration.weight_eco, Configuration.weight_r, Configuration.FL, Configuration.xPKM_Cruise)
		
	fig, ax = plt.subplots(figsize =(16, 9))
	bars = ax.barh(list_of_configurations, results)

	for s in ['top', 'bottom', 'left', 'right']:
		ax.spines[s].set_visible(False)
	ax.xaxis.set_ticks_position('none')
	ax.yaxis.set_ticks_position('none')
	ax.xaxis.set_tick_params(pad = 5)
	ax.yaxis.set_tick_params(pad = 10)
	ax.grid(b = True, color ='grey', linestyle ='-.', linewidth = 0.5, alpha = 0.2)
	ax.invert_yaxis()

	ax.bar_label(bars,fmt='%1.3f', padding = 3.5, fontsize = 10)
	#for i in ax.patches:
	#	plt.text(i.get_width()+0.2, i.get_y()+0.5, str(round((i.get_width()), 2)), fontsize = 10, fontweight ='bold', color ='grey')
	
	ax.set_title('Configuration Life Cycle Impact',	 loc ='left',fontsize = 16 )
	plt.tight_layout()
	plt.savefig('./images/bar_chart.png', dpi = 600)
	plt.close()


def write_to_excel(dict, name, write_type = "a", elec_prod_mtd = 0, weight_type = 0.):
    
	if elec_prod_mtd == 0:
		el_type = "EUmix"
	else:
		el_type = "renewables"

	if weight_type == 0:
		wt = "individualist"
	elif weight_type == 1:
		wt = "hierarchist"
	else:
		wt = "egalitarian"

	with open(name + '_output_{0}_{1}.csv'.format(el_type, wt), write_type) as f:
		for key in dict.keys():
			f.write("%s,%s\n"%(key,dict[key]))
		f.write('\n')

	return -1

def plot_pie_chart(list_of_configurations, elec_prod_mtd = 0):
	abs_value=0
	results = [0]*len(list_of_configurations)
	for j, config in enumerate(list_of_configurations):

			exctract_path = config.strip("\n").split("/")

			cwd = os.getcwd()

			os.chdir(os.path.join(exctract_path[0], exctract_path[1], exctract_path[2]))
			
			write_to_excel({},exctract_path[3], write_type = "w", elec_prod_mtd = elec_prod_mtd)

			Configuration = run_config(exctract_path[3]+'.csv', elec_prod_mtd = elec_prod_mtd)

			os.chdir(cwd)

			#if config == 'Conventional2014':
			result = Share_emission(Configuration)
			write_to_excel(result,config, elec_prod_mtd = elec_prod_mtd)
			#make_pie_plot(result,config, config+'Share_emission')
			result = Share_sources(Configuration)
			write_to_excel(result,config, elec_prod_mtd = elec_prod_mtd)
			#make_pie_plot(result,config, config+'Share_sources')
			result = Share_Endpoints(Configuration.xPKM_overall, Configuration.type_of_analys,
			    Configuration.FL, Configuration.weight_h, Configuration.weight_eco,
				Configuration.weight_r, Configuration.xPKM_Cruise)
			write_to_excel(result,config, elec_prod_mtd = elec_prod_mtd)
			#make_pie_plot(result,config, config+'Share_Endpoints')
			result = Share_Midpoints(Configuration.xPKM_overall, Configuration.type_of_analys,
			    Configuration.FL, Configuration.weight_h, Configuration.weight_eco,
				Configuration.weight_r, Configuration.xPKM_Cruise)
			write_to_excel(result,config, elec_prod_mtd = elec_prod_mtd)
			#make_pie_plot(result,config, config+'Share_Midpoints')
					
	return -1
