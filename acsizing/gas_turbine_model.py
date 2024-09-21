class gas_turbine(object):

    def __init__(self):        
        pass

    def gas_generator_characteristics(self, const_eff = True):


        '''
        ----------------------------------------------------------------------------------
        DEFINE GAS GENERATOR BASIC CHARACTERISTICS
        ----------------------------------------------------------------------------------
        '''

        self.efficiency = {}
        self.eta_dp = 0.4                   # gas generator efficiency at design point  [-]

        operating_points = ['Taxi-out', 'Take-off', 'Climb', 'Cruise', 'Descent', 'Approach and Landing', 
                'Taxi-in', 'Overshoot', 'DivClimb', 'DivCruise', 'DivDescent',
                'Hold', 'Div Approach and Landing']
        if const_eff:
            for key in operating_points:
                self.efficiency[key] = self.eta_dp
        
        self.fuel_LHV = 43e3                # fuel lower heating value                  [kJ/kg]
        self.mass = 256                     # gas generator mass (MAESTRO)              [kg]
        self.fuel_rho = 0.804               # fuel density [kg/L]
        self.fuel_energy_density = 9.6      # fuel energy density [kWh/L]

    def gas_generator_characteristics_from_GUI(self, from_GUI, const_eff = True):

        self.fuel_LHV = float(from_GUI.fuel_LHV_GUI)                           # fuel lower heating value                  [kJ/kg]
        self.mass = float(from_GUI.mass_GUI)                                   # core mass PT6A-67D                        [kg]
        self.fuel_rho = float(from_GUI.fuel_rho_GUI)                           # fuel density [kg/L]
        self.fuel_energy_density = float(from_GUI.fuel_energy_density_GUI)     # fuel energy density [kWh/L]

        operating_points = ['Taxi-out', 'Take-off', 'Climb', 'Cruise', 'Descent', 'Approach and Landing', 
                'Taxi-in', 'Overshoot', 'DivClimb', 'DivCruise', 'DivDescent',
                'Hold', 'Div Approach and Landing']
        
        self.efficiency = {}

        if const_eff:
            for key in operating_points:
                self.efficiency[key] = float(from_GUI.efficiency_GUI)

    def turbobprop_characteristics(self, sfc_red = 0.):

        '''
        ----------------------------------------------------------------------------------
        DEFINE TURBOPROP BASIC CHARACTERISTICS
        ----------------------------------------------------------------------------------
        '''

        self.fuel_LHV = 43e3                # fuel lower heating value                  [kJ/kg]
        self.mass = 233.5                   # core mass PT6A-67D                        [kg]
        self.fuel_rho = 0.804               # fuel density [kg/L]
        self.fuel_energy_density = 9.6      # fuel energy density [kWh/L]
        self.bsfc = {                       # [kg/kWh]
                    'Taxi-out' : 0.4,
                    'Take-off' : 0.32607,
                    'Climb' : 0.3346,
                    'Cruise' : 0.3346,
                    'Descent' : 0.3954,
                    'Approach and Landing' : 0.3954,
                    'Taxi-in' : 0.4,
                    'Overshoot' : 0.32607,
                    'DivClimb' : 0.3346,
                    'DivCruise' : 0.3346,
                    'DivDescent' : 0.3954,
                    'Hold' : 0.3954,
                    'Div Approach and Landing' : 0.3954,
            }
        self.thermal_efficiency(sfc_red)

    def update_turboprop_characteristics_from_GUI(self, from_GUI, sfc_red = 0):
        
        self.fuel_LHV = float(from_GUI.fuel_LHV_GUI)                           # fuel lower heating value                  [kJ/kg]
        self.mass = float(from_GUI.mass_GUI)                                   # core mass PT6A-67D                        [kg]
        self.fuel_rho = float(from_GUI.fuel_rho_GUI)                           # fuel density [kg/L]
        self.fuel_energy_density = float(from_GUI.fuel_energy_density_GUI)     # fuel energy density [kWh/L]

        self.bsfc = {}

        for key in from_GUI.bsfc_GUI.keys():
            self.bsfc[key] = float(from_GUI.bsfc_GUI[key])

        self.thermal_efficiency(sfc_red)
    
    def thermal_efficiency(self, sfc_red):

        '''
        ----------------------------------------------------------------------------------
        Calculate thermal efficiency from break specific fuel consumption
        ----------------------------------------------------------------------------------
        '''
        Sp = self.fuel_energy_density/self.fuel_rho
        self.efficiency = {}
        for key, item in self.bsfc.items():
            self.efficiency[key] = 1/(item*Sp*(1 - sfc_red))

    def fuel_requirement(self, P, eta):

        '''
        ----------------------------------------------------------------------------------
        CALCULATE FUEL MASS FLOW FOR EACH POINT
        ----------------------------------------------------------------------------------
        '''

        Q_thermal = P/eta                   # Calculate thermal power                   [kW]
        m_f = Q_thermal/self.fuel_LHV       # Fuel mass flow requirement                [kg/s]

        return m_f