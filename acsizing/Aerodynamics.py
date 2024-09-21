import numpy as np

class Aerodynamics():
    
    def __init__(self):

        '''
        -------------------------------------------------------------------------------
        Set file path for OpenVSP area properties
        -------------------------------------------------------------------------------
        '''

        self.path = './Aircraft/Area_Properties/' + 'Total.csv'
    

    def Read_area_properties(self):

        '''
        -------------------------------------------------------------------------------
        This function reads the extracted area properties of the as drawn aircraft from OpenVSP design.

        Areas that are extracted: 1. Fuselage Wetted Area
                                  2. Wing Wetted Area
                                  3. Horizontal Tail Wetted Area
                                  4. Vertical Tail Wetted Area
                                  5. Engine Nacelle Wetted Area
        -------------------------------------------------------------------------------
        '''

        with open(self.path, 'r') as f:
            data = f.readlines()

        f.close()

        S_Wetted = {}
        Volumes = {}

        for line in data:
            if "Comp_Name" in line:
                names = line.strip('\n').split(',')[1::]
            if 'Wet_Area' in line:
                values = line.strip('\n').split(',')[1::]
            if 'Theo_Vol' in line and 'Total' not in line:
                vpr = line.strip('\n').split(',')[1::]

        try:
            c = 0
            for name in names:
                S_Wetted.update( { name : float(values[c]) } )
                Volumes.update( { name : float(vpr[c]) } )
                c += 1
        except UnboundLocalError:
            vpr = []
            raise UnboundLocalError('Comp_Name or Wet_Area or Theo_Vol sections not found in .csv file. Check for corrupted file.')

        return S_Wetted, Volumes

    def Exp2Wet(self, t_c, Sexp):

        '''
        -------------------------------------------------------------------------------
        This function passes from the exposed area to wetted area if the first is known.

        Thickness is taken into cosideration as well.
        
        Wetted areas of wing and tail approximated from their planform.

        INPUTS:
        t_c  :                  thickness to chord ratio [-] 
        Sexp :                  exposed wing area [m2]

        OUTPUT:
        Swet :                  wetted area [m2]
        -------------------------------------------------------------------------------
        '''

        if t_c < 0.05:
            Swet = 2.003*Sexp
        else:
            Swet = (1.9997 + 0.52*t_c)*Sexp

        return Swet

    def Wet2Exp(self, t_c, Swet):

        '''
        -------------------------------------------------------------------------------
        This function passes from the wetted area to exposed area if the first is known.

        Thickness is taken into cosideration as well.

        Wetted areas of wing and tail approximated from their planform.

        INPUTS:
        t_c  :                  thickness to chord ratio [-] 
        Swet :                  wetted area [m2]

        OUTPUT:
        Sexp :                  exposed wing area [m2]
        -------------------------------------------------------------------------------
        '''

        if t_c < 0.05:
            Sexp = Swet/2.003
        else:
            Sexp = Swet/(1.9997 + 0.52*t_c)

        return Sexp

    def Lift_Curve_Slope(self, M, Dmax = None, Span = None, Sexp = None, Sref = None, AR = None, Sweep_max_t = None, Sweep_LE = None):

        '''
        -------------------------------------------------------------------------------
        This function calculates the lift curve slope for subsonic flight and ONLY for supersonic where M > 1 / cos(Λ.LE)

        INPUTS:
        
        For the supersonic condition, vars needed:

                                                    1. M (Mach Number)

                                                    2. Sweep.LE (Sweep Leading Edge)

        For the subsonic condition, vars needed:

                                                 1. M (Mach Number)

                                                 2. Dmax (Maximum diameter)

                                                 3. Span (Wing Span)

                                                 4. Sexp (Exposed Area)

                                                 5. Sref (Reference Area)

                                                 6. AR (Aspect Ratio)

                                                 7. Sweep.max.t (Sweep at maximum thickness)

        OUTPUTS:
        CLa : Lift curve slope coefficient
        -------------------------------------------------------------------------------
        '''

        if M < 0.85:
            # Subsonic lift curve slope
            F = 1.07*(1 + Dmax/Span)**2 # Eq. 12.9 Raymer
            if Sexp/Sref*F > 1:
                factor = 0.98
            else:
                factor = Sexp/Sref*F
            beta_sq = 1 - M**2 # Pradtl Correction
            eta = 0.95 # Airfoil efficiency according to Raymer
            CLa = 2*np.pi*AR/(2 + np.sqrt(4 + AR**2*beta_sq/eta**2*(1 + (np.tan(np.radians(Sweep_max_t)))**2/beta_sq)))*factor
        elif M > 1.2:
            # Supersonic lift curve slope
            if M > 1/np.cos(Sweep_LE):
                beta_sq = M**2 -1
                CLa = 4/np.sqrt(beta_sq)
            else:
                raise ValueError("Supersonic lift curve not available for condition where M < 1/cos(Λ_LE)! Please prefer computatinonal methods instead")
        else:
            # Transonic lift curve slope
            raise ValueError("Transonic region! Please prefer computatinonal methods instead")

        return CLa

    def Parasite_Drag(self, M, Fuselage, Main_Wing, Horizontal_Tail, Vertical_Tail, Engine, Landing_Gear, Wetted_areas, ftype = None, Raymer_correction = None):

        '''
        -------------------------------------------------------------------------------
        REQUIRED INPUTS:

        1. Mach Number (M)

        2. Fuselage Dictionary (fus_length and max diameter)

        3. Main Wing Disctionary (Reference area, Mean aerodynamic chord, Wing Thickness, Wing Sweep)

        4. Horizontal Tail Disctionary (Mean aerodynamic chord, Wing Thickness, Wing Sweep)

        5. Vertical Tail Disctionary (Mean aerodynamic chord, Wing Thickness, Wing Sweep)

        6. Engine dictionary (Diameter, Length)

        7. Landing Gear dictionary (Frontal Area)

        8. Wetted areas dictionary (Fuselage, Wing Reinforcement, Landing Gear, 
                                    Main Wing, Horizontal Tail, Vertical Tail, Engine)

        OPTIONAL INPUTS:

        ftype and Raymer_correction only for transonic and supersonic flight.

        ftype available options:
        
        1. 'Sears-Haack', 
        
        2. 'Blended Delta Wing',
        
        3. 'bomber',
        
        4. 'SST', 
        
        5. 'Poor Design', 
        
        6. 'F-15'.

        ftype default value: 
        
        3. 'bomber

        Raymer_correction available options: 
        
        1. True 
        
        2. False.

        Raymer_correction default value: 
        
        1. True


        OUTPUTS:

        CD0 : Parasite Drag [-]
        -------------------------------------------------------------------------------
        '''

        # Dictionaries breakdown
        Lf = Fuselage.get("Length")
        Dmax = Fuselage.get("Max Diameter")
        S_ref = Main_Wing.get("Sref")
        C_mean_w = Main_Wing.get("Cmean")
        t_c_w = Main_Wing.get("Thickness")
        Sweep_LE_w = Main_Wing.get("Sweep")
        C_mean_vt = Vertical_Tail.get("Cmean")
        t_c_vt = Vertical_Tail.get("Thickness")
        Sweep_C4_vt = Vertical_Tail.get("Sweep")
        C_mean_ht = Horizontal_Tail.get("Cmean")
        t_c_ht = Horizontal_Tail.get("Thickness")
        Sweep_C4_ht = Horizontal_Tail.get("Sweep")
        Leng = Engine.get("Engine Length")
        Davg = Engine.get("Engine Diameter")
        Sw_f = Wetted_areas.get("Fuselage") + Wetted_areas.get("Landing_Gear") + Wetted_areas.get("Wing_Reinforcement")
        Sw_w = Wetted_areas.get("Main_Wing")
        Sw_ht = Wetted_areas.get("Horizontal_Tail")
        Sw_vt = Wetted_areas.get("Vertical_Tail")
        Sw_eng = Wetted_areas.get("PT6A - 67D R")*2
        Afront = Landing_Gear.get("Frontal Area")

        # Component buildup method

        # Estimate parasite drag using flat-plate skin friction coefficient and form factors to fit to initial geometry
        # Interference factors taken into account as well

        if M < 0.85:
            case = "subsonic"
        elif M > 1.2:
            case = "supersonic"
        else:
            case = "transonic"

        # Fuselage
        Qf = 1
        cff = self.Friction_Coefficient(Lf, 'Smooth paint' , M, 'turbulent')
        FFf = self.Form_Factors('fuselage', l=Lf, d=Dmax)
        if case == "subsonic":
            cdf = cff*FFf*Qf*Sw_f/S_ref
        else:
            cdf = cff*Sw_f/S_ref

        u = 10 # 10 degrees upswept fuselage
        Amax = np.pi*Dmax**2/4
        D_qupsweep = 3.83*np.radians(u)**2.5*Amax
        cdupsweep = D_qupsweep/S_ref

        # Wing
        Qw = 1
        cfw = self.Friction_Coefficient(C_mean_w, 'Smooth paint', M, 'turbulent')
        FFw = self.Form_Factors('wing', t_c_w, 0.3, M, Sweep_LE_w)
        if case == "subsonic":
            cdw = cfw*FFw*Qw*Sw_w/S_ref
        else:
            cdw = cfw*Sw_w/S_ref

        # Vertical Tail
        Qvt = 1.05
        cfvt = self.Friction_Coefficient(C_mean_vt, 'Smooth paint', M, 'turbulent')
        FFvt = self.Form_Factors('wing', t_c_vt, 0.3, M, Sweep_C4_vt)
        if case == "subsonic":
            cdvt = Qvt*cfvt*FFvt*Sw_vt/S_ref
        else:
            cdvt = cfvt*Sw_vt/S_ref

        # Horizontal Tail
        Qht = 1.05
        cfht = self.Friction_Coefficient(C_mean_ht, 'Smooth paint', M, 'turbulent')
        FFht = self.Form_Factors('wing', t_c_ht, 0.3, M, Sweep_C4_ht)
        if case == "subsonic":
            cdht = Qht*cfht*FFht*Sw_ht/S_ref
        else:
            cdht = cfht*Sw_ht/S_ref

        # Engine Nacelles
        Qen = 1 # if positioned > 1 Diam
        cfen = self.Friction_Coefficient(Leng, 'Smooth paint', M, 'turbulent')
        FFen = self.Form_Factors('nacelle', l=Leng, d=Davg)
        if case == "subsonic":
            cdeng = Qen*cfen*FFen*Sw_eng/S_ref
        else:
            cdeng = cfen*Sw_eng/S_ref

        # Landing gear
        CDlg = 0.25 # from Table 12.6 'Regular wheel and tyre'
        D_qlg = CDlg*Afront
        cdlg = D_qlg/S_ref

        fac = 1.1 # leakage and protuberance drag Table 12.8 for prop AC
        if case == "subsonic":
            CD0 = fac*(cdf + cdw + cdvt + cdht + cdlg + cdeng + cdupsweep)
        else:
            if ftype == None:
                ftype = 'bomber'
            if Raymer_correction == None:
                Raymer_correction = True
            
            if ftype == "Sears-Haack":
                Ewd = 1
            elif ftype == "Blended Delta Wing":
                Ewd = 1.2
            elif ftype == "bomber" or ftype == "SST":
                Ewd = 2
            elif ftype == "Poor Design":
                Ewd = 2.7
            elif ftype == "F-15":
                Ewd = 2.9
            else:
                raise ValueError("Supersonic aircraft type not supported! Available options: 1. 'Sears-Haack', 2. 'Blended Delta Wing', 3. 'bomber', 4. 'SST', 5. 'Poor Design', 6. 'F-15' ")

            D_q_sears_haack = 9*np.pi/2*(Amax/Lf)**2
            if Raymer_correction:
                D_q_wave = Ewd*(1 - 0.2*(M - 1.2)**0.57*(1 - np.pi*Sweep_LE_w**0.77/100))*D_q_sears_haack
            else:
                D_q_wave = Ewd*(1 - 0.386*(M - 1.2)**0.57*(1 - np.pi*Sweep_LE_w**0.77/100))*D_q_sears_haack
            cd_wave = D_q_wave/S_ref

            CD0 = fac*(cdf + cdw + cdvt + cdht + cdlg + cdeng + cdupsweep + cd_wave)

        return CD0  

    def Friction_Coefficient(self, l, surface, M, ftype):

        '''
        -------------------------------------------------------------------------------
        Friction coefficient calculated according to flat-plate theory.

        For more detailed calculation refer to computational methods.

        INPUTS:
        l       :                   component length [m]
        surface :                   surface type
                                    Available options : 
                                                        1. 'Camouflage paint on aluminum', 
                                                        2. 'Smooth paint', 
                                                        3. 'Production sheet metal', 
                                                        4. 'Polished sheet metal', 
                                                        5. 'Smooth molded composite'
        M       :                   Mach number
        ftype   :                   Flow type           1. Laminar
                                                        2. Turbulent

        OUTPUTS:
        Cf      :                   Friction coefficient
        -------------------------------------------------------------------------------
        '''

        if surface == 'Camouflage paint on aluminum':
            k=1.015*10**-5
        elif surface == 'Smooth paint':
            k=0.634*10**-5
        elif surface == 'Production sheet metal':
            k=0.405*10**-5
        elif surface == 'Polished sheet metal':
            k=0.152*10**-5
        elif surface == 'Smooth molded composite':
            k=0.052*10**-5
        else:
            raise ValueError("Surface Type Not Found. Available options : 1. 'Camouflage paint on aluminum', 2. 'Smooth paint', 3. 'Production sheet metal', 4. 'Polished sheet metal', 5. 'Smooth molded composite' ")
        
        if M<=0.7:
            Recutoff=38.21*(l/k)**1.053
        else:
            Recutoff=44.62*(l/k)**1.053*M**1.16

        if ftype == 'laminar':
            Cf=1.328/np.sqrt(Recutoff)
        elif ftype == 'turbulent':
            Cf=0.455/(np.log10(Recutoff)**2.58*(1+0.144*M**2)**0.65)
        else:
            raise ValueError("Flow type not defined correctly. Either 'laminar' or 'turbulent' values are accepted")
        
        return Cf

    def Form_Factors(self,ftype,t_c=None,x_c=None,M=None,Sweepm=None,l=None,d=None):

        '''
        -------------------------------------------------------------------------------
        Form factors derived from empirical and theroetical data to correct the flat plate skin friction coefficient

        INPUTS:
        ftype   :           geometry type
                            Available options : 1. wing
                                                2. fuselage
                                                3. nacelle
        t_c     :           thickness to chord ratio
        x_c     :           max thickness position
        M       :           Mach number
        Sweepm  :           mean sweep angle
        l       :           length
        d       :           diameter

        REQUIRED INPUTS FOR ftype fuselage, nacelle
        1. ftype
        2. l
        3. d

        REQUIRED INPUTS FOR ftype wing
        1. ftype
        2. t_c
        3. x_c
        4. M
        5. Sweepm

        OUTPUTS:
        FF : Form factor [-]

        -------------------------------------------------------------------------------
        '''
        if ftype == 'wing':
            FF=(1+0.6*t_c/x_c+100*t_c**4)*(1.34*M**0.18*np.cos(np.radians(Sweepm))**0.28)
        elif ftype == 'fuselage':
            f=l/d
            FF=0.9+5/f**1.5+f/400
        elif ftype == 'nacelle':
            f=l/d
            FF=1+0.35/f
        else:
            raise ValueError("Geometry Type Not Found. Available options : 1. 'wing', 2. 'fuselage', 3. 'nacelle'")

        return FF

    def Windmilling_Drag(self, ftype, Afront, subtype = None, solidity = None):

        '''
        -------------------------------------------------------------------------------
        This function calculates the windmilling drag divided by the dynamic head for either a turboprop or turbojet engines.

        INPUTS:

        For the turboprop, mandatory arguments are: 
        
        1. ftype --type - 'prop'
                                                                          
        2. subtype -- supported types are: 
        
                        1. feathered 
        
                        2. unfeathered (if none, by default it is unfeathered)
                                                                                        
        3. solidity 
                                                                         
        4. Afront


        For the turbojet, mandatory arguments are: 
        
        1. ftype -- type - 'jet'
                                                                      
        2. Afront

        OUTPUTS:
        D_q : Windmilling drag divided by qinf = 1/2*rho*v**2 [m2]
        -------------------------------------------------------------------------------
        '''
        if ftype == "prop":
            if subtype == "feathered":
                factor = 0.1
            else:
                factor = 0.8
            D_q = factor*solidity*Afront
        elif ftype == "jet":
            D_q = 0.3*Afront
        else:
            D_q = []
            raise ValueError("Engine type not supported! Supported types are: 1. 'prop', 2. 'jet'")

        return D_q
