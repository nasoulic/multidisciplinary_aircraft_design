import numpy as np
from scipy.optimize import fsolve
from acsizing.area_surrogate_model import *
from acsizing.Aerodynamics import Aerodynamics
from XFOIL.readPolar import airfoil_polar
from XFOIL.runXFOIL import callXFOILWrapper
from acsizing.standard_atmosphere import Standard_Atmosphere as SA

class Stability_and_Trim():

    def __init__(self, aircraft, home_dir, output_dir):

        '''
        -------------------------------------------------------------------------------
        Initialize class variables

        INPUTS
        aircraft: aircraft object from acsizing module


        -------------------------------------------------------------------------------
        '''
        self.aircraft = aircraft
        self.Split_Input_File()
        self.M = aircraft.mission_inputs[8]
        self.Alt = aircraft.mission_inputs[4]
        self.home_dir = home_dir
        self.output_dir = output_dir
        self.Build_required_dictionaries()

    def overwrite_vsp_input_file(self):

        with open("./vsp_aircraft_input_file.dat", "w+") as f:
            for key, item in self.aircraft.GEOMETRY.items():
                f.write("Name={0}\n".format(key))
                for inkey, initem in item.items():
                    f.write("{1}={0}\n".format(initem, inkey))
                f.write("Fuselage Length={0}\n".format(self.aircraft.GEOMETRY["Fuselage"]["Length"]))
                f.write("#########################################\n")
        f.close()

    def Split_Input_File(self):

        '''
        -------------------------------------------------------------------------------
        Split input file dictionary
        -------------------------------------------------------------------------------
        '''

        master_dict = self.aircraft.GEOMETRY
        self.Fuselage = master_dict['Fuselage']
        self.Main_Wing = master_dict['Main_Wing']
        self.Vertical_Tail = master_dict['Vertical_Tail']
        self.Horizontal_Tail = master_dict['Horizontal_Tail']
        self.engine = master_dict['PT6A - 67D R']

    def Build_required_dictionaries(self):

        '''
        -------------------------------------------------------------------------------
        Calculate required quantities for the stability calculation
        -------------------------------------------------------------------------------
        '''

        Swet = { 'Main_Wing' : make_cokriging_main_wing_wetted(self.Main_Wing['Sref']),
                 'Horizontal_Tail' : make_cokriging_horizontal_tail_wetted(self.Horizontal_Tail['Sref']),
                }
        
        aerodynamics = Aerodynamics()
        Sexp_w = aerodynamics.Wet2Exp(self.Main_Wing['Thickness'], Swet['Main_Wing'])
        Sexp_ht = aerodynamics.Wet2Exp(self.Horizontal_Tail['Thickness'], Swet['Horizontal_Tail'])
        self.CLa_w = aerodynamics.Lift_Curve_Slope(self.M, self.Fuselage['Max Diameter'], self.Main_Wing['Span'], Sexp_w, self.Main_Wing['Sref'], self.Main_Wing['AR'], self.Main_Wing['Sweep_C4'], self.Main_Wing['Sweep'])
        self.CLa_ht = aerodynamics.Lift_Curve_Slope(self.M, self.Fuselage['Max Diameter'], self.Horizontal_Tail['Span'], Sexp_ht, self.Horizontal_Tail['Sref'], self.Horizontal_Tail['AR'], self.Horizontal_Tail['Sweep_C4'], self.Horizontal_Tail['Sweep'])
        self.Cmafus = self.Fuselage_Momment_Coefficient_grad()
        # Aerodynamic center main wing
        MW_position = self.Main_Wing['Relative Position X']*self.Fuselage['Length'] # Absolute position on assembly
        self.x_bar_acw = (MW_position + np.tan(np.radians(self.Main_Wing['Sweep']))*self.Main_Wing['Ybar'] + 0.25*self.Main_Wing['Cmean'])/self.Main_Wing['Cmean']
        # Aerodynamic center horizontal tail
        HT_position = MW_position + 0.25*(self.Main_Wing['Cmean'] - self.Horizontal_Tail['Cmean']) + self.Horizontal_Tail['Tailarm'] + self.Main_Wing['Ybar']*np.tan(np.radians(self. Main_Wing['Sweep'])) - self.Horizontal_Tail['Ybar']*np.tan(np.radians(self. Horizontal_Tail['Sweep']))
        self.x_bar_acht = (HT_position + self.Horizontal_Tail['Ybar']*np.tan(np.radians(self. Horizontal_Tail['Sweep'])) + 0.25*self.Horizontal_Tail['Cmean'])/self.Main_Wing['Cmean']
        self.nh = 0.9 # Dynamic Pressure Ratio for zero thrust pg 606
        self.dah_da = 0.8 # worst case from fig. 16.12
        self.i_w = np.radians(self.Main_Wing['Incidence'])
        self.i_ht = np.radians(self.Horizontal_Tail['Incidence'])

    def get_cruise_CL(self):

        '''
        -------------------------------------------------------------------------------
        Get CL @ cruise condition
        -------------------------------------------------------------------------------
        '''

        mtow = self.aircraft.mass_matrix["Aircraft"]["MTOM"]
        Sw = self.Main_Wing['Sref']
        atm_props = SA('Metric', self.Alt)
        Vinf = self.M*atm_props[3]
        rho = atm_props[1]
        q_inf = 0.5*rho*Vinf**2
        CL = mtow*9.81/(q_inf*Sw)

        return CL
        
    def Fuselage_Momment_param(self, x_bar_root_c4):

        '''
        -------------------------------------------------------------------------------
        Parameter from Raymer's approach Fig. 16.14

        INPUTS
        X_rc4   :   Absolute position of main wing's root C/4 divided by Cmean

        OUTPUTS
        kfus    :   fuselage parameter
        -------------------------------------------------------------------------------
        '''

        # x and y coordinates of curve
        x = [10, 20, 30, 42, 50, 55, 61]
        y = [0.005, 0.007, 0.01, 0.02, 0.03, 0.04, 0.05]

        Kfus = np.interp(x_bar_root_c4, x, y)

        return Kfus

    def Fuselage_Momment_Coefficient_grad(self):

        '''
        -------------------------------------------------------------------------------
        Fuselage momment coefficient gradient
        -------------------------------------------------------------------------------
        '''
        
        x_bar_r_c4 = (self.Main_Wing['Relative Position X'] + 0.25*self.Main_Wing['Croot']/self.Fuselage['Length'])*100 # percentage-wise position of c/4 of root chord on fuselage
        Kfus = self.Fuselage_Momment_param(x_bar_r_c4)
        Cmafus = Kfus*self.Fuselage['Max Diameter']**2*self.Fuselage['Length']/self.Main_Wing['Cmean']/self.Main_Wing['Sref']*180/np.pi # per rad

        return Cmafus

    def Wing_Momment_Coefficient(self):

        '''
        -------------------------------------------------------------------------------
        Wing momment coefficient
        -------------------------------------------------------------------------------
        '''

        atm_props = SA('Metric', self.Alt)
        rho = atm_props[1]
        miu = atm_props[4]
        cmean = self.Main_Wing['Cmean']
        Vinf = self.M*atm_props[3]
        wing_profile = self.Main_Wing['Profile']
        Re = Vinf*cmean*rho/miu
        callXFOILWrapper(wing_profile.replace("NACA", ""), Re, self.home_dir, self.output_dir)
        Cm0_airfoil = airfoil_polar(wing_profile.replace("NACA", ""), Re).zero_angle_moment_coefficient()
        Cmw = Cm0_airfoil*(self.Main_Wing['AR']*np.cos(np.radians(self.Main_Wing['Sweep']))**2)/(self.Main_Wing['AR'] + 2*np.cos(np.radians(self.Main_Wing['Sweep']))) + (-0.01)*self.Main_Wing['Twist']

        return Cmw

    def blade_der(self, case, J):

        '''
        -------------------------------------------------------------------------------
        Blade derivative

        INPUTS
        case    :   'Narrow Blade' or 'Wide Blade'
        J       :   Advance ratio

        OUTPUTS
        blade derivative parameter
        -------------------------------------------------------------------------------
        '''
        
        advance_ratio = [0, 1, 2, 3, 4, 5] # advance ratio
        if case == 'Narrow Blade':
            deriv = [0, 0.04, 0.07, 0.082, 0.09, 0.0995]
        elif case == 'Wide Blade':
            deriv = [0, 0.07, 0.095, 0.114, 0.13, 0.1375]
        else:
            raise ValueError("Case not found. Accepted cases are: 1. 'Narrow Blade', 2. 'Wide Blade'")

        der = np.interp(J, advance_ratio, deriv)

        return der

    def f_T(self, par):

        '''
        -------------------------------------------------------------------------------
        Non zero thrust adjustment parameter
        -------------------------------------------------------------------------------
        '''

        x_axis = [-0.25, 0, 0.5, 1., 1.52, 2, 2.5]
        y_axis = [0.8, 1, 1.3, 1.55, 1.75, 1.875, 2.03]

        fT = np.interp(par, x_axis, y_axis)

        return fT

    def factor_K1(self, par):

        '''
        -------------------------------------------------------------------------------
        Propeller downwash K1 parameter (NACA WR L-25)
        -------------------------------------------------------------------------------
        '''

        x_axis = [0, 0.5, 1, 1.5, 2]
        y_axis = [0, 0.22, 0.35, 0.45, 0.51]

        K1 = np.interp(par, x_axis, y_axis)

        return K1

    def factor_K2(self, par):

        '''
        -------------------------------------------------------------------------------
        Propeller downwash K2 parameter (NACA WR L-25)
        -------------------------------------------------------------------------------
        '''

        x_axis = [-0.5, 0, 0.5, 1, 1.5, 2, 2.5]
        y_axis = [0.25, 0.25, 0.245, 0.226, 0.205, 0.195, 0.17]

        K2 = np.interp(par, x_axis, y_axis)

        return K2

    def Lift_Increment(self, par, part):

        '''
        -------------------------------------------------------------------------------
        Lift increment with flap deflection

        INPUTS
        par     :       flap to airfoil chord ratio [-]
        part    :       dictionary of part

        OUTPUTS
        lift increment
        -------------------------------------------------------------------------------
        '''

        x_axis = [ 0.05, 0.1, 0.2, 0.3, 0.4, 0.5 ]
        y_axis_0 = [ 1.5, 2.5, 3.5, 4.2, 4.75, 5.1]
        y_axis_015 = [ 1.5, 2.5, 3.75, 4.6, 5.35, 6]

        ylower = np.interp(par, x_axis, y_axis_0)
        yupper = np.interp(par, x_axis, y_axis_015)

        y = ylower + (yupper - ylower)*part['Thickness']/0.15

        return y

    def kf_factor(self, ang, cf_c):

        '''
        -------------------------------------------------------------------------------
        Empirical correction for plain flap lift increment

        INPUTS:
        ang     :   angle [deg]
        cf_c    :   flap2wing chord ratio [-]

        OUTPUTS
        Plain flap lift increment correction factor
        -------------------------------------------------------------------------------
        '''

        angle = np.array([ 0, 10, 20, 30, 40, 50, 60])
        kf_01 = np.array([ 1, 1, 0.9, 0.72, 0.65, 0.6, 0.58])
        kf_05 = np.array([ 1, 1, 0.7, 0.55, 0.5, 0.45, 0.42])

        res01 = np.interp( ang, angle, kf_01)

        res05 = np.interp( ang, angle, kf_05)


        kf = res01 + (cf_c - 0.1)/(0.5 - 0.1)*(res05 - res01)

        return kf

    def Neutral_Point(self, q = None, par = None, J = None, case = None):

        '''
        -------------------------------------------------------------------------------
        This function calculates the neutral point of the aircraft
        Available cases are: 1.     'Zero Thrust' case"
                             2. non 'Zero Thrust' case "
        For the non zero thrust case args required are : " 
                                                     q : Dynamic Head    "
                                                   par : T/(rho*V^2*D^2) "
                                                     J : Advance Ratio  
        -------------------------------------------------------------------------------
        '''

        if case == None:
            case = 'Zero Thrust' # Default case is the zero thrust case
        
        if case == 'Zero Thrust':
            X_bar_np = (self.CLa_w*self.x_bar_acw - self.Cmafus + self.nh*self.Horizontal_Tail['Sref']/self.Main_Wing['Sref']*self.CLa_ht*self.dah_da*self.x_bar_acht)/(self.CLa_w + self.nh*self.Horizontal_Tail['Sref']/self.Main_Wing['Sref']*self.CLa_ht*self.dah_da)
        else:

            NB = self.engine['Number of Blades']
            Ap = np.pi*self.engine['Propeller Diameter']**2/4
            der = self.blade_der('Narrow Blade', J) # From Figure 16.15 Raymer
            fpar = self.f_T(par) # From Figure 16.16 Raymer
            K1 = self.factor_K1(par) # From Figure 16.17 Raymer
            K2 = self.factor_K2(par) # From Figure 16.17 Raymer
            Fpa = q*NB*Ap*der*fpar # Eq. 16.29 Raymer
            dap_da = 1 - (K1 + K2*NB*der)/(1 + K2*NB*der)
            thrust_par = Fpa/(q*self.Main_Wing['Sref'])*dap_da

            X_bar_p = self.engine['Relative Position X Eng']*self.Fuselage['Length']/self.Main_Wing['Cmean'] # propulsion relative position

            X_bar_np = (self.CLa_w*self.x_bar_acw - self.Cmafus + self.nh*self.Horizontal_Tail['Sref']/self.Main_Wing['Sref']*self.CLa_ht*self.dah_da*self.x_bar_acht + thrust_par*X_bar_p)/(self.CLa_w + self.nh*self.Horizontal_Tail['Sref']/self.Main_Wing['Sref']*self.CLa_ht*self.dah_da + thrust_par)

        return X_bar_np

    def Static_Margin(self, X_aft_cg):

        '''
        -------------------------------------------------------------------------------
        Calculate aircraft static margin

        INPUTS
        X_aft_cg    :       Absolute position of X cg [m]

        OUTPUTS
        SM          :       Static Margin
        -------------------------------------------------------------------------------
        '''

        x_bar_np = self.Neutral_Point()
        SM = x_bar_np - X_aft_cg/self.Main_Wing['Cmean']

        return SM

    def Moment_Coefficient(self, Xcg, alpha, de, df, i_w = np.radians(1), i_ht = np.radians(-2)):

        '''
        -------------------------------------------------------------------------------
        Aircraft moment coefficient

        INPUTS:
        Xcg     :   Aircraft center of gravity divided by Cmean [-]
        alpha   :   angle of attack [rad]
        de      :   elevator deflection [rad]
        df      :   wing flap deflection [rad]
        i_w     :   wing incidence angle [rad]
        i_ht    :   horizontal tail incidence angle [rad]

        OUTPUTS
        CL_tot  :   Total lift coefficient
        Cm_cg   :   Moment coefficient
        -------------------------------------------------------------------------------
        '''
        
        # alpha = np.radians(alpha)
        # de = np.radians(de)
        # df = np.radians(df)
        # i_w = np.radians(i_w)
        # i_ht = np.radians(i_ht)

        X_cg = Xcg/self.Main_Wing['Cmean'] # Calulate the X_bar value of X most fwd CoG position X_bar = X_fwd/c_mean

        X_acw = self.x_bar_acw
        X_ach = self.x_bar_acht
        dlift = 0.44 # Fig. 16.9 slotted flaps
        X_cp = self.x_bar_acw + dlift
        Sw = self.Main_Wing["Sref"]
        Sh = self.Horizontal_Tail['Sref']
        Ce_C = self.Horizontal_Tail['ChordRatio'][0]
        Cf_C = max(self.Main_Wing['ChordRatio']) # Aileron Chord to Wing Chord Ratio
        eta_h = self.nh

        atm_props = SA('Metric', self.Alt)
        wing_profile = self.Main_Wing['Profile']
        tail_profile = self.Horizontal_Tail['Profile']
        Vinf = self.M*atm_props[3]
        cmean_w = self.Main_Wing['Cmean']
        cmean_h = self.Horizontal_Tail['Cmean']
        rho = atm_props[1]
        miu = atm_props[4]
        ReH = Vinf*cmean_h*rho/miu
        ReW = Vinf*cmean_w*rho/miu

        CLaw = self.CLa_w
        CLaht = self.CLa_ht
        dah_da = self.dah_da

        # Find Control Surface Area of Main Wing
        Surf = 0
        for i in range(int(self.Main_Wing["Moving Parts"])):
            Surf = Surf + self.Main_Wing["ChordRatio"][i]*self.Main_Wing["SpanRatio"][i]
        Scsw = Surf

        # Find Control Surface Area of Horizontal Tail
        Surf = 0
        for i in range(int(self.Horizontal_Tail['Moving Parts'])):
            Surf = Surf + self.Horizontal_Tail['ChordRatio'][i]*self.Horizontal_Tail['SpanRatio'][i]
        Se_Sht = Surf
        
        Ke = self.kf_factor(np.degrees(de), Ce_C)
        dCl_dde_af = self.Lift_Increment(Ce_C, self.Horizontal_Tail)
        Sweep_ht = np.radians(self.Horizontal_Tail['Sweep_C4'])

        dCL_dde = 0.9*Ke*dCl_dde_af*Se_Sht*np.cos(Sweep_ht)
        Delta_a0Lht = -1/CLaht*dCL_dde*de

        a0Lw = airfoil_polar(wing_profile.replace("NACA", ""), ReW).zero_lift_angle()
        a0Lw = np.radians(a0Lw)
        callXFOILWrapper(tail_profile.replace("NACA", ""), ReH, self.home_dir, self.output_dir)
        a0Lh = airfoil_polar(tail_profile.replace("NACA", ""), ReH).zero_lift_angle()
        a0Lh = np.radians(a0Lh)

        # CLw = CLaw*(aoa + i_w - a0Lw)
        Kf = self.kf_factor(np.degrees(df), Cf_C)
        dCl_ddf_af = self.Lift_Increment(Cf_C, self.Main_Wing)
        Sweep_w = np.radians(1)
        dCL_ddf = 0.9*Kf*dCl_ddf_af*Scsw*np.cos(Sweep_w)
        Delta_a0Lw = -1/CLaw*dCL_ddf*df
        CLw = CLaw*(alpha - Delta_a0Lw)

        # CLh = CLaht*((aoa + i_w)*dah_da + (i_ht - i_w) - a0Lh)
        CLh = CLaht*(alpha*dah_da + (i_ht - i_w) - Delta_a0Lht)

        Cmw = self.Wing_Momment_Coefficient()

        Cmwdf = -dCL_ddf*(X_cp - X_cg)

        Cmfus = self.Fuselage_Momment_Coefficient_grad()

        Cm_cg = CLw*(X_cg - X_acw) + Cmw + Cmwdf*df + Cmfus*alpha - eta_h*Sh/Sw*CLh*(X_ach - X_cg)
        CL_tot = CLaw*alpha + eta_h*Sh/Sw*CLh

        return CL_tot, Cm_cg

    def trim_aircraft(self, Xcg, aircraft_angle, df, CL_tot, Cm_cg):

        '''
        -------------------------------------------------------------------------------
        Aircraft trim analysis

        INPUTS:
        Xcg                 :   aircraft center of gravity divided by Cmean [-]
        aircraft_angle      :   aircraft angle [rad]
        df                  :   wing flap deflection [rad]
        CL_tot              :   total lift coefficient [-]
        Cm_cg               :   moment coefficient [-]

        OUTPUTS
        flag  :   horizontal tail incidence solver flag
        -------------------------------------------------------------------------------
        '''

        self.i_w = self.find_w_incidence(Xcg, aircraft_angle, df, CL_tot, Cm_cg)
        self.i_ht, flag = self.find_ht_incidence()
        
        self.Xcg = Xcg
        self.df = df
        self.CL_tot = CL_tot
        self.Cm_cg = Cm_cg

        alpha, de = fsolve(self.solve_trim_equations, (0.1, 0.1))

        with open("trim_analysis.dat", 'w') as myfile:
            myfile.write('angle of attack, %f \n' %np.degrees(alpha))
            myfile.write('elevator deflection, %f \n' %np.degrees(de))
            myfile.write('for wing incidence, %f \n' %np.degrees(self.i_w))
            myfile.write('for horizontal tail incidence, %f \n' %np.degrees(self.i_ht))
        myfile.close()

        return flag

    def find_w_incidence(self, Xcg, aircraft_angle, df, CL_tot, Cm_cg, i_w = np.radians(1), i_ht = np.radians(-2)):

        '''
        -------------------------------------------------------------------------------
        Find main wing incidence

        INPUTS:
        Xcg                 :   aircraft center of gravity divided by Cmean [-]
        aircraft_angle      :   aircraft angle [rad]
        df                  :   wing flap deflection [rad]
        CL_tot              :   total lift coefficient [-]
        Cm_cg               :   moment coefficient [-]
        i_w                 :   wing incidence angle [rad]
        i_ht                :   horizontal tail incidence angle [rad]

        OUTPUTS
        req_i_w  :   required wing incidence
        -------------------------------------------------------------------------------
        '''

        self.Xcg = Xcg
        self.df = df
        self.CL_tot = CL_tot
        self.Cm_cg = Cm_cg
        self.i_w = i_w
        self.i_ht = i_ht

        
        atm_props = SA('Metric', self.Alt)
        wing_profile = self.Main_Wing['Profile']
        Vinf = self.M*atm_props[3]
        cmean_w = self.Main_Wing['Cmean']
        rho = atm_props[1]
        miu = atm_props[4]
        ReW = Vinf*cmean_w*rho/miu
        callXFOILWrapper(wing_profile.replace("NACA", ""), ReW, self.home_dir, self.output_dir)
        a0Lw = airfoil_polar(wing_profile.replace("NACA", ""), ReW).zero_lift_angle()

        alpha, de = fsolve(self.solve_trim_equations, (0.1, 0.1))

        req_i_w = np.degrees(alpha) - np.degrees(aircraft_angle) + a0Lw

        self.aircraft.GEOMETRY["Main_Wing"]["Incidence"] = req_i_w

        self.overwrite_vsp_input_file()

        return np.radians(req_i_w)

    def get_de(self, iht):

        '''
        -------------------------------------------------------------------------------
        Change tail incidence to alter elevator deflection
        -------------------------------------------------------------------------------
        '''

        self.i_ht = iht
        a, de = fsolve(self.solve_trim_equations, (0.1, 0.1))
        
        return abs(de)

    def find_ht_incidence(self):

        '''
        -------------------------------------------------------------------------------
        Find horizontal tail incidence for new main wing incidence
        -------------------------------------------------------------------------------
        '''

        x0 = np.radians(-1.)

        step = 0
        e = 1e-4
        flag = True
        converged = False
        deriv = 1e6
        h = 1e-4

        while not converged:
            if deriv == 0.0:
                print('Divide by zero error! Breaking code...')
                flag = False
                break
            
            deriv = (self.get_de(x0 + h) - self.get_de(x0))/h
            x1 = x0 - self.get_de(x0)/deriv
            de_old = self.get_de(x0)
            de_new = self.get_de(x1)

            x0 = x1
            step += 1

            if step > 1e3:
                flag = False
                print('Max iteration number reached. Exiting...')
                break

            converged = abs(de_old - de_new) < e

        if flag:
            # print('Root is : %f ' %np.degrees(x1))
            pass
        else:
            print('No convergence.')
            x1 = 1e6

        self.aircraft.GEOMETRY["Horizontal_Tail"]["Incidence"] = np.degrees(x1)

        self.overwrite_vsp_input_file()

        return x1, flag

    def solve_trim_equations(self, x):

        '''
        -------------------------------------------------------------------------------
        Solve non-linear pair of trim analysis equations

        INPUTS:
        x     :   list, includes angle of attack and elevator deflection
        

        OUTPUTS
        2x2 system of equations
        -------------------------------------------------------------------------------
        '''

        i_w = self.i_w
        i_ht = self.i_ht
        Xcg = self.Xcg
        df = self.df
        CL_tot = self.CL_tot
        Cm_cg = self.Cm_cg


        alpha, de = x

        X_cg = Xcg/self.Main_Wing['Cmean'] # Calulate the X_bar value of X most fwd CoG position X_bar = X_fwd/c_mean

        X_acw = self.x_bar_acw
        X_ach = self.x_bar_acht
        dlift = 0.44 # Fig. 16.9 slotted flaps
        X_cp = self.x_bar_acw + dlift

        # Find Control Surface Area of Main Wing
        Surf = 0
        for i in range(int(self.Main_Wing["Moving Parts"])):
            Surf = Surf + self.Main_Wing["ChordRatio"][i]*self.Main_Wing["SpanRatio"][i]
        Scsw = Surf

        # Find Control Surface Area of Horizontal Tail
        Surf = 0
        for i in range(int(self.Horizontal_Tail['Moving Parts'])):
            Surf = Surf + self.Horizontal_Tail['ChordRatio'][i]*self.Horizontal_Tail['SpanRatio'][i]
        Se_Sht = Surf

        Ce_C = self.Horizontal_Tail['ChordRatio'][0]
        Cf_C = max(self.Main_Wing['ChordRatio'])
        eta_h = self.nh
        Sw = self.Main_Wing["Sref"]
        Sh = self.Horizontal_Tail['Sref']
        CLaw = self.CLa_w
        CLaht = self.CLa_ht
        dah_da = self.dah_da
        Ke = self.kf_factor(np.degrees(de), Ce_C)
        dCl_dde_af = self.Lift_Increment(Ce_C, self.Horizontal_Tail)
        Sweep_ht = np.radians(self.Horizontal_Tail['Sweep_C4'])
        dCL_dde = 0.9*Ke*dCl_dde_af*Se_Sht*np.cos(Sweep_ht)
        Kf = self.kf_factor(np.degrees(df), Cf_C)
        dCl_ddf_af = self.Lift_Increment(Cf_C, self.Main_Wing)
        Sweep_w = np.radians(1)
        dCL_ddf = 0.9*Kf*dCl_ddf_af*Scsw*np.cos(Sweep_w)
        Delta_a0Lw = -1/CLaw*dCL_ddf*df
        CLw = CLaw*(alpha - Delta_a0Lw)

        Delta_a0Lht = -1/CLaht*dCL_dde*de

        CLh = CLaht*(alpha*dah_da + (i_ht - i_w) - Delta_a0Lht)

        Cmw = self.Wing_Momment_Coefficient()

        Cmwdf = -dCL_ddf*(X_cp - X_cg)

        Cmfus = self.Fuselage_Momment_Coefficient_grad()

        eq1 = CL_tot - CLaw*alpha - eta_h*Sh/Sw*CLh
        eq2 = Cm_cg - CLw*(X_cg - X_acw) - Cmw - Cmwdf*df - Cmfus*alpha + eta_h*Sh/Sw*CLh*(X_ach - X_cg)

        return (eq1, eq2)

    def make_trim_plot(self, X_cg, df = 0, i_w = np.radians(1), i_ht = np.radians(-2)):

        '''
        -------------------------------------------------------------------------------
        Make and save trim plot

        INPUTS:
        X_cg     :   Aircaft CoG divided by Cmean
        df       :   flap deflection [rad]
        i_w      :   main wing incidence angle [rad]
        i_ht     :   horizontal tail incidence angle [rad]
        
        -------------------------------------------------------------------------------
        '''
        
        CL_tot = []
        CM = []

        angle = np.arange(np.radians(0), np.radians(11), np.radians(2))
        elevator = np.arange(np.radians(-6), np.radians(7), np.radians(2))

        for aoa in angle:
            for de in elevator:
                CL, Cm = self.Moment_Coefficient(X_cg, alpha = aoa, de = de, df = df, i_w = i_w, i_ht = i_ht)
                CL_tot.append(CL)
                CM.append(Cm)

        CL_tot = np.array(CL_tot)
        CM = np.array(CM)

        CM = CM.reshape(len(angle), len(elevator))
        CL_tot = CL_tot.reshape(len(angle), len(elevator))

        import matplotlib.pyplot as plt
        from matplotlib.font_manager import FontProperties

        fontP = FontProperties()
        fontP.set_size("small")

        plt.figure()
        for k in range(len(elevator)):
            plt.scatter(CL_tot[:, k], CM[:, k], label = "\u03B4\u03B5 " + str(np.round((np.degrees(elevator[k])), 1)) + ' [deg]')
            plt.plot(CL_tot[:, k], CM[:, k], linewidth = 1, linestyle = '--')
        
        CL_cruise = self.get_cruise_CL()
        plt.scatter( CL_cruise, 0 , marker = "x", label = "cruise")
        plt.plot([CL_tot.min(), CL_tot.max()], [0, 0], '--', color = 'k')
        plt.legend(loc = "best", prop=fontP)
        plt.xlabel("Total Lift Coefficient [-]", weight = "bold")
        plt.ylabel("Momment Coefficient Cmcg [-]", weight = "bold")
        plt.tight_layout()
        plt.grid()
        plt.savefig('Trim_Plot.png', dpi = 300)
        plt.legend()
        plt.close()
        # plt.show()


    def Trim_Analysis(self, fwd_cg_X, show_plot = False):

        '''
        -------------------------------------------------------------------------------
        Aircraft trim analysis
        -------------------------------------------------------------------------------
        '''

        fwd_cg = fwd_cg_X/self.Main_Wing['Cmean'] # Calulate the X_bar value of X most fwd CoG position X_bar = X_fwd/c_mean

        Cf_C = max(self.Main_Wing['ChordRatio']) # Aileron Chord to Wing Chord Ratio
        ba_b = sum(self.Main_Wing['SpanRatio']) # Aileron Span to Wing Span ratio
        
        dCl_ddf = self.Lift_Increment(Cf_C, self.Main_Wing) # [per rad] slope from fig. 16.6
        Sweep_HLw = np.radians(0.9) # [deg] From CAD

        # Find Control Surface Area of Main Wing
        Surf = 0
        for i in range(int(self.Main_Wing["Moving Parts"])):
            Surf = Surf + self.Main_Wing["ChordRatio"][i]*self.Main_Wing["SpanRatio"][i]
        Scsw = Surf*self.Main_Wing["Sref"]

        # Find Control Surface Area of Horizontal Tail
        Surf = 0
        for i in range(int(self.Horizontal_Tail['Moving Parts'])):
            Surf = Surf + self.Horizontal_Tail['ChordRatio'][i]*self.Horizontal_Tail['SpanRatio'][i]
        Se_Sht = Surf

        incidence_w = np.radians(self.Main_Wing['Incidence'])
        incidence_ht = np.radians(self.Horizontal_Tail['Incidence'])

        dlift = 0.44 # Fig. 16.9 slotted flaps
        x_bar_cp = self.x_bar_acw + dlift

        atm_props = SA('Metric', self.Alt)
        rho = atm_props[1]
        miu = atm_props[4]
        cmean_w = self.Main_Wing['Cmean']
        cmean_ht = self.Horizontal_Tail['Cmean']
        Vinf = self.M*atm_props[3]
        wing_profile = self.Main_Wing['Profile']
        ht_profile = self.Horizontal_Tail['Profile']
        ReW = Vinf*cmean_w*rho/miu
        Reht = Vinf*cmean_ht*rho/miu

        a0w = airfoil_polar(wing_profile.replace("NACA", ""), ReW).zero_lift_angle()
        a0ht = airfoil_polar(ht_profile.replace("NACA", ""), Reht).zero_lift_angle()

        a0lw = np.radians(a0w) # from appendix D NACA 4415. To be changed with XFOIL
        a0Lht=np.radians(a0ht) # from Appendix D NACA 0012

        Cmw = self.Wing_Momment_Coefficient()

        Ce_C = self.Horizontal_Tail['ChordRatio'][0]
        be_b = self.Horizontal_Tail['SpanRatio'][0]
        dCl_dde = self.Lift_Increment(Ce_C, self.Horizontal_Tail) # [per rad] slope from fig. 16.6
        Sweep_HLe = np.radians(self.Horizontal_Tail['Sweep_C4'])
        
        AOA = np.radians(np.arange(-5, 20, 5)) # Angle of Attack | Range -5 to 20
        DE = np.radians(np.arange(-5, 10, 5)) # Elevator deflection Range -5 to 10
        DF = np.radians(np.arange(0, 5, 5)) # Flap deflection 0 to 35
        CLtotal = np.zeros([np.size(AOA), np.size(DE), np.size(DF)], dtype = float)
        Cmcg = np.zeros([np.size(AOA), np.size(DE), np.size(DF)], dtype = float)
        i = 0
        for aoa in AOA:
            j = 0
            for de in DE:
                k = 0
                for df in DF:
                    Kf = self.kf_factor(np.degrees(df), Cf_C)
                    dCL_ddf = 0.9*Kf*dCl_ddf*Scsw/self.Main_Wing['Sref']*np.cos(Sweep_HLw) # per rad
                    Da0Lw = -1/self.CLa_w*dCL_ddf*df
                    Cmwdf = -dCL_ddf*(x_bar_cp - fwd_cg)
                    CL = self.CLa_w*(aoa + incidence_w - a0lw - Da0Lw)
                    Ke = self.kf_factor(np.degrees(de), Ce_C)
                    dCL_dde = 0.9*Ke*dCl_dde*Se_Sht*np.cos(Sweep_HLe)
                    Da0Lht = -1/self.CLa_ht*dCL_dde*de
                    CLh = self.CLa_ht*(self.dah_da*(aoa + incidence_w) + incidence_ht - incidence_w - a0Lht - Da0Lht)
                    CLtotal[i, j, k] = self.CLa_w*(aoa + incidence_w - a0lw) + self.nh*self.Horizontal_Tail['Sref']/self.Main_Wing['Sref']*CLh
                    Cmcg[i, j, k] = CL*(fwd_cg - self.x_bar_acw) + Cmw + Cmwdf*df + self.Cmafus*aoa - self.nh*self.Horizontal_Tail['Sref']/self.Main_Wing['Sref']*CLh*(self.x_bar_acht - fwd_cg)
                    k += 1
                j += 1
            i += 1

        if show_plot:

            import matplotlib.pyplot as plt
            from matplotlib.font_manager import FontProperties

            fontP = FontProperties()
            fontP.set_size("small")

            reps = np.size(DF)
            for k in range(0, reps):
                plt.figure()
                plt.rcParams['font.size'] = '13'
                plt.grid()
                title = "Trim Plot for wing flap deflection angle: " + str(int(round(np.degrees(DF[k])))) + " [deg]"
                plt.title(title, weight = "bold")
                times=np.arange(0, np.size(DE), 1)
                for t in times:
                    plt.scatter(CLtotal[:,t,k], Cmcg[:,t,k])
                    plt.plot(CLtotal[:,t,k], Cmcg[:,t,k], label = "\u03B4\u03B5 " + str(int(round(np.degrees(DE[t])))) + " [deg] ")

                CL_cruise = self.get_cruise_CL()    
                #CL_climb = W_S_climb*9.81/qclimb
                #CL_cruise = W_S_cruise*9.81/qcruise
                #CL_loiter = W_S_loiter*9.81/qloiter
                #plt.scatter( CL_climb, 0 , marker = "x", label = "climb")
                plt.scatter( CL_cruise, 0 , marker = "x", label = "cruise")
                #plt.scatter( CL_loiter, 0 , marker = "x", label = "loiter")
                plt.plot([CLtotal.min(), CLtotal.max()], [0,0], '--', color='k')
                plt.legend(loc = "best", prop=fontP)
                plt.xlabel("Total Lift Coefficient [-]", weight = "bold")
                plt.ylabel("Momment Coefficient Cmcg [-]", weight = "bold")
                plt.tight_layout()
                plt.savefig('Trim_Plot.png', dpi = 300)
                plt.close()
                # plt.show()
