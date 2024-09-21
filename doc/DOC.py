import numpy as np
import matplotlib.pyplot as plt

class Direct_Operating_Cost(object):

    def __init__(self):
        
        self.name = ""
        self.EIS = 0

    def set_name(self, name):

        self.name = name

    def set_EIS(self, date):

        self.EIS = date

    def initialize(self):
        
        self.read_input(self.fname)
        self.Define_Inputs()

    def replace_inputs_from_acsizing(self):

        set1 = set(self.general_inputs.keys())
        set2 = set(self.from_acsizing.keys())

        for sname in set1.intersection(set2):
            self.general_inputs[sname] = self.from_acsizing[sname]

        set1 = set(self.aircraft.keys())

        for sname in set1.intersection(set2):
            self.aircraft[sname] = self.from_acsizing[sname]

        self.general_inputs.update( { 'Pot_Y_Op_T' : self.general_inputs['Days_in_Year']*24, # Potential Yearly Operating Time [hrs] 
                         'Checks_repairs_h' : self.general_inputs['Checks_repairs']*24,
                         'Operating_days' : self.general_inputs['Days_in_Year'] - self.general_inputs['Checks_repairs'],
                         'Daily_Total_Time' : 24*60, # [min]
                         'Daily_Off_Time' : self.general_inputs['Daily_Off_Time']*60, # [min]
                          } )
        
        self.general_inputs.update( { 'Daily_Available_flight_time' : self.general_inputs['Daily_Total_Time'] - self.general_inputs['Daily_Off_Time'],
                         'Seasonal_off_time' : self.general_inputs['Operating_days']*self.general_inputs['Daily_Off_Time'], } )

        self.general_inputs.update( { 'Available_flights' : self.general_inputs['Daily_Available_flight_time']/self.general_inputs['Block_Time'] } )

        self.general_inputs.update( { 'Annual_Flight_cycles' : self.general_inputs['Available_flights']*self.general_inputs['Operating_days'],
                         'Block_Time_h' : self.general_inputs['Block_Time']/60, } )
        
        self.general_inputs.update( { 'Annual_block_time' : self.general_inputs['Block_Time_h']*self.general_inputs['Annual_Flight_cycles']})


    def read_input(self, filename):

        self.fname = filename
        
        with open(filename, 'r') as myfile:
            data = myfile.readlines()
        myfile.close()

        from_acsizing = {}

        for line in data:
            tmp = line.strip('\n').split(',')
            from_acsizing[tmp[0]] = float(tmp[1])

        self.from_acsizing = from_acsizing

    def load_data_from_input_list(self, input_list):

        INPUTS = {
            'Block_Time' : input_list["block_time_input"], # Mission time [min]
            'Days_in_Year' : input_list["days_in_year_input"], # Days
            'Checks_repairs' : input_list["checks_repairs_input"], # Days
            'Years' : input_list["years_examined_input"], # Years examined
            'Daily_Off_Time' : input_list["day_off_time_input"], # Closed airport hours [h]
            'Navigation_Factor' : input_list["navigation_factor_input"], # [euro/km]
            'Fixed_cost_kREP' : input_list["fixed_cost_per_flight_input"], # [euro]
        }

        ENERGY_PRICING = {
            'Fuel_price' : input_list["fuel_price_input"], # [euro/kg] uncertain parameter
            'Energy_price' : input_list["electricity_price_input"], # [euro/kWh] uncertain parameter
        }

        LABOR = { 'Crew_compliments' : input_list["crew_complements_input"],
                  'Pilot' : input_list["pilots_input"],
                  'Crew' : input_list["crew_input"],
                  'Pilot_salary' : input_list["pilot_salary_input"], # [euro]
                  'Crew_salary' : input_list["crew_salary_input"], # [euro]
                  'Labor_cost' : input_list["labor_cost_input"], # [euro/hour]
            }

        AIRCRAFT = { 
            'Fuel_Burn' : input_list["block_fuel_input"], # [kg]
            'Battery_Energy' : input_list["battery_energy_input"], # [kWh]
            'Payload' : input_list["payload_input"], # [kg]
            'MTOW' : input_list["max_takeoff_mass_input"], # [kg]
            'Range' : input_list["mission_range_input"], # [km]
            'Empty_Weight' : input_list["empty_mass_input"], # [kg]
            'Propulsion_Weight' : input_list["propulsion_mass_input"], # [kg]
            'Wing_Span' : input_list["wing_span_input"], # [m]
            'Fuselage_Length' : input_list["fuselage_length_input"], # [m]
            'Vtakeoff' : input_list["v1_velocity_input"], # [m/s]
            'P_GT_max' : input_list["max_total_gt_power_input"], # [kW]
            'P_EM_max' : input_list["max_em_power_input"], # [kW]
            'Battery_cycles' : input_list["battery_cycles_input"], # Cycles
            'Battery_Sets' : input_list["battery_sets_input"], 
        }

        CAPITAL = { 'Depreciation_period' : input_list["depreciation_period_input"],
                    'Interest_Rate' : input_list["interest_rate_input"]/100,
                    'fRV' : input_list["residual_value_factor_input"], # Residual Value Factor
                    'fINS' : input_list["insurance_rate_input"]/100, # Insurance Rate
                    'Airframe_price_per_kg' : input_list["airframe_price_input"], # [euro/kg] uncertain parameter
                    'GT_price_per_kW' : input_list["gas_turbine_price_input"], # [euro/kW] uncertain parameter
                    'EM_price_per_kW' : input_list["electric_motor_price_input"], # [euro/kW] uncertain parameter
                    'Inv_price_per_kW' : input_list["inverter_price_input"], # [euro/kW] uncertain parameter
                    'Bat_price_per_kWh' : input_list["battery_price_input"], # [euro/kWh] uncertain parameter
                    'k_EPS' : input_list["k_eps_input"], # Factor k Electrical Power System
                    'k_GT' : input_list["k_gt_input"], # Factor k Gas Turbine
                    'k_AF' : input_list["k_af_input"], # Factor k Airframe
                    'eta_EM' : input_list["eta_em_input"], # Electrical Motor Efficiency
                    'eta_PMAD' : input_list["eta_pmad_input"], # PMAD Efficiency
                    }

        self.general_inputs = INPUTS
        self.energy_pricing = ENERGY_PRICING
        self.aircraft = AIRCRAFT
        self.labor = LABOR
        self.capital = CAPITAL

        self.general_inputs.update( { 'Pot_Y_Op_T' : self.general_inputs['Days_in_Year']*24, # Potential Yearly Operating Time [hrs] 
                         'Checks_repairs_h' : self.general_inputs['Checks_repairs']*24,
                         'Operating_days' : self.general_inputs['Days_in_Year'] - self.general_inputs['Checks_repairs'],
                         'Daily_Total_Time' : 24*60, # [min]
                         'Daily_Off_Time' : self.general_inputs['Daily_Off_Time']*60, # [min]
                          } )
        
        self.general_inputs.update( { 'Daily_Available_flight_time' : self.general_inputs['Daily_Total_Time'] - self.general_inputs['Daily_Off_Time'],
                         'Seasonal_off_time' : self.general_inputs['Operating_days']*self.general_inputs['Daily_Off_Time'], } )

        self.general_inputs.update( { 'Available_flights' : self.general_inputs['Daily_Available_flight_time']/self.general_inputs['Block_Time'] } )

        self.general_inputs.update( { 'Annual_Flight_cycles' : self.general_inputs['Available_flights']*self.general_inputs['Operating_days'],
                         'Block_Time_h' : self.general_inputs['Block_Time']/60, } )
        
        self.general_inputs.update( { 'Annual_block_time' : self.general_inputs['Block_Time_h']*self.general_inputs['Annual_Flight_cycles']})


    def Define_Inputs(self, fp = 0.79, ep = 0.115, afc = 1595.3, bat_price = 150, gt_price = 551.5, em_price = 150, inv_price = 75):

        INPUTS = {
            'Block_Time' : 185, # Mission time [min]
            'Days_in_Year' : 365, # Days
            'Checks_repairs' : 11.4, # Days
            'Years' : 1, # Years examined
            'Daily_Off_Time' : 7, # Closed airport hours [h]
            'Navigation_Factor' : 850, # [euro/km]
            'Fixed_cost_kREP' : 100, # [euro]
        }

        AIRCRAFT = { 
            'Fuel_Burn' : 767.35, # [kg]
            'Battery_Energy' : 0, # [kWh]
            'Payload' : 1938, # [kg]
            'MTOW' : 7384.75, # [kg]
            'Range' : 1111, # [km]
            'Empty_Weight' : 4373.25, # [kg]
            'Propulsion_Weight' : 700, # [kg]
            'Wing_Span' : 16.62, # [m]
            'Fuselage_Length' : 12.98, # [m]
            'Vtakeoff' : 51, # [m/s]
            'P_GT_max' : 1386.75, # [kW]
            'P_EM_max' : 0, # [kW]
            'Battery_cycles' : 1500, # Cycles
            'Battery_Sets' : 3, 
        }

        ENERGY_PRICING = {
            'Fuel_price' : fp, # [euro/kg] uncertain parameter
            'Energy_price' : ep, # [euro/kWh] uncertain parameter
        }

        LABOR = { 'Crew_compliments' : 5,
                  'Pilot' : 1,
                  'Crew' : 0,
                  'Pilot_salary' : 80000, # [euro]
                  'Crew_salary' : 40000, # [euro]
                  'Labor_cost' : 50, # [euro/hour]
            }

        CAPITAL = { 'Depreciation_period' : 20,
                    'Interest_Rate' : 0.2,
                    'fRV' : 0.1, # Residual Value Factor
                    'fINS' : 0.005, # Insurance Rate
                    'Airframe_price_per_kg' : afc, # [euro/kg] uncertain parameter
                    'GT_price_per_kW' : gt_price, # [euro/kW] uncertain parameter
                    'EM_price_per_kW' : em_price, # [euro/kW] uncertain parameter
                    'Inv_price_per_kW' : inv_price, # [euro/kW] uncertain parameter
                    'Bat_price_per_kWh' : bat_price, # [euro/kWh] uncertain parameter
                    'k_EPS' : 0.2, # Factor k Electrical Power System
                    'k_GT' : 0.3, # Factor k Gas Turbine
                    'k_AF' : 0.1, # Factor k Airframe
                    'eta_EM' : 0.96, # Electrical Motor Efficiency
                    'eta_PMAD' : 0.98, # PMAD Efficiency
                    }

        self.general_inputs = INPUTS
        self.energy_pricing = ENERGY_PRICING
        self.aircraft = AIRCRAFT
        self.labor = LABOR
        self.capital = CAPITAL

    def Evaluate_Design(self):

        years = self.general_inputs['Years']

        energy = self.Energy_Direct_Operating_Cost()
        crew = self.Crew_Direct_Operating_Cost()
        maintenance = self.Maintenance_Direct_Operating_Cost()
        fees = self.Fees_Direct_Operating_Cost()
        capital = self.Capital_Direct_Operating_Cost()

        annual = {
            'Energy' : energy,
            'Crew' : crew,
            'Maintenance' : maintenance,
            'Fees' : fees,
            'Capital' : capital
        }

        total_annual_cost = 0
        total_cost = 0

        total = { }
        for key, item in annual.items():
            total.update( { key : item*years } )
            total_annual_cost = total_annual_cost + item
            total_cost = total_cost + item*years

        labels = []
        size_annual = []
        size_total = []
        for key in annual.keys():
            labels.append(key)
            size_annual.append(annual[key]/total_annual_cost)
            size_total.append(total[key]/total_cost)
        
        self.labels = labels
        self.annual = size_annual
        self.total = size_total
        self.total_annual_cost = total_annual_cost
        self.total_cost = total_cost
        self.annual_abs = annual


    def Energy_Direct_Operating_Cost(self):
        
        # Variables Initialization BEGIN
        afc = self.general_inputs['Annual_Flight_cycles']
        fuel_burn = self.aircraft['Fuel_Burn']
        fuel_price = self.energy_pricing['Fuel_price']
        battery_energy = self.aircraft['Battery_Energy']
        energy_price = self.energy_pricing['Energy_price']
        # Variables Initialization END
        
        DOC_energy = afc*(fuel_burn*fuel_price + battery_energy*energy_price)

        self.doc_energy_fuel = afc*fuel_burn*fuel_price
        self.doc_energy_battery = afc*battery_energy*energy_price

        return DOC_energy

    def Crew_Direct_Operating_Cost(self):

        # Variables Initialization BEGIN
        Crew_compliments = self.labor['Crew_compliments']
        Pilot = self.labor['Pilot']
        Crew = self.labor['Crew']
        pilot_salary = self.labor['Pilot_salary']
        crew_salary = self.labor['Crew_salary']
        # Variables Initialization END

        DOC_Crew = Crew_compliments*(Pilot*pilot_salary + Crew*crew_salary)

        self.doc_crew = DOC_Crew

        return DOC_Crew

    def Fees_Direct_Operating_Cost(self):

        # Variables Initialization BEGIN
        MTOW = self.aircraft['MTOW']
        Payload = self.aircraft['Payload']
        Range = self.aircraft['Range']
        block_time = self.general_inputs['Block_Time_h']
        afc = self.general_inputs['Annual_Flight_cycles']
        nav_fact = self.general_inputs['Navigation_Factor']
        # Variables Initialization END

        Ln_t_total = np.log(block_time)
        factor = (MTOW/50000)**0.5

        DOC_Landing = (9.5*1e-3 - Ln_t_total*1e-3)*MTOW*afc

        DOC_Ground = (0.11*Payload - 5e-7*Payload**2)*afc

        DOC_Nav = nav_fact*Range/1000*factor*afc

        self.doc_landing = DOC_Landing
        self.doc_ground = DOC_Ground
        self.doc_nav = DOC_Nav

        return DOC_Ground + DOC_Landing + DOC_Nav

    def Maintenance_Direct_Operating_Cost(self):

        # Variables Initializatin BEGIN
        Wempty = self.aircraft['Empty_Weight']
        Wpropulsion = self.aircraft['Propulsion_Weight']
        fixed_krep_cost = self.general_inputs['Fixed_cost_kREP']
        Vtakeoff = self.aircraft['Vtakeoff']
        P_GT_max = self.aircraft['P_GT_max']
        Wing_span = self.aircraft['Wing_Span']
        Fuselage_length = self.aircraft['Fuselage_Length']
        block_time =  self.general_inputs['Block_Time_h']
        labor_cost = self.labor['Labor_cost']
        afc = self.general_inputs['Annual_Flight_cycles']
        # Variables Initialization END

        Wairframe = Wempty - Wpropulsion

        DOC_AF_Mat = Wairframe*(0.0010136*block_time + 0.0012632) + fixed_krep_cost

        DOC_AF_Per = labor_cost*((Wairframe*1e-4 + 0.5)*block_time + (Wairframe*1e-4 + 0.25))

        DOC_Eng = 7.621*1e-4*((0.64545*P_GT_max)/Vtakeoff) + (30.5*block_time) + 10.6

        DOC_Tec = 5*((Wing_span*Fuselage_length)**0.75)

        self.doc_af_mat = DOC_AF_Mat*afc
        self.doc_af_per = DOC_AF_Per*afc
        self.doc_eng = DOC_Eng*afc
        self.doc_tec = DOC_Tec*afc

        return afc*(DOC_AF_Mat + DOC_AF_Per + DOC_Eng + DOC_Tec)

    def Capital_Direct_Operating_Cost(self):

        # Variables Initializatin BEGIN
        dpr_p = self.capital['Depreciation_period']
        int_r = self.capital['Interest_Rate']
        frv = self.capital['fRV']
        fINS = self.capital['fINS']
        Wairframe = self.aircraft['Empty_Weight'] - self.aircraft['Propulsion_Weight']
        airframe_cost = self.capital['Airframe_price_per_kg']
        P_GT_max = self.aircraft['P_GT_max']
        P_EM_max = self.aircraft['P_EM_max']
        kAF = self.capital['k_AF']
        kEPS = self.capital['k_EPS']
        kGT = self.capital['k_GT']
        etaEM = self.capital['eta_EM']
        eta_PMAD = self.capital['eta_PMAD']
        GTprice = self.capital['GT_price_per_kW']
        EMprice = self.capital['EM_price_per_kW']
        Invprice = self.capital['Inv_price_per_kW']
        Batprice = self.capital['Bat_price_per_kWh']
        battery_cycles = self.aircraft['Battery_cycles']
        afc = self.general_inputs['Annual_Flight_cycles']
        Battery_Sets = self.aircraft['Battery_Sets']
        Battery_energy = self.aircraft['Battery_Energy']
        # Variables Initialization END

        annuity_rate = int_r*((1 - frv*((1/(1 + int_r))**dpr_p))/(1 - ((1/(1 + int_r))**dpr_p)))
        battery_depreciation = 3*(battery_cycles/afc)
        annuity_rate_bat = 0.2*((1 - 0.4*((1/(1 + 0.2))**battery_depreciation))/(1 - ((1/(1 + 0.2))**battery_depreciation)))

        airframe_price = Wairframe*airframe_cost

        DOC_capital_AF = airframe_price*(1 + kAF) # Airframe Capital DOC
        DOC_capital_GT = (P_GT_max*GTprice)*(1 + kGT) # Gas Turbine Capital DOC
        DOC_capital_EM = (P_EM_max*EMprice)*(1 + kEPS) # Gas Turbine Capital DOC
        DOC_capital_PMAD = Invprice*((P_EM_max/(etaEM*eta_PMAD)) + (P_EM_max/(etaEM*eta_PMAD*eta_PMAD)))*(1 + kEPS) # PMAD Capital DOC

        DOC_CAP_AC = (DOC_capital_AF + DOC_capital_GT + DOC_capital_EM + DOC_capital_PMAD)*(annuity_rate + fINS)

        DOC_CAP_BAT = Battery_Sets*Battery_energy*Batprice*(annuity_rate_bat + int_r)

        self.doc_cap_ac = DOC_CAP_AC
        self.doc_cap_bat = DOC_CAP_BAT

        return DOC_CAP_AC + DOC_CAP_BAT

    def make_pie(self, lab, s, file_name):
        
        labels = lab
        sizes = s
        
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels = labels, autopct = '%1.1f%%', shadow = True, startangle = 90)
        ax1.axis('equal') # Equal aspect ratio
        plt.savefig(file_name, dpi = 300)
        plt.close()

    def write_outputs(self, f_name, ctype = "full"):

        if ctype != "full" and ctype != "simple":
            raise ValueError("Wrong input value at ctype optional variable. Acceptable values are 'simple' and 'full'.")

        with open(f_name, 'w+') as f:

            if ctype == "full":
                for key, item in self.direct_operating_cost_breakdown.items():
                    f.write('%s, %f \n' %(key, item))
            else:
                for lab, val in zip(self.labels, self.total):
                    f.write('%s, %f \n' %(lab, val*self.total_annual_cost))

        f.close()

    def doc_breakdown(self):

        doc = {
            'Energy fuel' : self.doc_energy_fuel,
            'Energy batteries' : self.doc_energy_battery,
            'Crew' : self.doc_crew,
            'Landing fees' : self.doc_landing,
            'Ground handling fees' : self.doc_ground,
            'Navigation fees' : self.doc_nav,
            'Maintenance Tech' : self.doc_tec,
            'Maintenance Eng' : self.doc_eng,
            'Maintenance AF Per' : self.doc_af_per,
            'Maintenance AF Mat' : self.doc_af_mat,
            'Batteries capital' : self.doc_cap_bat,
            'Aircraft capital' : self.doc_cap_ac
        }

        self.direct_operating_cost_breakdown = doc
        