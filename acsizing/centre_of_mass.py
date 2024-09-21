import numpy as np
from scipy import interpolate
from acsizing.naca_generator import naca

class Center_of_Gravity():

    def __init__(self, aircraft):
        self.aircraft_design = aircraft

    def build_assembly(self):

        '''
        ---------------------------------------------------------------------------------------------------------
        Returns the dictionary of all components' CoGs 
        ---------------------------------------------------------------------------------------------------------
        ''' 
        
        aircraft_inputs = self.aircraft_design.GEOMETRY

        CoG = {}
        Lf = aircraft_inputs['Fuselage']['Length']
        Dmax = aircraft_inputs['Fuselage']['Max Diameter']

        # Fusalage #
        CoG['Fuselage'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        fus_cog = self.fuselage_cog(Lf, Dmax, nslices = 50)
        CoG['Fuselage']['x'] = aircraft_inputs['Fuselage']['Relative Position X']*Lf + fus_cog[0]
        CoG['Fuselage']['y'] = 0 + fus_cog[1]
        CoG['Fuselage']['z'] = aircraft_inputs['Fuselage']['Relative Position Z']*Lf + fus_cog[2]

        # Landing Gear #
        CoG['Landing_Gear'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        l = aircraft_inputs['Landing_Gear']['Pod Length']
        rh = aircraft_inputs['Landing_Gear']['XS_Height']
        rw = aircraft_inputs['Landing_Gear']['XS_Width']
        
        lg_cog = self.reinforcement_cog(l, rh, rw, nslices = 50)
        CoG['Landing_Gear']['x'] = aircraft_inputs['Landing_Gear']['Relative Position X']*Lf + lg_cog[0]
        CoG['Landing_Gear']['y'] = 0 + lg_cog[1]
        CoG['Landing_Gear']['z'] = aircraft_inputs['Landing_Gear']['Relative Position Z']*Lf + lg_cog[2]

        # Wing Reinforcement #
        CoG['Wing_Reinforcement'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        l = aircraft_inputs['Wing_Reinforcement']['Pod Length']
        rh = aircraft_inputs['Wing_Reinforcement']['XS_Height']
        rw = aircraft_inputs['Wing_Reinforcement']['XS_Width']
        
        wr_cog = self.reinforcement_cog(l, rh, rw, nslices = 50)
        CoG['Wing_Reinforcement']['x'] = aircraft_inputs['Wing_Reinforcement']['Relative Position X']*Lf + wr_cog[0]
        CoG['Wing_Reinforcement']['y'] = 0 + wr_cog[1]
        CoG['Wing_Reinforcement']['z'] = aircraft_inputs['Wing_Reinforcement']['Relative Position Z']*Lf + wr_cog[2]

        # Main Wing #
        CoG['Main_Wing'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        span = aircraft_inputs['Main_Wing']['Span']
        croot = aircraft_inputs['Main_Wing']['Croot']
        ctip = aircraft_inputs['Main_Wing']['Ctip']
        sweep = aircraft_inputs['Main_Wing']['Sweep']
        twist = aircraft_inputs['Main_Wing']['Twist']
        incidence = aircraft_inputs['Main_Wing']['Incidence']
        root_af = 'NACA4415'
        tip_af = 'NACA4415'
        sec_chng = 1
        mwng_cog = self.wing_cog(span, croot, ctip, sweep, twist, incidence, root_af, tip_af, sec_chng, nslices = 50)
        CoG['Main_Wing']['x'] = aircraft_inputs['Main_Wing']['Relative Position X']*Lf + mwng_cog[0]
        CoG['Main_Wing']['y'] = 0 
        CoG['Main_Wing']['z'] = aircraft_inputs['Main_Wing']['Relative Position Z']*Lf + mwng_cog[2]

        # Horizontal Tail #
        CoG['Horizontal_Tail'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        span = aircraft_inputs['Horizontal_Tail']['Span']
        croot = aircraft_inputs['Horizontal_Tail']['Croot']
        ctip = aircraft_inputs['Horizontal_Tail']['Ctip']
        sweep = aircraft_inputs['Horizontal_Tail']['Sweep']
        twist = -1*aircraft_inputs['Horizontal_Tail']['Twist']
        incidence = aircraft_inputs['Horizontal_Tail']['Incidence']
        root_af = 'NACA0012'
        tip_af = 'NACA0012'
        sec_chng = 1
        mwng_cog = self.wing_cog(span, croot, ctip, sweep, twist, incidence, root_af, tip_af, sec_chng, nslices = 50)
        CoG['Horizontal_Tail']['x'] = aircraft_inputs['Horizontal_Tail']['Relative Position X']*Lf + mwng_cog[0]
        CoG['Horizontal_Tail']['y'] = 0 
        CoG['Horizontal_Tail']['z'] = aircraft_inputs['Horizontal_Tail']['Relative Position Z']*Lf + mwng_cog[2]

        # Vertical Tail #
        CoG['Vertical_Tail'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        span = aircraft_inputs['Vertical_Tail']['Span']
        croot = aircraft_inputs['Vertical_Tail']['Croot']
        ctip = aircraft_inputs['Vertical_Tail']['Ctip']
        sweep = aircraft_inputs['Vertical_Tail']['Sweep']
        twist = -1*aircraft_inputs['Vertical_Tail']['Twist']
        incidence = aircraft_inputs['Vertical_Tail']['Incidence']
        root_af = 'NACA0012'
        tip_af = 'NACA0012'
        sec_chng = 1
        mwng_cog = self.wing_cog(span, croot, ctip, sweep, twist, incidence, root_af, tip_af, sec_chng, nslices = 50)
        CoG['Vertical_Tail']['x'] = aircraft_inputs['Vertical_Tail']['Relative Position X']*Lf + mwng_cog[0]
        CoG['Vertical_Tail']['y'] = 0 
        CoG['Vertical_Tail']['z'] = aircraft_inputs['Vertical_Tail']['Relative Position Z']*Lf + mwng_cog[2] + mwng_cog[1]

        # Engine #
        CoG['Engine'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        l = aircraft_inputs['PT6A - 67D L']['Engine Length']
        d = aircraft_inputs['PT6A - 67D L']['Engine Diameter']
        eng_cog = aircraft_inputs['PT6A - 67D L']['COG_GT']
        CoG['Engine']['x'] = aircraft_inputs['PT6A - 67D L']['Relative Position X Eng']*Lf + eng_cog[0]
        CoG['Engine']['y'] = 0
        CoG['Engine']['z'] = aircraft_inputs['PT6A - 67D L']['Relative Position Z Eng']*Lf

        # Cockpit #
        CoG['Cockpit'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        nrows = 1
        w = aircraft_inputs['Cockpit']['Seat Width']*2 + aircraft_inputs['Cockpit']['Aisle Width']
        l = aircraft_inputs['Cockpit']['Seat Length']
        h = aircraft_inputs['Cockpit']['Seat Height']
        V1 = aircraft_inputs['Cockpit']['Seat Width']*l*h
        base_cog = self.box_cog(w, l, h)
        hb = 2*l
        lb = 0.1
        V2 = hb*lb*aircraft_inputs['Cockpit']['Seat Width']
        back_cog = self.box_cog(w, lb, hb)
        CoG['Cockpit']['x'] = aircraft_inputs['Cockpit']['Relative Position X']*Lf + 0.1 + l/2 + (V1*base_cog[0] + V2*(l - back_cog[0]))/(V1 + V2)
        CoG['Cockpit']['y'] = 0
        CoG['Cockpit']['z'] = 0 + (V1*base_cog[2] + V2*(h + back_cog[2]))/(V1 + V2)

        # Cabin #
        CoG['Cabin'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        nrows = int(aircraft_inputs['Cabin']['PAX']/2)
        p = aircraft_inputs['Cabin']['Seat Pitch']
        w = aircraft_inputs['Cockpit']['Seat Width']*2 + aircraft_inputs['Cockpit']['Aisle Width']
        l = aircraft_inputs['Cockpit']['Seat Length']
        h = aircraft_inputs['Cockpit']['Seat Height']
        V1 = aircraft_inputs['Cockpit']['Seat Width']*l*h
        base_cog = self.box_cog(w, l, h)
        hb = 2*l
        lb = 0.1
        V2 = hb*lb*aircraft_inputs['Cockpit']['Seat Width']
        back_cog = self.box_cog(w, lb, hb)
        xcg = (V1*base_cog[0] + V2*(l - back_cog[0]))/(V1 + V2)
        zcg = (V1*base_cog[2] + V2*(h + back_cog[2]))/(V1 + V2)
        xi = []
        for i in range(nrows):
            xi.append(i*p + xcg)
        
        CoG['Cabin']['x'] = aircraft_inputs['Cabin']['Relative Position X']*Lf + 0.1 + l/2 + sum(xi)/len(xi)
        CoG['Cabin']['y'] = 0
        CoG['Cabin']['z'] = 0 + zcg

        # Cargo Boxes #
        no_boxes = 4
        for i in range(no_boxes):
            CoG['Cargo Box {0}'.format(i + 1)] = { 'x' : 0, 'y' : 0, 'z' : 0 }
            w = aircraft_inputs['Cargo Box {0}'.format(i + 1)]['Box Width']
            l = aircraft_inputs['Cargo Box {0}'.format(i + 1)]['Box Length']
            h = aircraft_inputs['Cargo Box {0}'.format(i + 1)]['Box Height']
            box_cog = self.box_cog(w, l, h)
            CoG['Cargo Box {0}'.format(i + 1)]['x'] = aircraft_inputs['Cargo Box {0}'.format(i + 1)]['Relative Position X']*Lf + box_cog[0]
            CoG['Cargo Box {0}'.format(i + 1)]['y'] = 0
            CoG['Cargo Box {0}'.format(i + 1)]['z'] = 0 + box_cog[2]

        # Aft Duct #
        CoG['Duct'] = { 'x' : 0, 'y' : 0, 'z' : 0 }
        l = aircraft_inputs['Duct']['Chord']
        d = aircraft_inputs['Duct']['Diameter']
        box_cog = aircraft_inputs['Duct']['COG']
        CoG['Duct']['x'] = aircraft_inputs['Duct']['Relative Position X']*Lf + box_cog[0]
        CoG['Duct']['y'] = 0
        CoG['Duct']['z'] = 0 + box_cog[2]

        # All Else #
        CoG['Else'] = { 'x' : 0.4*Lf, 'y' : 0, 'z' : 0.5*Dmax }
        
        self.CoG = CoG


    def fuselage_cog(self, L, D, nslices):

        '''
        ---------------------------------------------------------------------------------------------------------
        Returns the local CoG of the fuselage, starting from the nose

        INPUTS:
        L       :                   fuselage length [m]
        D       :                   fuselage diameter [m]
        nslices :                   number of slices to split fuselage to

        OUTPUTS:
        cog [x, y, z] coordinates
        ---------------------------------------------------------------------------------------------------------
        ''' 

        xpoints = np.linspace(0, L, endpoint = True, num = nslices)

        xloc = []
        yloc = []
        zloc = []
        Ai = []

        for x in xpoints:

            if x <= 0.05494*L:
                
                rh = interpolate.interp1d([0, 0.05494*L], [0, D/(2.181652397*2)], kind = 'linear')
                rw = interpolate.interp1d([0, 0.05494*L], [0, D/(1.623772069*2)], kind = 'linear')
                z = interpolate.interp1d([0, 0.05494*L], [0, 0.00255*L], kind = 'linear')
                xloc.append(x)
                yloc.append(0)
                zloc.append(z(x))
                Ai.append(np.pi*rh(x)*rw(x))

            elif x <= 0.13546*L:

                rh = interpolate.interp1d([0.05494*L, 0.13546*L], [D/(2.181652397*2), D/2], kind = 'linear')
                rw = interpolate.interp1d([0.05494*L, 0.13546*L], [D/(1.623772069*2), D/2], kind = 'linear')
                z = interpolate.interp1d([0.05494*L, 0.13546*L], [0.00255*L, 0.01864*L], kind = 'linear')
                xloc.append(x)
                yloc.append(0)
                zloc.append(z(x))
                Ai.append(np.pi*rh(x)*rw(x))

            elif x <= 0.66117*L:

                rh = interpolate.interp1d([0.13546*L, 0.66117*L], [D/2, D/2], kind = 'linear')
                rw = interpolate.interp1d([0.13546*L, 0.66117*L], [D/2, D/2], kind = 'linear')
                z = interpolate.interp1d([0.13546*L, 0.66117*L], [0.01864*L, 0.02007*L], kind = 'linear')
                xloc.append(x)
                yloc.append(0)
                zloc.append(z(x))
                Ai.append(np.pi*rh(x)*rw(x))

            elif x <= 0.985*L:
                
                rh = interpolate.interp1d([0.66117*L, 0.985*L], [D/2, D/(5.960711928*2)], kind = 'linear')
                rw = interpolate.interp1d([0.66117*L, 0.985*L], [D/2, D/(8.901135409*2)], kind = 'linear')
                z = interpolate.interp1d([0.66117*L, 0.985*L], [0.02007*L, 0.04316*L], kind = 'linear')
                xloc.append(x)
                yloc.append(0)
                zloc.append(z(x))
                Ai.append(np.pi*rh(x)*rw(x))
            
            else:

                rh = interpolate.interp1d([0.985*L, L], [D/(5.960711928*2), 0], kind = 'linear')
                rw = interpolate.interp1d([0.985*L, L], [D/(8.901135409*2), 0], kind = 'linear')
                z = interpolate.interp1d([0.985*L, L], [0.04316*L, 0.04545*L], kind = 'linear')
                xloc.append(x)
                yloc.append(0)
                zloc.append(z(x))
                Ai.append(np.pi*rh(x)*rw(x))

        x_cg = sum(np.array(Ai)*np.array(xloc))/sum(np.array(Ai))
        y_cg = sum(np.array(Ai)*np.array(yloc))/sum(np.array(Ai))
        z_cg = sum(np.array(Ai)*np.array(zloc))/sum(np.array(Ai))

        return [x_cg, y_cg, z_cg]

    def wing_cog(self, b, c_root, c_tip, sweep, twist, incidence, root_airfoil, tip_airfoil, section_change, nslices):

        '''
        ---------------------------------------------------------------------------------------------------------
        Returns the local CoG of the half wing

        INPUTS:
        b               :                   wing span [m]
        c_root          :                   root chord [m]
        c_tip           :                   tip chord [m]
        sweep           :                   wing sweep [deg]
        twist           :                   wing twist [deg]
        incidence       :                   wing incidence [deg]
        root_airfoil    :                   airfoil type NACAXXXX
        tip_airfoil     :                   airfoil type NACAXXXX
        section_change  :                   spanwise percentage of airfoil change 
        nslices         :                   number of slices to split wing to

        OUTPUTS:
        cog [x, y, z] coordinates
        ---------------------------------------------------------------------------------------------------------
        '''

        delta_twist = interpolate.interp1d([0, b/2], [0, twist], kind = 'linear')
        chord = interpolate.interp1d([0, b/2], [c_root, c_tip], kind = 'linear')

        span = np.linspace(0, b/2, endpoint =  True, num = nslices)

        xloc = []
        yloc = []
        zloc = []
        Ai = []
        
        for y in span:
            theta = incidence + delta_twist(y)

            if y <= section_change*b/2:
                x_u, z_u, x_l, z_l, x4, z4 = self.airfoil_section(y, root_airfoil, chord, theta, sweep)
                y_u = np.ones((1, len(x_u)))*y
                y_l = y_u.copy()
                chord_line = interpolate.interp1d([x_u[1], x_u[-1]], [z_u[1], z_u[-1]], kind = 'linear')
                xloc.append(x4)
                yloc.append(y)
                zloc.append(z4)
                Ai.append(self.shoelace_formula(x_u, z_u) + self.shoelace_formula(x_l, z_l))
            else:
                x_u, z_u, x_l, z_l, x4, z4 = self.airfoil_section(y, tip_airfoil, chord, theta, sweep)
                y_u = np.ones((1, len(x_u)))*y
                y_l = y_u.copy()
                chord_line = interpolate.interp1d([x_u[1], x_u[-1]], [z_u[1], z_u[-1]], kind = 'linear')
                xloc.append(x4)
                yloc.append(y)
                zloc.append(z4)
                Ai.append(self.shoelace_formula(x_u, z_u) + self.shoelace_formula(x_l, z_l))

        x_cg = sum(np.array(Ai)*np.array(xloc))/sum(np.array(Ai))
        y_cg = sum(np.array(Ai)*np.array(yloc))/sum(np.array(Ai))
        z_cg = sum(np.array(Ai)*np.array(zloc))/sum(np.array(Ai))

        return [x_cg, y_cg, z_cg]

    def box_cog(self, w, l, h):

        '''
        ---------------------------------------------------------------------------------------------------------
        Returns the Center of Gravity for a given box

        INPUTS:
        w : box width [float]
        l : box length [float]
        h : box height [float]

        OUTPUTS:
        cog : [x , y, z]
        -------------------------------------------------------------------------------------------------------
        ''' 

        return [0.5*l, 0.5*w, 0.5*h]

    def engine_cog(self, l, d):

        '''
        ---------------------------------------------------------------------------------------------------------
        Returns the Center of Gravity of a tube

        INPUTS:
        d : tube diameter [float]
        l : tube length [float]

        OUTPUTS:
        cog : [x , y, z]
        -------------------------------------------------------------------------------------------------------
        ''' 

        return [0.5*l, 0.5*d, 0.5*d]

    def reinforcement_cog(self, L, rh, rw, nslices):

        '''
        ---------------------------------------------------------------------------------------------------------
        Returns the Center of Gravity of pod-shaped reinforcements

        INPUTS:
        L      : pod length [float]
        rh     : height diameter [list]
        rw     : width diameter [list]
        slices : number of slices [float]

        OUTPUTS:
        cog : [x , y, z]
        -------------------------------------------------------------------------------------------------------
        '''

        Ai = []
        xloc = []
        yloc = []
        zloc = []

        xpoints = np.linspace(0, L, endpoint = True, num = nslices)

        for x in xpoints:

            if x <= 0.25*L:

                r_h = interpolate.interp1d([0, 0.25*L], [rh[0]/2, rh[1]/2], kind = 'linear')
                r_w = interpolate.interp1d([0, 0.25*L], [rw[0]/2, rw[1]/2], kind = 'linear')
                xloc.append(x)
                yloc.append(0)
                zloc.append(0)
                Ai.append(np.pi*r_h(x)*r_w(x))

            elif x <= 0.5*L:
                
                r_h = interpolate.interp1d([0.25*L, 0.5*L], [rh[1]/2, rh[2]/2], kind = 'linear')
                r_w = interpolate.interp1d([0.25*L, 0.5*L], [rw[1]/2, rw[2]/2], kind = 'linear')
                xloc.append(x)
                yloc.append(0)
                zloc.append(0)
                Ai.append(np.pi*r_h(x)*r_w(x))

            elif x <= 0.75*L:
                
                r_h = interpolate.interp1d([0.5*L, 0.75*L], [rh[2]/2, rh[3]/2], kind = 'linear')
                r_w = interpolate.interp1d([0.5*L, 0.75*L], [rw[2]/2, rw[3]/2], kind = 'linear')
                xloc.append(x)
                yloc.append(0)
                zloc.append(0)
                Ai.append(np.pi*r_h(x)*r_w(x))

            else:
                
                r_h = interpolate.interp1d([0.75*L, 1.0*L], [rh[3]/2, rh[4]/2], kind = 'linear')
                r_w = interpolate.interp1d([0.75*L, 1.0*L], [rw[3]/2, rw[4]/2], kind = 'linear')
                xloc.append(x)
                yloc.append(0)
                zloc.append(0)
                Ai.append(np.pi*r_h(x)*r_w(x))

        x_cg = sum(np.array(Ai)*np.array(xloc))/sum(np.array(Ai))
        y_cg = sum(np.array(Ai)*np.array(yloc))/sum(np.array(Ai))
        z_cg = sum(np.array(Ai)*np.array(zloc))/sum(np.array(Ai))

        return [x_cg, y_cg, z_cg]


    def airfoil_section(self, y, profile, chord, theta, sweep):

        '''
        ---------------------------------------------------------------------------------------------------------
        Returns the airfoil section for given y coordinate

        INPUTS:
        y       :           spanwise airfoil position [m]
        profile :           airfoil profile NACAXXXX
        chord   :           airfoil chord [m]
        theta   :           airfoil rotation angle [deg]
        sweep   :           airfoil sweep [deg]

        OUTPUTS:
        x_u :               upper curve x coordinates
        z_u :               upper curve z coordinates
        x_l :               lower curve x coordinates             
        z_l :               lower curve z coordinates
        x4  :               quarter chord position x
        z4  :               quarter chord position z
        ---------------------------------------------------------------------------------------------------------
        ''' 

        numbers = profile.strip('NACA')
        M = int(float(numbers)/1000)
        P = int((float(numbers) - M*1000)/100)
        T = int(float(numbers) - M*1000 - P*100)

        root_profile = naca()
        root_profile.create_airfoil(int(numbers), spacing = 1)

        x_u = y*np.tan(np.radians(sweep)) + chord(y)*(root_profile.x_u*np.cos(np.radians(theta)) - root_profile.y_u*np.sin(np.radians(theta)))
        z_u = chord(y)*(root_profile.x_u*np.sin(np.radians(theta)) + root_profile.y_u*np.cos(np.radians(theta)))

        x_l = y*np.tan(np.radians(sweep)) + chord(y)*(root_profile.x_l*np.cos(np.radians(theta)) - root_profile.y_l*np.sin(np.radians(theta)))
        z_l = chord(y)*(root_profile.x_l*np.sin(np.radians(theta)) + root_profile.y_l*np.cos(np.radians(theta)))

        x4 = y*np.tan(np.radians(sweep)) + 0.25*chord(y)
        z4 = root_profile.get_camber4digit(M, P, alpha = 0, x = 0.25)
        
        return x_u, z_u, x_l, z_l, x4, z4

    def shoelace_formula(self, x, y):

        '''
        ---------------------------------------------------------------------------------------------------------
        Returns the area of an irregular polygon

        INPUTS: 
        x : list of x coordinates of polygon
        y : list of y coordinates of polygon

        OUTPUTS:
        area : area of polygon
        ---------------------------------------------------------------------------------------------------------
        ''' 

        sum1 = 0
        sum2 = 0

        for i in range(0, len(x) - 1):
            sum1 = sum1 + x[i]*y[i + 1]
            sum2 = sum2 + y[i]*x[i + 1]

        sum1 = sum1 + x[len(x) - 1]*y[0]
        sum2 = sum2 + x[0]*y[len(x) - 1]

        area = abs(sum1 - sum2)/2

        return area

    def calc_CoG(self, names, cogs, weights):

        '''
        ---------------------------------------------------------------------------------------------------------
        Returns CoG using the formula sum(ri*mi)/sum(mi)
        
        INPUTS: 
        names : list of strings
        cogs : dict
        weights : dict

        names list example:                 [ 'Fuselage', 'Box' ]

        cogs dictionary example:
                                            { 'Fuselage' : { 'x' : 0, 'y' : 0, 'z' : 0 },
                                              'Box'      : { 'x' : 1, 'y' : 1, 'z' : 1 },
                                              }

        weights dictionary example:
                                            { 'Fuselage' : 100,
                                              'Box'      : 10,
                                              }

        OUTPUTS:
        cog : [x , y, z]
        ---------------------------------------------------------------------------------------------------------
        ''' 

        Mx = []
        My = []
        Mz = []
        mass = []

        for name in names:
            mass.append(weights[name])
            Mx.append(cogs[name]['x']*weights[name])
            My.append(cogs[name]['y']*weights[name])
            Mz.append(cogs[name]['z']*weights[name])

        xloc = sum(Mx)/sum(mass)
        yloc = sum(My)/sum(mass)
        zloc = sum(Mz)/sum(mass)

        return [ xloc, yloc, zloc ], sum(mass)

    def get_loading_scenario(self, cogs, case):

        '''
        ---------------------------------------------------------------------------------------------------------
        Filters the parts to be included in the CoG calculation for each case

        INPUTS:
        cogs : dict [cog for each part]
        case : string [weight scenario]

        cogs dictionary example:
                                            { 'Fuselage' : { 'x' : 0, 'y' : 0, 'z' : 0 },
                                              'Box'      : { 'x' : 1, 'y' : 1, 'z' : 1 },
                                              }

        All Possible Weight Scenarios are: 
                                            1. Empty, 
                                            2. Crew_No_Fuel, 
                                            3. Loaded_No_Fuel, 
                                            4. Crew_and_Fuel, 
                                            5. Loaded_and_Fuel

        OUTPUTS:
        names : list of names
        ---------------------------------------------------------------------------------------------------------
        ''' 

        names = []
        for key in cogs.keys():
            names.append(key)
        
        if case == 'Empty':
            names.remove("Cockpit")
            names.remove("Cabin")
            names.remove("Fuel")
            names.remove("Cargo Box 3")
        elif case == 'Crew_No_Fuel':
            names.remove("Cabin")
            names.remove("Fuel")
            names.remove("Cargo Box 3")
        elif case == 'Loaded_No_Fuel':
            names.remove("Fuel")
            names.remove("Cargo Box 3")
        elif case == 'Crew_and_Fuel':
            names.remove("Cabin")
            names.remove("Cargo Box 3")
        elif case == 'Loaded_and_Fuel':
            names.remove("Cargo Box 3")
        else:
            raise ValueError('''
                            Weight Scenario not found! All Possible Weight Scenarios are: 
                                1. Empty, 
                                2. Crew_No_Fuel, 
                                3. Loaded_No_Fuel, 
                                4. Crew_and_Fuel, 
                                5. Loaded_and_Fuel
                                ''')

        return names      
