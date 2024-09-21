from scipy.optimize import fsolve
import numpy as np
import os

class heat_exchanger(object):

    def __init__(self):

        '''
        ------------------------------------------------------------------
        Call class constructor and initialize default values
        ------------------------------------------------------------------
        '''

        self.R_fouling = 1e-4 # [m2K/W] Default fouling value
        self.tube_dh = 0.018 # primary flow default hydraulic diameter
        self.outer_Dh = 0.24 # secondary flow default hyrdaulic diameter

    def set_fouling(self, fouling):

        '''
        ------------------------------------------------------------------
        Set fouling value
        ------------------------------------------------------------------
        '''

        self.R_fouling = fouling
    
    def set_primary_flow_type(self, flow_type):

        '''
        ------------------------------------------------------------------
        Force the primary flow type. Acceptable values are :
        
        1. "Laminar",
        2. "Turbulent"
        ------------------------------------------------------------------
        '''

        self.flow_type = flow_type
    
    def add_name(self, name):

        '''
        ------------------------------------------------------------------
        Set object's name
        ------------------------------------------------------------------
        '''

        self.name = name

    def set_secondary_flow_hydraylic_diameter(self, dh):

        '''
        ------------------------------------------------------------------
        Set secondary flow hyrdaulic diameter
        ------------------------------------------------------------------
        '''

        self.outer_Dh = dh

    def set_primary_flow_hydraylic_diameter(self, dh):

        '''
        ------------------------------------------------------------------
        Set primary flow hydraulic diameter
        ------------------------------------------------------------------
        '''

        self.tube_dh = dh

    def set_material(self, mat):

        '''
        ------------------------------------------------------------------
        Define HEX material. At the moment only "Aluminum" is supported.
        ------------------------------------------------------------------
        '''

        if mat == "Aluminum":
            '''
            ------------------------------------------------------
            Thermal resistance of aluminum wall
            ------------------------------------------------------
            '''
            self.lamda_mat = 239                        # [W/mK]
            self.thickness = 0.001                      # [m]
            self.R = self.thickness/self.lamda_mat      # [m2K/W]
        else:
            raise ValueError("Aluminum material is the only material supported at the moment.")


    def eps_NTU(self, primary_phase, secondary_phase, write_sizing_report = False):

        '''
        ------------------------------------------------------------------
        Apply epsilon-NTU method for heat-exchanger sizing

        INPUTS:
        primary_phase   : [object] [reqiured]       coolant mass flow
        secondary_phase : [object] [required]       coolant mean temperature

        Each object has a list obj.flow_conditions with items in list for
        primary and secondary phases:
            0.  coolant mass flow       [kg/s]
            1.  specific heat           [J/kgK]
            2.  Outlet temperature      [K]
            3.  Inlet temperature       [K]


        OUTPUTS:
        A       : [m2]                            heat exchanger area
        ------------------------------------------------------------------
        '''

        m_flow1, cp1, Tout1, Tin1 = primary_phase.flow_conditions

        m_flow2, cp2, Tout2, Tin2 = secondary_phase.flow_conditions

        Q1 = m_flow1*cp1*abs(Tout1 - Tin1)
        Q2 = m_flow2*cp2*abs(Tout2 - Tin2)

        if abs(Q1 - Q2) > 0.02*Q1:                                      # Allowing for a maximum of 2 % losses
            raise ValueError("Thermal loads Q1 and Q2 do not match. Please check inputs.")

        Cmin = min(m_flow1*cp1, m_flow2*cp2)
        Cmax = max(m_flow1*cp1, m_flow2*cp2)
        self.Crel = Cmin/Cmax
        
        Qmax = Cmin*abs(Tin1 - Tin2)

        self.eps = min(Q1, Q2)/Qmax

        if self.eps >= 1:
            raise ValueError("Epsilon greater or equal to 1. Please check secondary flow inputs.")
        
        ntu = fsolve(self.solve_NTU, (1.))[0]

        '''
        ------------------------------------------------------
        Geometrical properties of HX to achieve desired 
        thermal convection coefficient
        ------------------------------------------------------
        '''
        converged = False

        outer_Dh = self.outer_Dh
        tube_D = self.tube_dh
        a, b = self.hx_box_compactness(outer_Dh)

        while not converged:

            n_passes = int(b/tube_D)
            tube_len = n_passes*a*1.2 # accounting for 20 % increased piping length due to min tube curvature radius

            '''
            ------------------------------------------------------
            Overal convection coefficient calculation
            ------------------------------------------------------
            '''

            # h_primary, is_turbulent = self.convection_coefficient_primary(m_flow1, 0.5*(Tin1 + Tout1), Dh = tube_D, d_L = tube_D/tube_len)
            h_primary, is_turbulent = self.convection_coefficient_primary(primary_phase, Dh = tube_D, d_L = tube_D/tube_len)
            if self.flow_type == "Laminar":
                if is_turbulent:
                    tube_D = tube_D + 0.001
                else:
                    converged = True
            else:
                converged = True

        self.tube_dh = tube_D # Update changes in tube hydraulic diameter

        h_secondary = self.convection_coefficient_secondary(secondary_phase, Dh = outer_Dh)

        U = 1/(1/h_primary + self.R + 2*self.R_fouling + 1/h_secondary)

        A = Cmin*ntu/U                                      # [m2]

        if write_sizing_report:
            with open('./HEX_SIZING_REPORT.dat', 'w') as myfile:
                myfile.write("Primary phase\n")
                myfile.write("==================================\n")
                myfile.write("Inlet temperature: {0} [K]\n".format(np.round(Tin1, 2)))
                myfile.write("Outlet temperature: {0} [K]\n".format(np.round(Tout1, 2)))
                myfile.write("Mass flow: {0} [kg/s]\n".format(np.round(m_flow1, 2)))
                myfile.write("Specific heat: {0} [J/kgK]\n".format(np.round(cp1, 2)))
                myfile.write("Convection coefficient: {0} [W/m2K]\n".format(np.round(h_primary, 2)))
                myfile.write("Coolant medium: {0} \n".format(primary_phase.coolant_medium.name))
                myfile.write("==================================\n")
                myfile.write("\n\n")
                myfile.write("Secondary phase\n")
                myfile.write("==================================\n")
                myfile.write("Inlet temperature: {0} [K]\n".format(np.round(Tin2, 2)))
                myfile.write("Outlet temperature: {0} [K]\n".format(np.round(Tout2, 2)))
                myfile.write("Mass flow: {0} [kg/s]\n".format(np.round(m_flow2, 2)))
                myfile.write("Specific heat: {0} [J/kgK]\n".format(np.round(cp2, 2)))
                myfile.write("Convection coefficient: {0} [W/m2K]\n".format(np.round(h_secondary, 2)))
                myfile.write("Coolant medium: {0} \n".format(secondary_phase.coolant_medium.name))
                myfile.write("==================================\n")
                myfile.write("\n\n")
                myfile.write("HEX characteristics\n")
                myfile.write("==================================\n")
                myfile.write("HEX Area: {0} [m2]\n".format(np.round(A, 2)))
                myfile.write("Heat transfer coefficient: {0} [W/m2K]\n".format(np.round(U, 2)))
                myfile.write("Primary phase tube diameter: {0} [m]\n".format(np.round(tube_D, 3)))
                myfile.write("Primary phase tube length: {0} [m]\n".format(np.round(tube_len, 2)))
                myfile.write("Coolant flow inside tubes - primary phase: {0} \n".format(self.flow_type))
                myfile.write("Secondary phase hydraulic diameter: {0} [m]\n".format(np.round(outer_Dh, 2)))
                myfile.write("HEX outer dimensions a x b: {0} x {1} [m]\n".format(np.round(a, 2), np.round(b, 2)))
            myfile.close()

            print("----------------------------------------------------------------------------------------------- \n")
            print("File {0} exported to path : {1} \n".format('HEX_SIZING_REPORT.dat', os.getcwd()))
            print("----------------------------------------------------------------------------------------------- \n\n")

        return A

    def convection_coefficient_primary(self, primary_phase, Dh = 0.1, d_L = None, Prw = None):

        '''
        ------------------------------------------------------------------
        Convection coefficient calculation for the heat exchanger primary phase

        INPUTS:
        primary phase   : [object]  [required]          primary flow medium
        Dh              : [m]       [required]          hydraulic diameter of coolant tubes
        d_L             : [-]       [optional]          tube diameter to length ratio 
        Prw             : [-]       [optional]          Bulck Prandtl number

        OUTPUTS:
        h       : [W/m2K]                       convection coefficient


        primary phase object includes list primary_phase.flow_properties which contains:
            0.  coolant mass flow       [kg/s]
            1.  specific heat           [J/kgK]
            2.  Outlet temperature      [K]
            3.  Inlet temperature       [K]
        ------------------------------------------------------------------
        '''

        m_flow, cp, Tout, Tin = primary_phase.flow_conditions

        primary_phase.coolant_medium.prandtl_number(0.5*(Tout + Tin))
        primary_phase.coolant_medium.dynamic_viscocity(0.5*(Tout + Tin))
        primary_phase.coolant_medium.thermal_conductivity(0.5*(Tout + Tin))

        pr = primary_phase.coolant_medium.Pr
        mi = primary_phase.coolant_medium.mi
        k = primary_phase.coolant_medium.k

        flag = False

        if d_L == None:
            d_L = 0
        if Prw == None:
            Prw = pr

        Re = 4*m_flow/(np.pi*Dh*mi)

        if Re > 1e4:
            xi = (1.82*np.log10(Re) - 1.64)**-2
            Nu = xi/8*(Re - 1000)*pr/(1 + 12.7*np.sqrt(xi/8)*(pr**(2/3) - 1))*(1 + (d_L)**(2/3))*(Prw/pr)**0.11
            flag = True
        else:
            Nu = 3.66

        h = Nu*k/Dh

        return h, flag

    def convection_coefficient_secondary(self, secondary_phase, Dh):
        
        '''
        ------------------------------------------------------------------
        Convection coefficient calculation for the heat exchanger secondary phase

        INPUTS:
        secondary phase     : [object]  [required]          secondary flow medium
        Dh                  : [m]       [required]          hydraulic diameter of coolant tubes
        d_L                 : [-]       [optional]          tube diameter to length ratio 
        Prw                 : [-]       [optional]          Bulck Prandtl number

        OUTPUTS:
        h       : [W/m2K]                       convection coefficient

        secondary phase object includes list secondary_phase.flow_properties which contains:
            0.  coolant mass flow       [kg/s]
            1.  specific heat           [J/kgK]
            2.  Outlet temperature      [K]
            3.  Inlet temperature       [K]
        ------------------------------------------------------------------
        '''

        m_flow, cp, Tout, Tin = secondary_phase.flow_conditions

        secondary_phase.coolant_medium.prandtl_number(0.5*(Tout + Tin))
        secondary_phase.coolant_medium.dynamic_viscocity(0.5*(Tout + Tin))
        secondary_phase.coolant_medium.thermal_conductivity(0.5*(Tout + Tin))

        pr = secondary_phase.coolant_medium.Pr
        mi = secondary_phase.coolant_medium.mi
        k = secondary_phase.coolant_medium.k

        Re = 4*m_flow/(np.pi*Dh*mi)
        
        if Re < 1e5:
            Nu = 0.664*Re**0.5*pr**(1/3)
        else:
            Nu = 0.037*Re**0.8*pr**(1/3)

        h = Nu*k/Dh

        return h

    def epsilon(self, NTU):

        '''
        ------------------------------------------------------------------
        Calculate epsilon as function of NTU
        ------------------------------------------------------------------
        '''

        Crel = self.Crel
        return 1 - np.exp((np.exp(-Crel*NTU**0.78) - 1)/(Crel*NTU**-0.22))

    def solve_NTU(self, NTU):

        '''
        ------------------------------------------------------------------
        Form equation : eps - eps(NTU) = 0
        This equation is to be solved iteratively  
        ------------------------------------------------------------------
        '''
        
        return self.eps - self.epsilon(NTU)

    def hx_box_compactness(self, Dh):

        '''
        ------------------------------------------------------------------
        Calculate box dimensions a x b to form the requested hydraulic diameter

        INPUTS:
        Dh : [required]         Hydraulic diameter

        OUTPUTS:
        a : base dimension
        b : height dimension
        ------------------------------------------------------------------
        '''

        b = np.linspace(Dh/2*1.01, 2*Dh, num = 100, endpoint = True)
        a = Dh*b/(2*b - Dh)
        A = a*b

        minA = A[0]
        minApos = 0
        for i in range(1, len(A)):
            if A[i] < minA:
                minApos = i
                minA = A[i]
        
        a_opt = a[minApos]
        b_opt = b[minApos]

        return a_opt, b_opt
