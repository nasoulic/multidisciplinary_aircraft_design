import math, csv

class thermal_management_system_mass_model(object):

    def __init__(self, run = 0):
        self.run = run
        self.EM_Qflow0 = 0
        self.EG_Qflow0 = 0
        self.Inverter_Qflow0 = 0
        self.Converter_Qflow0 = 0
        self.Batteries_Qflow0 = 0

    def add_name(self, name):
        self.name = name

    def read_input_files(self):

        with open('eps2thermal_mission_run{0}.csv'.format(self.run), 'r') as myfile:
            eps_input = myfile.readlines()

        myfile.close()

        eps_TO = eps_input[6].strip('\n').split(',')
        self.EM_Qflow0 = float(eps_TO[1])
        self.EG_Qflow0 = float(eps_TO[2])
        self.Inverter_Qflow0 = float(eps_TO[3])
        self.Converter_Qflow0 = float(eps_TO[4])
        self.Batteries_Qflow0 = float(eps_TO[5])

    def TMS_mass_calculation(self, m_tot = 0.285, m_bat = 0.1, m_eM = 0.1, m_eG = 0.085, HT_Area = 30):

        '''
        ---------------------------------------------------------------------------------------------------------
        Calculate TMS total mass

        INPUTS:

        m_tot : [required]          Total Mass Flow Rate of Coolant in the TMS [kg/s]
        m_bat : [required]          Mass Flow Rate of Coolant in Battery Route [kg/s]
        m_eM  : [required]          Mass Flow Rate of Coolant in Motor Drive Route (Inverter & eM) [kg/s]
        m_eG  : [required]          Mass Flow Rate of Coolant in Motor Drive Route (Inverter & eM) [kg/s]

        HT_Area : [required]        Total Heat Transfer Area of HEX for specific Heat Load [m2]

        OUTPUTS:

        TMSoutput_runi.csv          .csv file including Thermal Management System overall mass and power requirement
                                    for TMS pump

        ---------------------------------------------------------------------------------------------------------
        '''

        # ------------------------------------------MODEL INPUTS-------------------------------------------------------------
        
        # m_tot = 0.285                   # Total Mass Flow Rate of Coolant in the TMS [Kg/s]
        # m_bat = 0.1                     # Mass Flow Rate of Coolant in Battery Route [Kg/s].
        # m_eM =  0.1                     # Mass Flow Rate of Coolant in Motor Drive Route (Inverter & eM) [Kg/s].
        # m_eG =  0.085                   # Mass Flow Rate of Coolant in Motor Drive Route (Inverter & eM) [Kg/s].

        Coolant_Density = 1044          # Density of Propylene Glycol/Water 47% Mixture at 20 C.
        Dynamic_Viscocity = 0.006264    # Dynamic Viscocity of the Coolant at 20 C.

        D_in = 0.018                    # Inner Diameter of Piping System [m].
        D_out = D_in + 0.002            # Outer Diameter of Pipes with 1 mm Thicknes [m].
        Pipe_Length = 32                # Piping Length of the TMS System [m]

        # HT_Area = 30                    # Total Heat Transfer Area of HEX for specific Heat Load [m2]
        Compactness_Ratio = 1100        # Compactness Ratio of HEX in [m2/m3].
        Comb_MaterialDensity = 2700     # Combined Material Density of HEX in [Kg/m3].
        Porosity_Factor = 0.5           # Porosity Factor of HEX.

        Rejected_Heat = (self.EM_Qflow0 + self.EG_Qflow0 + self.Inverter_Qflow0 + self.Converter_Qflow0 + self.Batteries_Qflow0)

        # --------------------------------FLOW PROPERTIES CALCULATION---------------------------------------------------------

        Kinematic_Viscocity = Dynamic_Viscocity/Coolant_Density       # Kinematic Viscocity of the Coolant at 20 C.
        Q_bat = m_bat/Coolant_Density                                 # Coolant Volumetric Flow Rate in Battery Route [m3/s].
        Q_eM = m_eM/Coolant_Density                                   # Coolant Volumetric Flow Rate in eM Route [m3/s].
        Q_eG = m_eG/Coolant_Density                                   # Coolant Volumetric Flow Rate in eG Route [m3/s].
        Q_tot = Q_bat + Q_eM + Q_eG                                   # Total Coolant Volumetric Flow Rate [m3/s].

        V_bat = (4*m_bat)/(math.pi*Coolant_Density*(D_in**2))         # Flow Velocity in Battery Route [m/s].
        V_eM = (4*m_eM)/(math.pi*Coolant_Density*(D_in**2))           # Flow Velocity in eM Route [m/s].
        V_eG = (4*m_eG)/(math.pi*Coolant_Density*(D_in**2))           # Flow Velocity in eG Route [m/s].
        V_tot = (4*m_tot)/(math.pi*Coolant_Density*(D_in**2))         # Velocity of the total Flow [m/s].

        Re_bat = (Coolant_Density*V_bat*D_in)/Dynamic_Viscocity       # Reynolds number of Battery Route Flow.
        Re_eM = (Coolant_Density*V_eM*D_in)/Dynamic_Viscocity         # Reynolds number of eM Route Flow.
        Re_eG = (Coolant_Density*V_eG*D_in)/Dynamic_Viscocity         # Reynolds number of eG Route Flow.
        Re_tot = (Coolant_Density*V_tot*D_in)/Dynamic_Viscocity       # Reynolds number of the total Flow.


        # --------------------------COMPONENT MASS CALCULATION - 1. HEAT EXCHANGER---------------------------------------------

        Volume_HEX = HT_Area/Compactness_Ratio                                  # Volume of the HEX in [m3].
        W_HEX = Comb_MaterialDensity*Volume_HEX*(1-Porosity_Factor) + \
                (Porosity_Factor/4)*Volume_HEX*Coolant_Density                  # Wet Weight of the HEX in [Kg].

        W_wet_HEX = (Porosity_Factor/4)*Volume_HEX*Coolant_Density

        self.HEX_mass_wet = W_HEX

        # ------------------------- COMPONENT MASS CALCULATION - 2. PIPES-------------------------------------------------------

        Bat_Length = 0.393*Pipe_Length
        eM_Length = 0.112*Pipe_Length
        eG_Length = 0.437*Pipe_Length
        Common_Length = 0.058*Pipe_Length

        f_lam_bat = 64/Re_bat                   # Friction Coeff. at laminar flow in Battery Route.
        f_lam_eM = 64/Re_eM                     # Friction Coeff. at laminar flow in eM Route.
        f_lam_eG = 64/Re_eG                     # Friction Coeff. at laminar flow in eG Route.
        f_lam_common = 64/Re_tot                # Friction Coeff. at laminar flow in Common Route.

        K_roughness = 0.002/1000                # Roughness Coefficient for Al pipes in [mm].

        f_turb_bat = 1/((-1.8*math.log((((K_roughness/D_in)/3.7)**1.11) + 6.9/Re_bat))**2)      # Friction Coeff. at turb. FLow
        f_turb_eM = 1/((-1.8*math.log((((K_roughness/D_in)/3.7)**1.11) + 6.9/Re_eM))**2)        # Friction Coeff. at turb. FLow
        f_turb_eG = 1/((-1.8*math.log((((K_roughness/D_in)/3.7)**1.11) + 6.9/Re_eG))**2)        # Friction Coeff. at turb. FLow
        f_turb_common = 1/((-1.8*math.log((((K_roughness/D_in)/3.7)**1.11) + 6.9/Re_tot))**2)   # Friction Coeff. at turb. FLow

        # Compute pressure drops for lam. and turb. from Darcy - Weisbach

        if Re_bat < 2300:
            DP_bat = (f_lam_bat*(Bat_Length/D_in)*((Coolant_Density*V_bat**2)/2))/100000
        else:
            DP_bat = (f_turb_bat*(Bat_Length/D_in)*((Coolant_Density*V_bat**2)/2))/100000

        if Re_eM < 2300:
            DP_eM = (f_lam_eM*(eM_Length/D_in)*((Coolant_Density*V_eM**2)/2))/100000
        else:
            DP_eM = (f_turb_eM*(eM_Length/D_in)*((Coolant_Density*V_eM**2)/2))/100000
            
        if Re_eG < 2300:
            DP_eG = (f_lam_eG*(eG_Length/D_in)*((Coolant_Density*V_eG**2)/2))/100000
        else:
            DP_eG = (f_turb_eG*(eG_Length/D_in)*((Coolant_Density*V_eG**2)/2))/100000


        if Re_tot < 2300:
            DP_common = (f_lam_common*(Common_Length/D_in)*((Coolant_Density*V_tot**2)/2))/100000
        else:
            DP_common = (f_turb_common*(Common_Length/D_in)*((Coolant_Density*V_tot**2)/2))/100000

        DP_tot = DP_bat + DP_eM + DP_eG + DP_common

        # Material Properties to use for the piping system - Copper, Aluminum

        Cu_Density = 8940           # Density of Copper in [Kg/m3].
        Al_Density = 2700           # Density of Aluminum in [Kg/m3].

        # Mass of empty pipes for each material (Aluminum was used)---------------------------------------

        W_Pipes_bat = ((math.pi/4)*Al_Density*(
                D_out**2 - D_in**2))*Bat_Length                     # Empty weight of Battery Route pipes [Kg].

        W_Pipes_eM = ((math.pi/4)*Al_Density*(
                D_out**2 - D_in**2))*eM_Length                      # Empty weight of eM Route Pipes [Kg].

        W_Pipes_eG = ((math.pi/4)*Al_Density*(
                D_out**2 - D_in**2))*eG_Length                      # Empty weight of eG Route Pipes [Kg].

        W_Pipes_common = ((math.pi/4)*Al_Density*(
                D_out**2 - D_in**2))*Common_Length                  # Empty weight of common Route [Kg].

        W_Pipes_tot = W_Pipes_bat + W_Pipes_eM + W_Pipes_eG + W_Pipes_common     # Total weight of empty pipes [Kg].

        self.piping_mass = W_Pipes_tot

        # ------------------------- COMPONENT MASS CALCULATION - 3. COOLANT-------------------------------------------------------

        W_Coolant = (Coolant_Density*(math.pi/4)*(
                D_in**2))*Pipe_Length                               # Weight of Coolant in Pipes [Kg].
        Volume_Coolant = W_Coolant/Coolant_Density                  # Volume of Coolant in Pipes or Reservoir [m3].

        self.coolant_mass = W_Coolant

        # ------------------------- COMPONENT MASS CALCULATION - 4. COOLANT RESERVOIR---------------------------------------------

        K_Reservoir = 1.2                                       # Fitting Factor of Reservoir to adjust to Coolant Volume [-].
        Inner_Volume_Tank = K_Reservoir * Volume_Coolant        # Volume of a solid material Reservoir [m3].
        Volume_Tank = ((Inner_Volume_Tank**(1/3) +
                        0.002)**3) - Inner_Volume_Tank          # Actual Volume of the Empty Coolant Reservoir [m3].
        W_Reservoir = Volume_Tank*Al_Density                    # Weight of Coolant Reservoir with Al as Material [Kg].

        self.coolant_reservoir_mass = W_Reservoir

        # ------------------------- COMPONENT MASS CALCULATION - 5. PUMP(S)-------------------------------------------------------

        Displacement_Pump = 0.64815 * ((Q_tot)**(1.3857))       # Specific Mass FLow Rate of Small Pumps [Kg/m3/s] - Regression.
        DP_Pump = DP_tot + 2 + 1                                # System Pressure Increase from Pump [bar].


        # Efficiencies and Specific Power of several pump components to calculate pump requirements

        Eff_Impeller = 0.85                                     # Impeller Efficiency
        Eff_eMotor = 0.95                                       # Electric Motor Efficiency
        Eff_eGenerator = 0.95                                   # Electric Generator Efficiency
        Eff_eMC = 0.96                                          # Inverter Efficiency
        Eff_eGC = 0.96                                          # Converter Efficiency
        Eff_Total = Eff_Impeller*Eff_eMotor*Eff_eMC*Eff_eGenerator*Eff_eGC             # Total Efficiency of Pump

        K_Pump = 237879.8                               # Pump factor, based on the units transformation to get mass in [Kg]

        W_Pump = (K_Pump*Displacement_Pump) + 1.1       # Total Weight of Centrifugal Pump in [Kg].

        self.pump_mass = W_Pump

        # ## Edit by C. P. Nasoulis 19/05/2022 BEGIN  ##

        # Dp = Coolant_Density*9.81*2                     # DP = rho*g*h, rho = coolant density kg/m3 , g = 9.81 m/s2, h = 2 m (head)
        # q_flow = m_tot/Coolant_Density                  # [m3/s]
        # P_Pump = Dp*q_flow/Eff_Total                    # [W]

        # ## Edit by C. P. Nasoulis 19/05/2022 END  ##

        P_Pump = 5000 # [W] (includes ecs model)

        # P_Pump = 3.6*m_tot*Coolant_Density*9.81*2*Eff_Total/3600000    # Pump Power calculation for g=9.81 m^2/s  head=2 m


        # ----------------------THEMAL MANAGEMENT SYSTEM OVERALL MASS WITHOUT COLD PLATES FOR EPS COOLING-------------------------

        TMS_W_woCPs = W_HEX + W_Pipes_tot + W_Coolant + W_Reservoir + W_Pump            # Total TMS Weight for EPS in [Kg].
        CSP_woCPs = Rejected_Heat/TMS_W_woCPs                                           # Combined Specific Power of TMS.

        # print("Total weight without cold plates is", TMS_W_woCPs)
        self.csp = CSP_woCPs
        self.tms_mass_no_cold_plates = TMS_W_woCPs
        self.tms_pump_power_req = P_Pump

        
        self.mass_breakdown = {
            "HEX" : self.HEX_mass_wet,
            "Piping" : self.piping_mass,
            "Coolant" : self.coolant_mass,
            "Coolant reservoir" : self.coolant_reservoir_mass,
            "Pump" : self.pump_mass,
            "TMS" : self.tms_mass_no_cold_plates
        }

        return TMS_W_woCPs, P_Pump/1000

    def export_HECARRUS_outputs(self):

        heccarus_vnames = ['HECARRUS Variable Names', 'FailCode', 'thermal2acsizing_W_TMS_tot', 'thermal2mission_W_TMS_tot', 'thermal2energyflow_P_TMS_req']
        variable_names = ['Variable Names', 'FailCode', 'W_TMS_tot', 'W_TMS_tot', 'P_TMS_req']
        variable_symbols = ['Variable Symbols', 'FailCode', 'W_TMS_tot', 'W_TMS_tot', 'P_TMS_req']
        variable_units = ['Variable Units', '-', 'kg', 'kg', 'kW']

        var_vals = ['Single Value', -1, self.tms_mass_no_cold_plates, self.tms_mass_no_cold_plates, self.tms_pump_power_req/1000]

        with open('TMSoutput_run{0}.csv'.format(self.run), 'w', newline = '') as myfile:
            write = csv.writer(myfile, )
            write.writerows([heccarus_vnames, variable_names, variable_symbols, variable_units, [""], var_vals])
        myfile.close()

        with open('thermal2acsizing_run{0}.csv'.format(self.run), 'w', newline = '') as myfile:
            write = csv.writer(myfile, )
            write.writerows([heccarus_vnames[0:3], variable_names[0:3], variable_symbols[0:3], variable_units[0:3], [""], var_vals[0:3]])
        myfile.close()

        with open('thermal2mission_run{0}.csv'.format(self.run), 'w', newline = '') as myfile:
            write = csv.writer(myfile, )
            write.writerows([[heccarus_vnames[0], heccarus_vnames[1], heccarus_vnames[-2]], 
                             [variable_names[0], variable_names[1], variable_names[-2]], 
                             [variable_symbols[0], variable_symbols[1], variable_symbols[-2]], 
                             [variable_units[0], variable_units[1], variable_units[-2]], [""], [var_vals[0], var_vals[1], var_vals[-2]]])
        myfile.close()

        with open('thermal2energyflow_run{0}.csv'.format(self.run), 'w', newline = '') as myfile:
            write = csv.writer(myfile, )
            write.writerows([[heccarus_vnames[0], heccarus_vnames[1], heccarus_vnames[-1]], 
                             [variable_names[0], variable_names[1], variable_names[-1]], 
                             [variable_symbols[0], variable_symbols[1], variable_symbols[-1]], 
                             [variable_units[0], variable_units[1], variable_units[-1]], [""], [var_vals[0], var_vals[1], var_vals[-1]]])
        myfile.close()