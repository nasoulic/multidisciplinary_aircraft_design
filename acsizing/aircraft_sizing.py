from acsizing.standard_atmosphere import Standard_Atmosphere as SA
from acsizing.area_surrogate_model import *
from acsizing.Aerodynamics import Aerodynamics
from scipy.interpolate import interp1d
import numpy as np
import json

class aircraft_sizing(object):

    def __init__(self):
        
        self.mass_matrix = {}

    def design_evaluation(self, MTOW, eps_weight, tms_weight, wfuel, wbatteries, m_cab_dc, m_cab_ac, PAX, Crew, WPAX, settings):

        Wpayload = PAX*WPAX
        Wcrew = Crew*WPAX

        t_tail = False
        pressurized_cabin = False

        n = self.GENERAL_INFO["load_factor"]
        n_check = 2.1 + 24000/(MTOW*2.2046226218488 + 10000)
        if n < n_check:
            n = n_check
        if n > 3.8:
            n = 3.8

        if self.GENERAL_INFO["tail"] == 0:
            t_tail = True

        if self.mission_inputs[4] > 3048:
            pressurized_cabin = True

        wetted_S = {
            'Fuselage' : make_cokriging_fuselage_wetted(self.GEOMETRY['Fuselage']['Length']),
            'Main_Wing' : make_cokriging_main_wing_wetted(self.GEOMETRY['Main_Wing']['Sref']),
            'Horizontal_Tail' : make_cokriging_horizontal_tail_wetted(self.GEOMETRY['Horizontal_Tail']['Sref']),
            'Vertical_Tail' : make_cokriging_vertical_tail_wetted(self.GEOMETRY['Vertical_Tail']['Sref']),
            'PT6A - 67D R' : engine_wetted_area(),
            'Wing_Reinforcement' :  0, # Included in Fuselage
            'Landing_Gear' : 0, # Included in Fuselage
        }

        self.Volume = {
            'Fuselage' : make_cokriging_fuselage_volume(self.GEOMETRY['Fuselage']['Length']),
            'Main_Wing' : make_cokriging_wing_volume(self.GEOMETRY['Main_Wing']['Sref']),
        }

        landing_gear = self.Landing_Gear(MTOW) # Calculate landing gear parasite drag
        aircaft_parasite_drag = \
            Aerodynamics().Parasite_Drag(self.mission_inputs[8], self.GEOMETRY['Fuselage'], self.GEOMETRY['Main_Wing'],
            self.GEOMETRY['Horizontal_Tail'], self.GEOMETRY['Vertical_Tail'],
            self.GEOMETRY['PT6A - 67D L'], landing_gear, wetted_S)

        Nz = 1.5*n

        if not settings.constrain_OEM:        
            empty_weight = self.Empty_Weight_Estimation_Level_3_Transport(MTOW, Nz, t_tail, pressurized_cabin,
                                                                      self.advanced_materials, wetted_S, self.Volume)
        else:
            empty_weight = self.Empty_Weight_Estimation_Level_3_Transport(8618, Nz, t_tail, pressurized_cabin,
                                                                      self.advanced_materials, wetted_S, self.Volume)
        
        l_cables = self.Calbing_Length(settings.configuration)
        w_cables = l_cables['DC_Cables']*m_cab_dc + l_cables['AC_Cables']*m_cab_ac
        self.mass_matrix["EPS"]["DC Cables"] = l_cables['DC_Cables']*m_cab_dc
        self.mass_matrix["EPS"]["AC Cables"] = l_cables['AC_Cables']*m_cab_ac

        OEW = empty_weight['Main_Wing'] + empty_weight['Horizontal_Tail'] + empty_weight['Vertical_Tail'] +\
            empty_weight['Fuselage'] + empty_weight['Landing_Gear'] + empty_weight['Installed_Engines'] +\
                empty_weight['Else'] + eps_weight + w_cables + tms_weight

        MTOW = OEW + Wpayload + wbatteries + wfuel

        self.aircraft_mass_breakdown = {
            'MTOM' : MTOW,
            'Empty' : OEW,
            'Payload' : Wpayload,
            'Crew' : Wcrew,
            'Batteries' : wbatteries,
            'Fuel' : wfuel
        }

        for key, item in empty_weight.items():
            self.aircraft_mass_breakdown[key] = item

        return MTOW, self.GEOMETRY['Main_Wing']['Sref'], aircaft_parasite_drag

    def define_geometry(self, clmax, AR, Pmax, Pcruise, etap, w_gt, settings):

        if settings.configuration == 'Series':
            N_gt_L = 2
            N_gt_R = 2
        else:
            N_gt_L = 1
            N_gt_R = 1

        if settings.advanced_materials:
            self.advanced_materials = True
        else:
            self.advanced_materials = False       

        self.GEOMETRY = {'Main_Wing' : {
                                        'AR' : AR,
                                        'Taper' : 0.7,
                                        'Twist' : -3, 
                                        'Incidence' : 1., 
                                        'Dihedral' : 1., 
                                        'Sweep' : 5,
                                        'Thickness' : 0.15,
                                        'Profile' : 'NACA4415', 
                                        'Wetted2Reference_area_ratio' : 4.,
                                        'KLD' : 11.,
                                        'Moving Parts' : 2, 
                                        'ChordRatio' : [0.2, 0.15], 
                                        'SpanRatio' : [0.5, 0.3],
                                        'Relative Position X' : 0.38,
                                        'Relative Position Z' : 0.1,
                                        'Name' : 'Main_Wing'
                                        },

                         'Horizontal_Tail' : {
                                        'AR' : 4.,
                                        'Taper' : 0.9,
                                        'Twist' : 0., 
                                        'Incidence' : 0., 
                                        'Dihedral' : 0.,
                                        'Sweep' : 10.,
                                        'Thickness' : 0.15,
                                        'Profile' : 'NACA0012', 
                                        'Moving Parts' : 1, 
                                        'ChordRatio' : [0.25], 
                                        'SpanRatio' : [0.8],
                                        'Relative Position X' : 0.88,
                                        'Relative Position Z' : 0.169,
                                        'Name' : 'Horizontal_Tail',
                                        },

                         'Vertical_Tail' : {
                                        'AR' : 1.,
                                        'Taper' : 0.8,
                                        'Twist' : 0., 
                                        'Incidence' : -3., 
                                        'Dihedral' : 0., 
                                        'Sweep' : 45.,
                                        'Thickness' : 0.15,
                                        'Profile' : 'NACA0012', 
                                        'Moving Parts' : 1, 
                                        'ChordRatio' : [0.3], 
                                        'SpanRatio' : [0.8],
                                        'Relative Position X' : 0.75,
                                        'Relative Position Z' : 0.06,
                                        'Name' : 'Vertical_Tail'
                                        },

                         'Fuselage' :   {
                                        'Relative Position Z' : 0.25,
                                        'Relative Position X' : 0.,
                                        'Fuselage XSection' : 'Ellipse',
                                        'Name' : 'Fuselage',
                                        },

                        'Wing_Reinforcement' : {    
                                        'Pod Length' : 4.3,
                                        'Pod XS Type' : 'Rectangular',
                                        'Relative Position X' : 0.34,
                                        'Relative Position Z' : 0.0917,
                                        'Top Side Angles' : [45, 9, -9, -9, -45],
                                        'Right Side Angles' : [45, 0, 0, 0, -45],
                                        'Top Side Strengths' : [0.75, 1, 1, 1, 0.75],
                                        'XS_Width' : [0, 1.8, 1.8, 1.8, 0],
                                        'XS_Height' : [0, 0.75, 0.75, 0.34, 0],
                                        'Name' : 'Wing_Reinforcement', },

                         'Landing_Gear' : {
                                        'Relative Position X' : 0.33,
                                        'Relative Position Z' : -0.01812,
                                        'Pod Length' : 4.3,
                                        'Pod XS Type' : 'Ellipse',
                                        'Top Side Angles' : [90, 0, 0, 0, -90],
                                        'Right Side Angles' : [90, 20, 0, -25, -90],
                                        'Top Side Strengths' : [0.75, 1, 1, 1, 0.75],
                                        'XS_Width' : [0, 1.93182, 2.5, 2.15909, 0], 
                                        'XS_Height' : [0, 0.62233, 0.76818, 0.62233, 0],
                                        'Name' : 'Landing_Gear',
                                        },

                         'PT6A - 67D L' :   {
                                        'Weight' : w_gt,
                                        'No_GT' : N_gt_L,
                                        'Name' : 'PT6A - 67D L',
                                        'Engine Length' : 4,
                                        'Engine Diameter' : 2.73,
                                        'Relative Position X Eng' : 0.295,
                                        'Relative Position Y Eng' : -0.1914,
                                        'Relative Position Z Eng' : 0.093,
                                        'XS_Width' : [0, 0.84808, 0.84808, 0.73746, 0],
                                        'XS_Height' : [0, 1.0354, 1.26459, 1.0354, 0],
                                        'XS_Xpos_rel' : [0, 0.25, 0.5, 0.75, 1],
                                        'XS_Zpos_rel' : [0, -0.05, -0.08431, -0.1, -0.15],
                                        'Name1' : 'Propeller L',
                                        'Propeller Diameter' : 0.,
                                        'Number of Blades' : 4,
                                        'Relative Position X Prop' : 0.3316,
                                        'Relative Position Y Prop' : -0.1914,
                                        'Relative Position Z Prop' : 0.0845,
                                        'COG_GT' : [0.251, 0., 0.],
                                        },

                         'PT6A - 67D R' :   {
                                        'Weight' : w_gt,
                                        'No_GT' : N_gt_R,
                                        'Name' : 'PT6A - 67D R',
                                        'Engine Length' : 4.,
                                        'Engine Diameter' : 2.73,
                                        'Relative Position X Eng' : 0.295,
                                        'Relative Position Y Eng' : 0.1914,
                                        'Relative Position Z Eng' : 0.093,
                                        'XS_Width' : [0, 0.84808, 0.84808, 0.73746, 0],
                                        'XS_Height' : [0, 1.0354, 1.26459, 1.0354, 0],
                                        'XS_Xpos_rel' : [0, 0.25, 0.5, 0.75, 1],
                                        'XS_Zpos_rel' : [0, -0.05, -0.08431, -0.1, -0.15],
                                        'Name1' : 'Propeller R',
                                        'Propeller Diameter' : 0.,
                                        'Number of Blades' : 4,
                                        'Relative Position X Prop' : 0.3316,
                                        'Relative Position Y Prop' : 0.1914,
                                        'Relative Position Z Prop' : 0.0845,
                                        'COG_GT' : [0.251, 0., 0.],
                                        },

                        'Cockpit' : { 'Name' : 'Cockpit',
                                        'Name1' : 'Pilot',
                                        'Draw PAX' : 'False',
                                        'PAX' : 1,
                                        'Seat Pitch' : 0.77,
                                        'Seat Gap' : 0.0,
                                        'Aisle Width' : 0.35,
                                        'Seat Length' : 0.5,
                                        'Seat Height' : 0.35,
                                        'Seat Angle' : 5.,
                                        'Seat Width' : 0.5,
                                        'Rotate Seats' : 0,
                                        'Relative Position X' : 0.15,
                                        'Seats on Left Side' : 1.,
                                        'Seats on Mid Side' : 0.,
                                        'Seats on Right Side' : 1.},

                        'Cabin' :   { 'Name' : 'Cabin',
                                        'Name1' : 'PAX',
                                        'Draw PAX' : 'False',
                                        'PAX' : 19,
                                        'Seat Pitch' : 0.77,
                                        'Seat Gap' : 0.0,
                                        'Aisle Width' : 0.35,
                                        'Seat Length' : 0.5,
                                        'Seat Height' : 0.35,
                                        'Seat Angle' : 5.,
                                        'Seat Width' : 0.5,
                                        'Rotate Seats' : 0,
                                        'Relative Position X' : 0.2,
                                        'Seats on Left Side' : 1.,
                                        'Seats on Mid Side' : 0.,
                                        'Seats on Right Side' : 1.},

                         'Cargo Box 1' : { 'Name' : 'Cargo Box 1',
                                            'Relative Position X' : 0.642,
                                            'Relative Position Z' : 0.0422,
                                            'Box Width' : 1,
                                            'Box Height' : 1.5,
                                            'Box Length' : 0.6,},
            
                        'Cargo Box 2' : { 'Name' : 'Cargo Box 2',
                                        'Relative Position X' : 0.6785,
                                        'Relative Position Z' : 0.0422,
                                        'Box Width' : 1.,
                                        'Box Height' : 1.3,
                                        'Box Length' : 0.6,},
                        
                        'Cargo Box 3' : { 'Name' : 'Cargo Box 3',
                                        'Relative Position X' : 0.714,
                                        'Relative Position Z' : 0.0422,
                                        'Box Width' : 0.9,
                                        'Box Height' : 1.2,
                                        'Box Length' : 0.6,},

                        'Cargo Box 4' : {   'Name' : 'Cargo Box 4',
                                            'Relative Position X' : 0.06,
                                            'Relative Position Z' : 0.0181,
                                            'Box Width' : 0.9,
                                            'Box Height' : 0.7,
                                            'Box Length' : 1.32,},
                        'Duct'        : {   'Name' : 'Duct',
                                            'Relative Position X' : 0.96,
                                            'Relative Position Z' : 0.06,
                                            'Diameter' : 1.2,
                                            'Chord' : 1.5,
                                            'Thickness' : 0.15,
                                            'Camber' : 0.,
                                            'Camber_pos' : 0.,
                                            'COG' : [0.25, 0, 0.8],
                                            'FanWeight' : 120.,
                                            }
                        }

        self.GENERAL_INFO = {'g' : 9.81,
                             'rho_at_denver_mks' : 0.974,
                             'tail' : 'T',
                             'advanced_materials' : 'Yes',
                             'W_S_typical' : 195.,
                             'CLMAX' : clmax,
                             'Vtakeoff_Vstall': 1.1,
                             'LFL' : 900,
                             'TOFL' : 1000, }

        self.M_TO = 0.135
        self.psls = Pmax
        self.pcruise = Pcruise
        self.GENERAL_INFO['Oswald'] = 1.78*(1 - 0.045*self.GEOMETRY['Main_Wing']['AR']**0.68) - 0.64
        self.GENERAL_INFO['CD0'] = 0.0352
        self.etap = etap

    def apply_advanced_settings(self, settings):

        for key, item in settings.advanced_settings.items():
            if key in self.GEOMETRY.keys():
                for inner_key, inner_item in item.items():
                    self.GEOMETRY[key][inner_key] = json.loads(inner_item)
            else:
                for inner_key, inner_item in item.items():
                    self.GENERAL_INFO[inner_key] = json.loads(inner_item)
            
                    

    def define_mission(self, mission):

        self.distances = mission.distance
        self.altitude = mission.alttable
        self.duration = mission.timetable
        self.mission_inputs = mission.inputs
        
        self.roc_avg, self.glide = mission.climb('Climb', self.mission_inputs[3], self.mission_inputs[4],
                                                 self.mission_inputs[6], self.mission_inputs[7],
                                                 self.mission_inputs[11], 0.1)


    def Geometry_Sizing(self, MTOW):

        '''
        -------------------------------------------------------------------------------
        Size aircraft components based on Maximum Take-Off Weight estimated at sizing
        level 2
        
        INPUTS:
        MTOW :                  Maximum Take-Off Weight [kg]
        -------------------------------------------------------------------------------
        '''

        # Initialize Variables BEGIN #
        AR_w = self.GEOMETRY['Main_Wing']['AR']
        tpr_w = self.GEOMETRY['Main_Wing']['Taper']
        sweep_w = self.GEOMETRY['Main_Wing']['Sweep']
        AR_h = self.GEOMETRY['Horizontal_Tail']['AR']
        tpr_h = self.GEOMETRY['Horizontal_Tail']['Taper']
        sweep_h = self.GEOMETRY['Horizontal_Tail']['Sweep']
        AR_v = self.GEOMETRY['Vertical_Tail']['AR']
        tpr_v = self.GEOMETRY['Vertical_Tail']['Taper']
        sweep_v = self.GEOMETRY['Vertical_Tail']['Sweep']
        # Initialize Variables END #

        # Fuselage Length and Diameter from Raymer's approach (Table 6.3)
        a = self.GEOMETRY["Fuselage"]["a_fus"]
        c = self.GEOMETRY["Fuselage"]["c_fus"]
        L_f = a*MTOW**c # [m]
        f = self.GEOMETRY["Fuselage"]["f"] # Fuselage fitness factor
        Dmax = L_f/f # [m] Fuselage's max diameter
        L_tailarm = 0.5*L_f # [m] picked 50% for combination of aft mounted and wing mounted engines
        L_vt = L_tailarm - 0.6/16.56*L_f # Second term is a positioning scale factor to make VSP CAD dimensionless
        L_ht = L_tailarm + 0.6/16.56*L_f # Second term is a positioning scale factor to make VSP CAD dimensionless

        self.GEOMETRY['Fuselage'].update( {  'Length' : L_f,
                                            'Max Diameter' : Dmax,
                                            'Horizontal Tailarm' : L_ht,
                                            'Vertical Tailarm' : L_vt,
                                            'Fitness Factor' : f, } )
        
        # Wing and Empennage sizing
        tofl = self.GENERAL_INFO['TOFL']
        top = self.takeoff_parameter(tofl)
        Sref = MTOW/self.Calculate_Wing_Loading(TOP = top)
        [Span, Croot, Ctip, Cmean, Ybar] = self.Wing_Geometry_Characteristics(Sref, AR_w, tpr_w)

        sweep_c4 = np.rad2deg(np.arctan(np.tan(np.deg2rad(sweep_w) - (1 - tpr_w)/(AR_w*(1 + tpr_w)))))

        self.GEOMETRY['Main_Wing'].update( {    'Span' : Span,
                                                'Croot' : Croot,
                                                'Ctip' : Ctip,
                                                'Cmean' : Cmean,
                                                'Ybar' : Ybar,
                                                'Sweep_C4' : sweep_c4,
                                                'Sref' : Sref } )

        # Constant volume fractions according to Raymer (Table 6.4)
        Cvt = self.GEOMETRY["Fuselage"]["cvt"]
        Cht = self.GEOMETRY["Fuselage"]["cht"]

        Svt = Cvt*self.GEOMETRY['Main_Wing']['Span']*self.GEOMETRY['Main_Wing']['Sref']/L_vt

        [Span, Croot, Ctip, Cmean, Ybar] = self.Wing_Geometry_Characteristics(Svt, AR_v, tpr_v)

        sweep_c4 = np.rad2deg(np.arctan(np.tan(np.deg2rad(sweep_v) - (1 - tpr_v)/(AR_v*(1 + tpr_v)))))

        self.GEOMETRY['Vertical_Tail'].update( {    'Span' : Span,
                                                    'Croot' : Croot,
                                                    'Ctip' : Ctip,
                                                    'Cmean' : Cmean,
                                                    'Ybar' : 2*Ybar,
                                                    'Tailarm' : L_vt,
                                                    'Sweep_C4' : sweep_c4,
                                                    'Sref' : Svt } )

        Sht = Cht*self.GEOMETRY['Main_Wing']['Cmean']*self.GEOMETRY['Main_Wing']['Sref']/L_ht

        [Span, Croot, Ctip, Cmean, Ybar] = self.Wing_Geometry_Characteristics(Sht, AR_h, tpr_h)

        sweep_c4 = np.rad2deg(np.arctan(np.tan(np.deg2rad(sweep_h) - (1 - tpr_h)/(AR_h*(1 + tpr_h)))))

        self.GEOMETRY['Horizontal_Tail'].update( {      'Span' : Span,
                                                        'Croot' : Croot,
                                                        'Ctip' : Ctip,
                                                        'Cmean' : Cmean,
                                                        'Ybar' : Ybar,
                                                        'Tailarm' : L_ht,
                                                        'Sweep_C4' : sweep_c4,
                                                        'Sref' : Sht } )


    def Wing_Geometry_Characteristics(self, Sref, AR, taper):

            '''
            -------------------------------------------------------------------------------
            Determine wing geometry characteristics

            INPUTS:
            Sref    :                   Reference area [m2]
            AR      :                   Aspect ratio
            taper   :                   Taper ratio

            OUTPUTS:
            Span    :                   Wing span [m]
            Croot   :                   Wing root chord [m]
            Ctip    :                   Wing tip chord [m]
            Cmean   :                   Wing mean aerodynamic chord [m]
            Ybar    :                   Wing mean aerodynamic chord position [m]
            -------------------------------------------------------------------------------
            '''

            Span = (AR*Sref)**0.5 # [m]
            Croot = 2*Sref/(Span*(1 + taper)) # [m]
            Ctip = taper*Croot # [m]
            Cmean = 2/3*Croot*(1 + taper + taper**2)/(1 + taper) # [m]
            Ybar = Span/6*(1 + 2*taper)/(1 + taper) # [m]

            return Span, Croot, Ctip, Cmean, Ybar

    def Calculate_Wing_Loading(self, TOP = 350, CD0 = 0.02):

        '''
        -------------------------------------------------------------------------------
        Calculate aircraft wing loading per mission phase

        OPTIONAL INPUTS:
        
        1. TOP :                           Take-Off parameter 
        2. CD0 :                           Parasite Drag
        
        OUTPUTS:
        W_S    :                           Minimum required wing loading [kg/m2]
        -------------------------------------------------------------------------------
        '''

        # Initialize Variables BEGIN #
        SLS_atm_prop = SA('Metric', 0)
        Climb_atm_prop = SA('Metric', 0.5*(self.altitude['Climb'] - self.altitude['Take-off']))
        Cruise_atm_prop = SA('Metric', self.altitude['Cruise'])
        Loiter_atm_prop = SA('Metric', self.altitude['Hold'])
        rho_SLS = SLS_atm_prop[1]
        rho_climb = Climb_atm_prop[1]
        rho_cruise = Cruise_atm_prop[1]
        rho_loiter = Loiter_atm_prop[1]
        Vclimb = self.mission_inputs[9]*Climb_atm_prop[3]
        Vcruise = self.mission_inputs[8]*Cruise_atm_prop[3]
        Vloiter = self.mission_inputs[10]*Loiter_atm_prop[3]
        AR = self.GEOMETRY['Main_Wing']['AR']
        g = self.GENERAL_INFO['g']
        ROC = self.roc_avg
        # ROC = self.DUMMY['ROC']
        h = self.altitude['Cruise'] - 457.2 # Take-Off phase untill 1500 ft
        # Initialize Variables END #

        # Take-Off Wing Loading
        sigma = self.GENERAL_INFO['rho_at_denver_mks']/rho_SLS
        CL_TO = self.GENERAL_INFO['CLMAX']/self.GENERAL_INFO['Vtakeoff_Vstall']

        # Take-off field length <= 1000m from TLAR's
        # According to Raymer's approach from Figure 5.4 and an over 50 ft obstacle
        P_W_hp = 1.341*self.Calculate_Power_Loading(self.psls, self.pcruise, self.etap) # Convert kW/kg to hp/kg
        W_S_takeoff = TOP*sigma*CL_TO*P_W_hp # [kg/m^2]

        # Landing Wing Loading
        Sa = self.GENERAL_INFO["S_a"] # [m] Obstacle clearence distance from Raymer's approach (General Aviation Power-off approach)
        LFL = self.GENERAL_INFO['LFL']
        W_S_landing = (LFL - Sa)*sigma*self.GENERAL_INFO['CLMAX']/5 # [kg/m^2]

        # Cruise Wing Loading
        e = 1.78*(1 - 0.045*AR**0.68) - 0.64 # Oswald Parameter
        self.GENERAL_INFO.update( { 'CD0' : CD0,
                                     'Oswald' : e } )
        cruise_dynamic_head = 0.5*rho_cruise*Vcruise**2
        W2_W0 = 0.97*0.985
        W_S_cruise = cruise_dynamic_head*np.sqrt(np.pi*AR*e*CD0)/(g*W2_W0) # [kg/m^2] comparable with T.O.

        # Loiter Wing Loading
        loiter_dynamic_head = 0.5*rho_loiter*Vloiter**2
        W_S_loiter = loiter_dynamic_head*np.sqrt(3*np.pi*AR*e*CD0)/(g*0.85) # [kg/m^2] # Divide by 0.85 to be comparable with T.O

        # Climb and Glide
        climb_angle = np.arcsin(ROC/Vclimb)
        Vclimb_x = Vclimb*np.cos(climb_angle)
        t_glide = h/ROC # Glide time [s]
        glide_horizontal_dist = Vclimb_x*t_glide
        G = h/glide_horizontal_dist # Climb Gradient
        climb_dynamic_head = 0.5*rho_climb*Vclimb**2
        L_D = self.Lift2Drag_Simple()
        T_W_climb = 1/L_D['Climb'] + ROC/Vclimb
        W_S_climb_1 = (T_W_climb - G + np.sqrt((T_W_climb - G)**2 - 4*CD0/(np.pi*AR*e)))/(2/(climb_dynamic_head*np.pi*AR*e))/(g*0.97) # [kg/m^2]
        W_S_climb_2 = (T_W_climb - G - np.sqrt((T_W_climb - G)**2 - 4*CD0/(np.pi*AR*e)))/(2/(climb_dynamic_head*np.pi*AR*e))/(g*0.97) # [kg/m^2]

        W_S = min(W_S_cruise, W_S_climb_1, W_S_takeoff, W_S_loiter, W_S_landing)
        
        return W_S

    def Calculate_Power_Loading(self, sls_power, cruise_power, etap):

        '''
        -------------------------------------------------------------------------------
        Calculate aircraft power loading per mission phase
        
        OUTPUTS:
        P_W    :                           Maximum required power loading [kW/kg]
        -------------------------------------------------------------------------------
        '''

        # Initialize Variables BEGIN #
        SLS_atm_prop = SA('Metric', 0)
        TO_atm_prop = SA('Metric', self.altitude['Taxi-out'])
        Climb_atm_prop = SA('Metric', 0.5*(self.altitude['Climb'] - self.altitude['Take-off']))
        Cruise_atm_prop = SA('Metric', self.altitude['Cruise'])
        rho_SLS = SLS_atm_prop[1]
        Vtakeoff = self.M_TO*TO_atm_prop[3]
        Vclimb = self.mission_inputs[9]*Climb_atm_prop[3]
        Vcruise = self.mission_inputs[8]*Cruise_atm_prop[3]
        g = self.GENERAL_INFO['g']
        ROC = self.roc_avg
        self.VTO = Vtakeoff
        # ROC = self.DUMMY['ROC']

        # Initialize Variables END #

        # Calculate the power loading of the aircraft for the initial sizing module. More accurate power calculations will follow in the mission model

        P_W_table = self.GENERAL_INFO["P_W_table"] # [kW/kg] Empirical power loading from Tabulated data for twin-turboprop engines

        # Regression factors according to data for twin-turboprop engines
        a = self.GENERAL_INFO["a"]
        c = self.GENERAL_INFO["c"]
        P_W_reg = a*(Vcruise/3.6)**c # [kW/kg] (Vcruise must be in km/h)

        # Thrust matching
        L_D = self.Lift2Drag_Simple()

        # Cruise thrust matching
        T_W_cruise = 1/L_D.get("Cruise")
        Wcruise_WTO = 0.97*0.985

        P_TO_SLS = sls_power # [W]
        P_cruise = cruise_power # [W]
        prop_diameter = 0.49*(P_TO_SLS/1000)**0.25 # [m]
        self.GEOMETRY['PT6A - 67D L'].update( { 'Propeller Diameter' : prop_diameter } )
        self.GEOMETRY['PT6A - 67D R'].update( { 'Propeller Diameter' : prop_diameter } )
        T_TO_SLS = (P_TO_SLS**2*etap['Take-off']**2*np.pi*prop_diameter**2/2*rho_SLS)**(1/3)
        T_cruise = P_cruise*etap['Cruise']/Vcruise
        T_W_takeoff = T_W_cruise*Wcruise_WTO*T_TO_SLS/T_cruise
        P_W_takeoff = T_W_takeoff*Vtakeoff/etap['Take-off']*g/1000 # [kW/kg]

        # Climb thrust matching
        Wclimb_WTO = 0.97
        T_W_climb = 1/L_D['Climb'] + ROC/Vclimb
        P_W_climb = T_W_climb*Wclimb_WTO*Vclimb/etap['Climb']*g/1000 # [kW/kg]

        P_W = max(P_W_reg, P_W_table, P_W_takeoff, P_W_climb)
        
        self.PW_ratio = P_W

        return P_W

    def Lift2Drag_Simple(self):

        '''
        -------------------------------------------------------------------------------
        Simple lift to drag ratio estimation
        
        OUTPUTS:
        L_D    :                           Lift to drag ratio [-]
        -------------------------------------------------------------------------------
        '''

        # Calculate Lift to Drag ratio according to Raymer for Sizing Level 1

        # Initialize Variables BEGIN #
        AR = self.GEOMETRY['Main_Wing']['AR']
        Wet2Ref = self.GEOMETRY['Main_Wing']['Wetted2Reference_area_ratio']
        KLD = self.GEOMETRY['Main_Wing']['KLD']
        # Initialize Variables END #

        Awet = AR/Wet2Ref
        L_Dmax = KLD*Awet**0.5
        L_D = {
            'Cruise' : L_Dmax,
            'Loiter' : 0.866*L_Dmax,
            'Climb' : 0.5*1.866*L_Dmax,
        }

        return L_D

    def lift2drag_detailed(self, W_S):

        AR = self.GEOMETRY['Main_Wing']['AR']
        e = self.GENERAL_INFO['Oswald']
        CD0 = self.GENERAL_INFO['CD0']

        Climb_atm_prop = SA('Metric',  0.5*(self.altitude['Climb'] - self.altitude['Take-off']))
        Cruise_atm_prop = SA('Metric', self.altitude['Cruise'])
        Descent_atm_prop = SA('Metric', self.altitude['Descent'])
        Loiter_atm_prop = SA('Metric', self.altitude['Hold'])
        Divclimb_atm_prop = SA('Metric', 0.5*(self.altitude['DivClimb'] - self.altitude['Overshoot']))
        DivCruise_atm_prop = SA('Metric', self.altitude['DivCruise'])
        DivDescent_atm_prop = SA('Metric', self.altitude['DivDescent'])
        rho_climb = Climb_atm_prop[1]
        rho_cruise = Cruise_atm_prop[1]
        rho_descent = Descent_atm_prop[1]
        rho_loiter = Loiter_atm_prop[1]
        rho_divclimb = Divclimb_atm_prop[1]
        rho_divcruise = DivCruise_atm_prop[1]
        rho_divdescent = DivDescent_atm_prop[1]
        Vclimb = self.mission_inputs[9]*Climb_atm_prop[3]
        Vcruise = self.mission_inputs[8]*Cruise_atm_prop[3]
        Vdescent = self.mission_inputs[10]*Descent_atm_prop[3]
        Vloiter = self.mission_inputs[10]*Loiter_atm_prop[3]
        Vdivclimb = self.mission_inputs[9]*Divclimb_atm_prop[3]
        Vdivcruise = self.mission_inputs[8]*DivCruise_atm_prop[3]
        Vdivdescent = self.mission_inputs[10]*DivDescent_atm_prop[3]
        q_climb = 0.5*rho_climb*Vclimb**2
        q_cruise = 0.5*rho_cruise*Vcruise**2
        q_descent = 0.5*rho_descent*Vdescent**2
        q_loiter = 0.5*rho_loiter*Vloiter**2
        q_divclimb = 0.5*rho_divclimb*Vdivclimb**2
        q_divcruise = 0.5*rho_divcruise*Vdivcruise**2
        q_divdescent = 0.5*rho_divdescent*Vdivdescent**2

        L_D_climb = 1/(q_climb*CD0/W_S + W_S/(q_climb*np.pi*AR*e))
        L_D_cruise = 1/(q_cruise*CD0/W_S + W_S/(q_cruise*np.pi*AR*e))
        L_D_descent = 1/(q_descent*CD0/W_S + W_S/(q_descent*np.pi*AR*e))
        L_D_divclimb = 1/(q_divclimb*CD0/W_S + W_S/(q_divclimb*np.pi*AR*e))
        L_D_divcruise = 1/(q_divcruise*CD0/W_S + W_S/(q_divcruise*np.pi*AR*e))
        L_D_divdescent = 1/(q_divdescent*CD0/W_S + W_S/(q_divdescent*np.pi*AR*e))
        L_D_loiter = 1/(q_loiter*CD0/W_S + W_S/(q_loiter*np.pi*AR*e))

        self.Lift2Drag_Detailed = {
                'Climb' : L_D_climb,
                'Cruise' : L_D_cruise,
                'Descent' : L_D_descent,
                'DivClimb' : L_D_divclimb,
                'DivCruise' : L_D_divcruise,
                'DivDescent' : L_D_divdescent,
                'Loiter' : L_D_loiter,
            }

    def Landing_Gear(self, MTOW):

        '''
        -------------------------------------------------------------------------------
        Calculate landing gear properties

        INPUTS:
        MTOW  :                 Maximum Take-Off Mass [kg]

        OUTPUTS:
        Landing_gear            Dictionary, including keys:
                                            1. "Front Wheel Diameter"
                                            2. "Front Wheel Width"
                                            3. "Front Wheel No"
                                            4. "Rear Wheel Diameter"
                                            5. "Rear Wheel Width"
                                            6. "Rear Wheel No"
                                            7. "Frontal Area"
        -------------------------------------------------------------------------------
        '''

        # This function calculates the basic dimensions of the landing gear wheels
        # More aircraft options will be added in a future relesae
        # Damping calculation not included at the momment
        # More landing gear layouts will be included soon

        # Table 11.1 for Transport/Bomber Aircraft
        A = self.GEOMETRY["Landing_Gear"]["A"]
        B = self.GEOMETRY["Landing_Gear"]["B"]
        C = self.GEOMETRY["Landing_Gear"]["C"]
        D = self.GEOMETRY["Landing_Gear"]["D"]
        
        # Calculate Weight per Wheel
        No_m = self.GEOMETRY["Landing_Gear"]["No_wheels_r"] # Assume 2 wheels per main mechanism
        No_f = self.GEOMETRY["Landing_Gear"]["No_wheels_fr"] # Assume 1 wheel in front mechanism
        Ww_m = MTOW*0.9/2/No_m # 90 % of MTOW carried by main landing gear
        fr2r_ratio = self.GEOMETRY["Landing_Gear"]["fr2r_wheels_ratio"]

        Dia_m = A*Ww_m**B # [cm]
        Wid_m = C*Ww_m**D # [cm]
        # According to Raymer pg.344 nose tyres can be assumed 60-100 % of main tyres
        Dia_f = fr2r_ratio*Dia_m # [cm]
        Wid_f = fr2r_ratio*Wid_m # [cm]

        frontal_area = (Dia_f*Wid_f*No_f + 2*No_m*Dia_m*Wid_m)/10000 # [m^2]
        # Assuming struts to be 13 % of total frontal area (estimation)
        Afr = 1.13*frontal_area

        Landing_gear = { "Front Wheel Diameter" : Dia_f,
                         "Front Wheel Width" : Wid_f,
                         "Front Wheel No" : No_f,
                         "Rear Wheel Diameter" : Dia_m,
                         "Rear Wheel Width" : Wid_m,
                         "Rear Wheel No" : 2*No_m,
                         "Frontal Area" : Afr }
        
        return Landing_gear

    def Empty_Weight_Estimation_Level_3_Transport(self, MTOW, Nz, conventional_tail, pres_cab,
                                                  advanced_materials, Surf_from_model = None,
                                                  Vol_from_model = None, GEO = None):

        '''
        -------------------------------------------------------------------------------
        Estimate empty weight mass fraction from aircraft dimensions
        
        INPUTS:
        MTOW                :                         Maximum Take-Off Mass [kg]
        Nz                  :                         Ultimate loading factor [-]
        conventional_tail   :                         True for inversed T tail, False for T-tail
        pres_cab            :                         True for cabin pressurization, false for non-pressurized cabin
        advanced_materials  :                         True to consider advanced materials, false to use conventional materials
        Surf_from_model     : [optional]              True to use surfaces from model                        
        Vol_from_model      : [optional]              True to use volumes from model
        GEO                 : [optional]              Geomtery dictionary (see notes)

        OUTPUTS:
        OEW                 :                         Empty weight mass [kg]

        NOTES:
        GEOMETRY dictionary is a self attribute of the class
        to use the funciton outside the class, use GEOMETRY = YOUR_DICT in the attributes
        YOUR_DICT must have the Fuselage, Main_Wing, Horizontal_Tail, Vertical_Tail, Engine keys
        Each key has a dictionary as an item with basic dimensions as keys
        -------------------------------------------------------------------------------
        '''

        if GEO == None:
            GEOMETRY = self.GEOMETRY
        

        # Fudge factors from Raymer Chapter 15, Table 15.4
        if advanced_materials:
            fudge_wing = 0.85
            fudge_tails = 0.83
            fudge_lg = 0.95
            fudge_fus = 0.9
        else:
            fudge_wing = 1
            fudge_tails = 1
            fudge_lg = 1
            fudge_fus = 1
        
        if conventional_tail:
            Ht_Hv = 0
        else:
            Ht_Hv = 1

        if Surf_from_model ==  None and Vol_from_model == None:
            Sf = (0.0122*MTOW - 7.4269)/0.3048**2
            Vpr = (0.0105*MTOW - 29.897)/0.3048**3
        else:
            Sf = Surf_from_model["Fuselage"]/0.3048**2 # [ft^2]
            Vpr = Vol_from_model["Fuselage"]/0.3048**3 # [ft^3]

        # Find Control Surface Area of Main Wing
        Surf = 0 
        for i, item in enumerate(GEOMETRY['Main_Wing']['ChordRatio']):
            Surf = Surf + item*GEOMETRY['Main_Wing']['SpanRatio'][i]
        Scsw = Surf*GEOMETRY['Main_Wing']['Sref']

        # Find Control Surface Area of Horizontal Tail
        Surf = 0
        for i, item in enumerate(GEOMETRY['Horizontal_Tail']['ChordRatio']):
            Surf = Surf + item*GEOMETRY['Horizontal_Tail']['SpanRatio'][i]
        Se_Sht = Surf/GEOMETRY['Horizontal_Tail']['Sref']

        # Convert to fps units
        Wdg = MTOW*2.2046226218488 # [lbs]
        Sw = GEOMETRY['Main_Wing']['Sref']/0.3048**2 # [ft^2]
        Scsw = Scsw/0.3048**2 # [ft^2]
        Sht = GEOMETRY['Horizontal_Tail']['Sref']/0.3048**2 # [ft^2]
        Lht = GEOMETRY['Fuselage']['Horizontal Tailarm']/0.3048 # [ft]
        Lvt = GEOMETRY['Fuselage']['Vertical Tailarm']/0.3048 # [ft]
        Svt = GEOMETRY['Vertical_Tail']['Sref']/0.3048**2 # [ft^2]
        L = GEOMETRY['Fuselage']['Length']/0.3048 # [ft]
        D = GEOMETRY['Fuselage']['Max Diameter']/0.3048 # [ft]
        Fw = GEOMETRY['Fuselage']['Max Diameter']/0.3048 # [ft]
        Bw = GEOMETRY['Main_Wing']['Span']/0.3048 # [ft]
        Bh = GEOMETRY['Horizontal_Tail']['Span']/0.3048 # [ft]
        Wen = (GEOMETRY['PT6A - 67D L']['Weight'])*2.2046226218488 # [lbs]
        Nen = GEOMETRY['PT6A - 67D L']['No_GT'] + GEOMETRY['PT6A - 67D R']['No_GT']
        # End of conversion

        taper_w = GEOMETRY['Main_Wing']['Ctip']/GEOMETRY['Main_Wing']['Croot']
        Sweep_w = GEOMETRY['Main_Wing']['Sweep']
        Sweep_ht = GEOMETRY['Horizontal_Tail']['Sweep']
        Sweep_vt = GEOMETRY['Vertical_Tail']['Sweep']
        A_w = GEOMETRY['Main_Wing']['AR']
        A_h = GEOMETRY['Horizontal_Tail']['AR']
        A_v = GEOMETRY['Vertical_Tail']['AR']
        t_c_w = GEOMETRY['Main_Wing']['Thickness']
        t_c_v = GEOMETRY['Vertical_Tail']['Thickness']
        

        # from page 577 on Raymer's Approach
        Kuht = 1.0 # 1.143 for unit all moving horiozntal tail, otherwise Kuht=1
        Kdoor = 1.06 # one side cargo door
        Klg = 1.12 # fuselage mounted main landing gear
        Ky = 0.3*Lht
        Kz = Lvt
        Kws = 0.75*((1 + 2*taper_w)/(1 + taper_w)*Bw/L*np.tan(np.radians(Sweep_w)))

        if pres_cab:
            pd = 8 # [psi] pressure differential
            Wpress = 11.9*(Vpr*pd)**0.271 # [lbs] pressurized cabin penalty weight
        else:
            Wpress = 0
        
        W_Wing = 0.0051*(Wdg*Nz)**0.557*Sw**0.649*A_w**0.5*t_c_w**-0.4*(1 + taper_w)**0.1*np.cos(np.radians(Sweep_w))**-1*Scsw**0.1*fudge_wing
        W_Horizontal_tail = 0.0379*Kuht*(1 + Fw/Bh)**-0.25*Wdg**0.639*Nz**0.1*Sht**0.75*Lht**-1*Ky**0.704*np.cos(np.radians(Sweep_ht))**-1*A_h**0.166*(1 + Se_Sht)**0.1*fudge_tails
        W_Vertical_tail = 0.0026*(1 + Ht_Hv)**0.225*Wdg**0.556*Nz**0.536*Lvt**-0.5*Svt**0.5*Kz**0.875*np.cos(np.radians(Sweep_vt))**-1*A_v**0.35*t_c_v**-0.5*fudge_tails
        W_fuselage = (0.328*Kdoor*Klg*(Wdg*Nz)**0.5*L**0.25*Sf**0.302*(1 + Kws)**0.04*(L/D)**0.1 + Wpress)*fudge_fus
        W_landing_gear = 0.043*Wdg*fudge_lg # from Table 15.2
        W_eng_installed = 2.575*Wen**0.922*Nen
        Welse = 0.17*Wdg

        OEW = { "Main_Wing" : W_Wing,
                "Horizontal_Tail" : W_Horizontal_tail,
                "Vertical_Tail" : W_Vertical_tail,
                "Fuselage" : W_fuselage,
                "Landing_Gear" : W_landing_gear,
                "Installed_Engines" : W_eng_installed,
                "Else" : Welse}

        for pids, pparts in OEW.items():\
            OEW.update( { pids : pparts/2.2046226218488 } )

        return OEW
    
    def Empty_Weight_Estimation_Level_3_General_Aviation(self, TLARS, Mission, Weights, Nz, conventional_tail,
                                                         pres_cab, simple, advanced_materials, GEO = None,
                                                         Surf_from_model = None, Vol_from_model = None):

        '''
        -------------------------------------------------------------------------------
        Estimate empty weight mass fraction from aircraft dimensions
        
        INPUTS:
        TLARS               :                         Top Level Aircraft Requirements dictionary (Crew, Pax)
        Mission             :                         Mission attributes (Mcruise, Vcruise, rho_cruise)
        Nz                  :                         Ultimate loading factor [-]
        conventional_tail   :                         True for inversed T tail, False for T-tail
        pres_cab            :                         True for cabin pressurization, false for non-pressurized cabin
        simple              :                         True to follow simple component build-up, False to follow detailed component build-up                         
        advanced_materials  :                         True to consider advanced materials, false to use conventional materials
        GEO                 : [optional]              Geomtery dictionary (see notes)
        Surf_from_model     : [optional]              True to use surfaces from model                        
        Vol_from_model      : [optional]              True to use volumes from model

        OUTPUTS:
        OEW                 :                         Empty weight mass [kg]

        NOTES:
        GEOMETRY dictionary is a self attribute of the class
        to use the funciton outside the class, use GEOMETRY = YOUR_DICT in the attributes
        YOUR_DICT must have the Fuselage, Main_Wing, Horizontal_Tail, Vertical_Tail, Engine keys
        Each key has a dictionary as an item with basic dimensions as keys
        -------------------------------------------------------------------------------
        '''
        
        # GEOMETRY dictionary is a self attribute of the class
        # to use the funciton outside the class, use GEOMETRY = YOUR_DICT in the attributes
        # YOUR_DICT must have the Fuselage, Main_Wing, Horizontal_Tail, Vertical_Tail, Engine keys
        # Each key has a dictionary as an item with basic dimensions as keys

        if GEO == None:
            GEOMETRY = self.GEOMETRY

        if conventional_tail:
            Ht_Hv = 0
        else:
            Ht_Hv = 1

        # Fudge factors from Raymer Chapter 15, Table 15.4
        if advanced_materials:
            if self.EIS < 2035:
                fudge_wing = 0.9
                fudge_tails = 0.85
                fudge_lg = 0.97
                fudge_fus = 0.95
            else:
                fudge_wing = 0.85
                fudge_tails = 0.8
                fudge_lg = 0.95
                fudge_fus = 0.9
        else:
            fudge_wing = 1
            fudge_tails = 1
            fudge_lg = 1
            fudge_fus = 1

        if Surf_from_model ==  None and Vol_from_model == None:
            Sf = (0.0122*Weights['MTOW'] - 7.4269)/0.3048**2
            Vpr = (0.0105*Weights['MTOW'] - 29.897)/0.3048**3
        else:
            Sf = Surf_from_model["Fuselage"]/0.3048**2 # [ft^2]
            Vpr = Vol_from_model["Fuselage"]/0.3048**3 # [ft^3]
   
        # convert to fps units first
        Sw = GEOMETRY['Main_Wing']['Sref']/0.3048**2 # [ft^2]
        Sht = GEOMETRY['Horizontal_Tail']['Sref']/0.3048**2 # [ft^2]
        Svt = GEOMETRY['Vertical_Tail']['Sref']/0.3048**2 # [ft^2]
        Lt = GEOMETRY['Fuselage']['Horizontal Tailarm']/0.3048 # [ft]
        L = GEOMETRY['Fuselage']['Length']/0.3048 # [ft]
        D = GEOMETRY['Fuselage']['Max Diameter']/0.3048 # [ft]
        Wfw = Weights["Fuel"]*2.2046226218488 # [lbs]
        Wdg = Weights["MTOW"]*2.2046226218488 # [lbs]
        Bw = GEOMETRY['Main_Wing']['Span']/0.3048 # [ft]
        Wen = (GEOMETRY['PT6A - 67D L']['Weight'])*2.2046226218488 # [lbs]
        Nen = GEOMETRY['PT6A - 67D L']['No_GT'] + GEOMETRY['PT6A - 67D R']['No_GT'] 
        # End of Unit Conversion

        taper_w = GEOMETRY['Main_Wing']['Ctip']/GEOMETRY['Main_Wing']['Croot']
        taper_h = GEOMETRY['Horizontal_Tail']['Ctip']/GEOMETRY['Horizontal_Tail']['Croot']
        taper_v = GEOMETRY['Vertical_Tail']['Ctip']/GEOMETRY['Vertical_Tail']['Croot']
        Sweep_w = GEOMETRY['Main_Wing']['Sweep']
        Sweep_h = GEOMETRY['Horizontal_Tail']['Sweep']
        Sweep_v = GEOMETRY['Vertical_Tail']['Sweep']
        A_w = GEOMETRY['Main_Wing']['AR']
        A_h = GEOMETRY['Horizontal_Tail']['AR']
        A_v = GEOMETRY['Vertical_Tail']['AR']
        t_c_w = GEOMETRY['Main_Wing']['Thickness']
        t_c_v = GEOMETRY['Vertical_Tail']['Thickness']
        t_c_h = GEOMETRY['Horizontal_Tail']['Thickness']

        q = 0.020885434273039*0.5*Mission["Cruise_rho_mks"]*Mission["Vcruise_mps"]**2 # [lb/ft^2]
        M = Mission["Mcruise"]
        Np = TLARS["PAX"] + TLARS["Crew"]

        Nt = 2 # Two fuel tanks
        Vt = Weights["Fuel"]/0.810*0.2641720524 # gal

        if taper_v < 0.2:
            taper_v = 0.2

        if pres_cab:
            pd = 8 # [psi] pressure differential
            Wpress = 11.9*(Vpr*pd)**0.271 # [lbs] pressurized cabin penalty weight
        else:
            Wpress = 0
        
        W_Wing = 0.036*Sw**0.758*Wfw**0.0035*(A_w/(np.cos(np.radians(Sweep_w)))**2)**0.6*q**0.006*taper_w**0.04*(100*t_c_w/np.cos(np.radians(Sweep_w)))**-0.3*(Nz*Wdg)**0.49*fudge_wing
        W_Horizontal_tail = 0.016*(Nz*Wdg)**0.414*q**0.168*Sht**0.896*(100*t_c_h/np.cos(np.radians(Sweep_h)))**-0.12*(A_h/(np.cos(np.radians(Sweep_h)))**2)**0.043*taper_h**-0.02*fudge_tails
        W_Vertical_tail = 0.073*(1 + 0.2*Ht_Hv)*(Nz*Wdg)**0.376*q**0.122*Svt**0.873*(100*t_c_v/np.cos(np.radians(Sweep_v)))**-0.49*(A_v/(np.cos(np.radians(Sweep_v)))**2)**0.357*taper_v**0.039*fudge_tails
        W_fuselage = (0.052*Sf**1.086*(Nz*Wdg)**0.177*Lt**-0.051*(L/D)**-0.072*q**0.241 + Wpress)*fudge_fus
        W_landing_gear = 0.057*Wdg*fudge_lg # from Table 15.2
        W_eng_installed = 2.575*Wen**0.922*Nen

        if simple:
            Welse = 0.1*Wdg
            OEW = { "Main_Wing" : W_Wing,
                    "Horizontal_Tail" : W_Horizontal_tail,
                    "Vertical_Tail" : W_Vertical_tail,
                    "Fuselage" : W_fuselage,
                    "Landing_Gear" : W_landing_gear,
                    "Installed_Engines" : W_eng_installed,
                    "Else" : Welse}
        else:
            Wfuel_system = 2.49*Vt**0.726*(1/(1 + 1.2))**0.363*Nt**0.242*Nen**0.157
            Wflight_controls = 0.053*L**1.536*Bw**0.371*(Nz*Wdg*10**-4)**0.8
            if M < 0.2:
                Kh = 0.013
                M_ = 0.1
            elif M < 0.3:
                Kh = 0.05
                M_ = M
            elif M < 0.6:
                Kh = 0.11
                M_ = M
            else:
                Kh = 0.12
                M_ = M
            Whydraulics = Kh*Wdg*0.8*M_**0.5
            Wavionics = 2.117*800**0.933
            Welectrical = 12.57*(Wfuel_system + Wavionics)**0.51
            Wac = 0.265*Wdg**0.52*Np**0.68*Wavionics**0.17*M**0.08
            Wfurnish = 0.0582*Wdg - 65
            OEW = { "Main_Wing" : W_Wing,
                    "Horizontal_Tail" : W_Horizontal_tail,
                    "Vertical_Tail" : W_Vertical_tail,
                    "Fuselage" : W_fuselage,
                    "Landing_Gear" : W_landing_gear,
                    "Installed_Engines" : W_eng_installed,
                    "Fuel_System" : Wfuel_system,
                    "Flight_Controls" : Wflight_controls,
                    "Hydraulics" : Whydraulics,
                    "Avionics" : Wavionics,
                    "Electrical" : Welectrical,
                    "Air_Conditioning" : Wac,
                    "Furnish" : Wfurnish }

        for pids, pparts in OEW.items():
            OEW.update( { pids : pparts/2.2046226218488 } )
        
        return OEW

    def takeoff_parameter(self, tofl, atype = 'Propeller', case = '50ft', neng = 2):

        '''
        -------------------------------------------------------------------------------
        Calculate Take-off parameter

        INPUTS:
        tofl  :                 Take-off field length [m] [required]
        atype :                 aircraft type [optional]
                                                Available Types:
                                                                1. "Propeller"
                                                                2. "Jet"
                                                                3. "Fan"
        case  :                 Take-off case [optional]
                                                Available cases:
                                                                1. "50ft" (over 50ft obstacle)
                                                                2. "GR"   (ground roll)
        neng  :                 number of engines (for Fan type only) [optional]
                                                Available inputs:
                                                                1. 2
                                                                2. 3
                                                                3. 4

        OUTPUTS:
        top            take-off parameter
        -------------------------------------------------------------------------------
        '''

        x = np.array([])
        y = np.array([])
        top = 1e6

        tofl = tofl*3.2808399/1000

        if atype == 'Propeller':

            if case == '50ft':

                ### Propeller over 50 ft
                x = np.array([98.28054148682065, 161.26696288972485, 266.063366786447,
                              412.126733572894, 537.5565567746094, 638.5520720021569])
                y = np.array([0.8925514796670808, 1.483516292088071, 2.5579973965971314,
                              4.102563984328906, 5.526251242862405, 6.815628875684788])

            elif case == 'GR':

                ### Propeller ground roll
                x = np.array([102.08143015599524, 205.24885809359714, 300.27148908875677,
                              418.09953495212295, 530.4977990403532, 633.6652269779552])
                y = np.array([0.6239312035398157, 1.429792031921611, 2.208791242572693,
                              3.2429788957806513, 4.317460000289712, 5.391941104798772])

            else:
                raise ValueError('Invalid case. Valid inputs are 1. "50ft", and "GR" ')

        elif atype == 'Jet':
            
            if case == '50ft':

                ### Jet over 50 ft
                x = np.array([80.36197164281589, 140.63346073157268, 204.70587991608355,
                              270.95021181064874, 331.7647205034986, 391.49323141474184,
                              457.194626558373, 512.5792291963485])
                y = np.array([1.4700854832227142, 2.6654448922250182, 4.062270533027803,
                              5.566544694163508, 7.07081783059418, 8.588522288242725,
                              10.321123274204592, 11.879120926977983])

            elif case == 'GR':

                ### Jet ground roll
                x = np.array([86.87783405271739, 153.66514412479617, 230.22622709843748,
                              303.52939958041776, 376.8326134889776, 456.1085873501868,
                              526.6968275180196])
                y = np.array([1.201465207095449, 2.4774115186999586, 4.03540891529709,
                              5.6202674172724185, 7.285714358907502, 9.192917909529072,
                              11.019536094605986])
            
            else:
                raise ValueError('Invalid case. Valid inputs are 1. "50ft", and "GR" ')

        elif atype == 'Fan':
            
            if neng == 2:

                ### FAR Take-Off BFL 2-eng
                x = np.array([54.29864628294837, 92.85067685852582, 140.0904825540591,
                              188.95926420871263, 231.85520305755773, 273.1221659472826,
                              316.5610829736413])
                y = np.array([2.0744811045090605, 3.6324785011061924, 5.566544694163508,
                              7.540903313816894, 9.286935108644117, 10.97924289948114,
                              12.73870575934998])

            elif neng == 3:

                ### FAR Take-Off BFL 3-eng
                x = np.array([57.01357859709579, 101.53845197848165, 156.9230546164572,
                              206.3348558752038, 262.8054148682065, 324.16290173857])
                y = np.array([2.0476184620733147, 3.7130643790033653, 5.7948715189896705,
                              7.648351321797297, 9.79731353081542, 12.080586134073432])

            elif neng == 4:

                ### FAR Take-Off BFL 4-eng
                x = np.array([58.64251312963654, 100.99547380096807, 162.8959388488451,
                              225.33938207423574, 282.3529606713315, 336.65156552770037])
                y = np.array([1.9670325841761416, 3.4444441028761, 5.566544694163508,
                              7.742368520912343, 9.70329684405289, 11.51648345173567])
            
            else:
                raise ValueError('Invalid neng. Valid inputs are 2, 3, and 4 ')

        else:
            raise ValueError('Invalid atype. Valid inputs are 1. "Propeller", 2. "Jet", and 3. "Fan" ')

        if not x.size == 0:
            top_par = interp1d(y, x)
            top = top_par(tofl)

        return top

    def Calbing_Length(self, configuration):

        '''
        -------------------------------------------------------------------------------
        Calculate cabling length

        INPUTS:
        configuration  :                 aircraft configuration type

        OUTPUTS:
        Cable_lengths                    Dictionary, including keys:
                                                    1. AC_Cables
                                                    2. DC_Cables
                                                    3. DC_HP_Cables
                                                    4. DC_LP_Cables
                                                    5. Container_Cables
        -------------------------------------------------------------------------------
        '''

        Cable_lengths = {
                'AC_Cables' : 0,
                'DC_Cables' : 0,
                'DC_HP_Cables' : 0,
                'DC_LP_Cables' : 0,
                'Container_Cables' : 0,
            }

        Lfus = self.GEOMETRY['Fuselage']['Length']

        if 'Series' in configuration and 'Parallel' in configuration:

            '''
            -------------------------------------------------------------------
            Series/Parallel Configuration
            -------------------------------------------------------------------
            '''

            x_batt_loc = Lfus*self.GEOMETRY['Landing_Gear']['Relative Position X']

            batM2BLI = (Lfus - x_batt_loc)

            batM2EM = (abs(self.GEOMETRY['Landing_Gear']['Relative Position X'] -\
                    self.GEOMETRY['PT6A - 67D L']['Relative Position X Eng']) +\
                    abs(self.GEOMETRY['PT6A - 67D L']['Relative Position Y Eng']) +\
                    self.GEOMETRY['PT6A - 67D L']['Relative Position Z Eng'] -\
                    self.GEOMETRY['Landing_Gear']['Relative Position Z'])*Lfus
            
            batF2batM = (abs(self.GEOMETRY['Landing_Gear']['Relative Position X'] -\
                 self.GEOMETRY['Cargo Box 4']['Relative Position X']) +\
                     abs(self.GEOMETRY['Landing_Gear']['Relative Position Z'] -\
                          self.GEOMETRY['Cargo Box 4']['Relative Position Z']))*Lfus

            batM2batA = (abs(self.GEOMETRY['Landing_Gear']['Relative Position X'] -\
                self.GEOMETRY['Cargo Box 1']['Relative Position X']) +\
                    abs(self.GEOMETRY['Landing_Gear']['Relative Position Z'] -\
                          self.GEOMETRY['Cargo Box 1']['Relative Position Z']))*Lfus

            Cable_lengths['DC_Cables'] = batM2BLI + batM2EM + batF2batM + batM2batA
            Cable_lengths['AC_Cables'] = 0.02*Cable_lengths['DC_Cables']
            Cable_lengths['DC_HP_Cables'] = batM2BLI
            Cable_lengths['DC_LP_Cables'] = batM2EM
            Cable_lengths['Container_Cables'] = batF2batM + batM2batA


        if 'Parallel' in configuration and 'Series' not in configuration:

            '''
            -------------------------------------------------------------------
            Parallel Configuration
            -------------------------------------------------------------------
            '''

            batM2EM = (abs(self.GEOMETRY['Landing_Gear']['Relative Position X'] -\
                    self.GEOMETRY['PT6A - 67D L']['Relative Position X Eng']) +\
                    abs(self.GEOMETRY['PT6A - 67D L']['Relative Position Y Eng']) +\
                    self.GEOMETRY['PT6A - 67D L']['Relative Position Z Eng'] -\
                    self.GEOMETRY['Landing_Gear']['Relative Position Z'])*Lfus

            batF2batM = (abs(self.GEOMETRY['Landing_Gear']['Relative Position X'] -\
                 self.GEOMETRY['Cargo Box 4']['Relative Position X']) +\
                     abs(self.GEOMETRY['Landing_Gear']['Relative Position Z'] -\
                          self.GEOMETRY['Cargo Box 4']['Relative Position Z']))*Lfus

            batM2batA = (abs(self.GEOMETRY['Landing_Gear']['Relative Position X'] -\
                self.GEOMETRY['Cargo Box 1']['Relative Position X']) +\
                    abs(self.GEOMETRY['Landing_Gear']['Relative Position Z'] -\
                          self.GEOMETRY['Cargo Box 1']['Relative Position Z']))*Lfus

            Cable_lengths['DC_Cables'] = batM2EM + batF2batM + batM2batA
            Cable_lengths['AC_Cables'] = 0.02*Cable_lengths['DC_Cables']
            Cable_lengths['DC_HP_Cables'] = batM2EM
            Cable_lengths['Container_Cables'] = batF2batM + batM2batA

        if 'Series' in configuration and 'Parallel' not in configuration:

            '''
            -------------------------------------------------------------------
            Series Configuration
            -------------------------------------------------------------------
            '''

            batM2EM = (abs(self.GEOMETRY['Landing_Gear']['Relative Position X'] -\
                    self.GEOMETRY['PT6A - 67D L']['Relative Position X Eng']) +\
                    abs(self.GEOMETRY['PT6A - 67D L']['Relative Position Y Eng']) +\
                    self.GEOMETRY['PT6A - 67D L']['Relative Position Z Eng'] -\
                    self.GEOMETRY['Landing_Gear']['Relative Position Z'])*Lfus + self.GEOMETRY['Main_Wing']['Span']*0.75

            batF2batM = (abs(self.GEOMETRY['Landing_Gear']['Relative Position X'] -\
                 self.GEOMETRY['Cargo Box 4']['Relative Position X']) +\
                     abs(self.GEOMETRY['Landing_Gear']['Relative Position Z'] -\
                          self.GEOMETRY['Cargo Box 4']['Relative Position Z']))*Lfus

            batM2batA = (abs(self.GEOMETRY['Landing_Gear']['Relative Position X'] -\
                self.GEOMETRY['Cargo Box 1']['Relative Position X']) +\
                    abs(self.GEOMETRY['Landing_Gear']['Relative Position Z'] -\
                          self.GEOMETRY['Cargo Box 1']['Relative Position Z']))*Lfus

            Cable_lengths['DC_Cables'] = batM2EM + batF2batM + batM2batA
            Cable_lengths['AC_Cables'] = 0.02*Cable_lengths['DC_Cables']
            Cable_lengths['DC_HP_Cables'] = batM2EM
            Cable_lengths['Container_Cables'] = batF2batM + batM2batA

        self.cable_len = Cable_lengths

        return Cable_lengths
    
    def create_input_for_vsp(self):

        '''
        -------------------------------------------------------------------------------
        Write output file for OpenVSP

        OUTPUTS:
        aircraft_design2VSP.dat report
        -------------------------------------------------------------------------------
        '''

        with open("aircraft_design2VSP.dat", 'w+') as myfile:
            for key, item in self.GEOMETRY.items():
                myfile.write("Name={0}\n".format(key))
                for in_key, in_item in item.items():
                    myfile.write("{0}={1}\n".format(in_key, in_item))
                myfile.write("{0}={1}\n".format("Fuselage Length", self.GEOMETRY["Fuselage"]["Length"]))
                myfile.write("#########################################\n")
    
    def Extract_Design_Report(self, run):

        '''
        -------------------------------------------------------------------------------
        Extract design report

        OUTPUTS:
        Design_Report_run{i}.dat report
        -------------------------------------------------------------------------------
        '''

        with open('Design_Report.dat'.format(run), 'w') as fid:
            fid.write("====== Specifications ======\n")
            fid.write("Range                         [nmi] : %f\r\n" % self.DUMMY['RANGE'])
            fid.write("Reserves                      [nmi] : %f\r\n" % self.DUMMY['RESERVES'])
            fid.write("Actual range                  [nmi] : %f\r\n" % self.recalc_range)
            for key in self.single_points.keys():
                fid.write("Hybridization Degree " + key + " [-] : %f\r\n" % self.single_points[key]['HP'])
            fid.write("Battery Specific Energy     [kWh/kg] : %f\r\n" % self.EPS_INPUT_DICT['SE_Batt'])

            fid.write("====== Aircraft's General Characteristics ======\n")
            fid.write('Power to Weight Ratio                  [kW/kg]  : %f\r\n' % self.PW_ratio)
            for key in self.Wing_Loading.keys():
                fid.write('Actual Wing Loading @ ' + key + '      [kg/m^2] : %f\r\n' % (self.Wing_Loading[key]))
            for key in self.Lift2Drag_Detailed.keys():
                fid.write('L/D @ ' + key + '                       [-] : %f\r\n' % (self.Lift2Drag_Detailed[key]))

            fid.write('====== Final Design ======\n')
            for key in self.Weights_Level_3.keys():
                fid.write(key + ' Weight                          [kg] : %f\r\n' % self.Weights_Level_3[key])
            fid.write("PAX                                    [people] : %i\r\n" % self.DUMMY['PAX'])
            fid.write("Crew                                   [people] : %i\r\n" % self.DUMMY['CREW'])
            fid.write("Weight per PAX                         [kg/PAX] : %i\r\n" % self.DUMMY['WPAX'])

            fid.write('====== Mach Number Profile ======\n')
            for key in self.single_points.keys():
                fid.write("Mach Number " + key + "[-] : %f\r\n" % self.single_points[key]['M0'])

            fid.write('====== Flight Lane ======\n')
            for key in self.single_points.keys():
                fid.write("Flight Altitude " + key + "[m] : %f\r\n" % self.single_points[key]['ALT'])

            fid.write("====== Aircraft's Geometrical Characteristics ======\n")

            fid.write("====== Fuselage ======\n")
            fid.write('Fuselage length       [m]  : %f\r\n' % self.GEOMETRY['Fuselage']['Length'])
            fid.write('Fuselage max Diameter [m]  : %f\r\n' % self.GEOMETRY['Fuselage']['Max Diameter'])

            fid.write("====== Wing ======\n")
            fid.write('Aspect Ratio W        [-]  : %i\r\n' % self.GEOMETRY['Main_Wing']['AR'])
            fid.write('Wing area            [m^2] : %f\r\n' % self.GEOMETRY['Main_Wing']['Sref'])
            fid.write('Wing Span             [m]  : %f\r\n' % self.GEOMETRY['Main_Wing']['Span'])
            fid.write('Root Chord Wing       [m]  : %f\r\n' % self.GEOMETRY['Main_Wing']['Croot'])
            fid.write('Tip Chord Wing        [m]  : %f\r\n' % self.GEOMETRY['Main_Wing']['Ctip'])
            fid.write("Taper ratio W         [-]  : %f\r\n" % self.GEOMETRY['Main_Wing']['Taper'])
            fid.write('Sweep Wing            [deg]  : %f\r\n' % self.GEOMETRY['Main_Wing']['Sweep'])
            fid.write("Wing incidence       [deg] : %f\r\n" % self.GEOMETRY['Main_Wing']['Incidence'])
            fid.write("Wing twist           [deg] : %f\r\n" % self.GEOMETRY['Main_Wing']['Twist'])
            fid.write('M.A.C Wing            [m]  : %f\r\n' % self.GEOMETRY['Main_Wing']['Cmean']) 
            fid.write('M.A.C vert. loc. Wing [m]  : %f\r\n' % self.GEOMETRY['Main_Wing']['Ybar'])
            fid.write("Thickness to chord W  [-]  : %f\r\n" % self.GEOMETRY['Main_Wing']['Thickness'])
            fid.write("Oswald parameter      [-]  : %f\r\n" % self.GENERAL_INFO['Oswald'])
            fid.write("Wing relative position to fuselage : %f\r\n" % self.GEOMETRY['Main_Wing']['Relative Position X'])

            fid.write("====== Horizontal Tail ======\n")
            fid.write('Horizontal Tail Span  [m]  : %f\r\n' % self.GEOMETRY['Horizontal_Tail']['Span'])
            fid.write('Horizontal tail area [m^2] : %f\r\n' % self.GEOMETRY['Horizontal_Tail']['Sref'])
            fid.write('Aspect Ratio H        [-]  : %i\r\n' % self.GEOMETRY['Horizontal_Tail']['AR'])
            fid.write("Horizontal incidence [deg] : %f\r\n" % self.GEOMETRY['Horizontal_Tail']['Incidence'])
            fid.write('Root Chord Horizontal [m]  : %f\r\n' % self.GEOMETRY['Horizontal_Tail']['Croot'])
            fid.write('Tip Chord Horizontal  [m]  : %f\r\n' % self.GEOMETRY['Horizontal_Tail']['Ctip'])
            fid.write("Taper ratio H         [-]  : %f\r\n" % self.GEOMETRY['Horizontal_Tail']['Taper'])
            fid.write("Thickness to chord H  [-]  : %f\r\n" % self.GEOMETRY['Horizontal_Tail']['Thickness'])
            fid.write('Sweep Horizontal Tail [deg]  : %f\r\n' % self.GEOMETRY['Horizontal_Tail']['Sweep'])
            fid.write('MAC Horizontal Tail   [m]  : %f\r\n' % self.GEOMETRY['Horizontal_Tail']['Cmean']) 
            fid.write('Ybar Horizontal tail  [m]  : %f\r\n' % self.GEOMETRY['Horizontal_Tail']['Ybar'])
            fid.write("Horizontal Tail relative position to fuselage : %f\r\n" % self.GEOMETRY['Horizontal_Tail']['Relative Position X'])

            fid.write("====== Vertical Tail ======\n")
            fid.write('Vertical Tail Span    [m]  : %f\r\n' % self.GEOMETRY['Vertical_Tail']['Span'])
            fid.write('Vertical tail area   [m^2] : %f\r\n' % self.GEOMETRY['Vertical_Tail']['Sref'])
            fid.write('Aspect Ratio V        [-]  : %i\r\n' % self.GEOMETRY['Vertical_Tail']['AR'])
            fid.write('Root Chord Vertical   [m]  : %f\r\n' % self.GEOMETRY['Vertical_Tail']['Croot'])
            fid.write('Tip Chord Vertical    [m]  : %f\r\n' % self.GEOMETRY['Vertical_Tail']['Ctip'])
            fid.write("Taper ratio V         [-]  : %f\r\n" % self.GEOMETRY['Vertical_Tail']['Taper'])
            fid.write('M.A.C Vertical        [m]  : %f\r\n' % self.GEOMETRY['Vertical_Tail']['Cmean']) 
            fid.write('M.A.C loc Vertical    [m]  : %f\r\n' % self.GEOMETRY['Vertical_Tail']['Ybar'])
            fid.write('Sweep Vertical Tail   [deg]  : %f\r\n' % self.GEOMETRY['Vertical_Tail']['Sweep'])
            fid.write("Thickness to chord V  [-]  : %f\r\n" % self.GEOMETRY['Vertical_Tail']['Thickness'])
            fid.write("Vertical Tail relative position to fuselage : %f\r\n" % self.GEOMETRY['Vertical_Tail']['Relative Position X'])
        
        fid.close()

    def Extract_Weight_Report(self, my_dict, run):

        '''
        -------------------------------------------------------------------------------
        Extract weight report
        
        INPUTS:
        my_dict :    list of dictionaries
        run     :    case run

        OUTPUTS:
        Weight_Report_run{i}.dat report
        -------------------------------------------------------------------------------
        '''

        with open('Weight_Report.dat'.format(run), 'w') as fid:
            fid.write("====== Analytical Weight Report [kg] ======\n")
            for dictionary in my_dict:
                for key, item in dictionary.items():
                    fid.write(key + ':%f\r\n' %item)
        fid.close()