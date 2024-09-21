import numpy as np

class axial_flux_motor(object):

    def __init__(self):
        
        '''
        -----------------------------------------------------------------
        Initialize design variables
        -----------------------------------------------------------------
        '''

        self.dimensions_constants()
        self.magnets_constants()

    def dimensions_constants(self):

        '''
        -----------------------------------------------------------------
        Dimensions constants section
        -----------------------------------------------------------------
        '''

        self.bar_len_max = 0.4           # maximum EM length [m]
        self.bar_len_min = 0.03          # minimum EM length [m]
        self.rpm2omega = 2*np.pi/60      # convert rpm to rad/s
        self.tip_speed = 70              # maximum rotor tip speed [m/s]
        self.eps2acsizing_W_EM = 1e6     # minimum weight initial guess

    def magnets_constants(self):

        '''
        -----------------------------------------------------------------
        Magnets constants section
        -----------------------------------------------------------------
        '''

        self.nslots = 18                # number of slots
        self.npoles = 20                # number of poles
        self.Bmax_magnet = 1.45         # magnets N45 maximum flux density in [T]
        self.Bcore = 2.2                # stator core max magnetic flux [T]
        self.air_gap = 1e-3             # radial air
        self.Kfill = 0.65               # winding area to total area
        self.Kr = 0.67                  # stator diameters ratio
        self.Kgap = 0.9                 # magnet arc to full magnet pitch ratio
        self.nominal_operation = 1.2    # maximum to nominal operating condition factor
        self.T_wire_max = 180           # maxumum allowed T during nominal operating condition [K]
        self.T_coolant = 90             # maximum coolant take-off temparature (hot day) [K]
        self.Dtmax = self.T_wire_max - self.T_coolant
        self.wire_size = 0.002          # wire diameter
        self.iron_rho = 7800            # iron density [kg/m3]
        self.magnet_rho = 7400          # magnet density [kg/m3]
        self.resin_rho = 1550           # resin density [kg/m3]
        self.alu_rho = 2700             # aluminum density [kg/m3]
        self.k_al = 180                 # aluminum thermal conductivity [W/mK]
        self.k_resin = 1.8              # resin thermal conductivity [W/mK]
        self.heat_transf_coef = 3000    # heat transfer coefficient [W/m2K]
        self.alu_fin_thick = 0.008      # aluminum fin thickness [m]
        self.stack_limit = 5            #
        self.optimized = 0              #

    def size_motor(self, P, N, V):
        
        '''
        -----------------------------------------------------------------
        Start sizing routine

        INPUTS
        P   :           Power requirement [kW]
        N   :           Nominal rpm       [rpm]
        V   :           Maximum voltage   [V]

        OUTPUTS
        W_em    :       electric motor mass             [kg]
        W_cp_em :       coldplate electric motor mass   [kg]
        V_cp_em :       coldplate electric motor volume [m3]
        A_cp_em :       coldplate electric motor area   [m2]
        Tlim    :       coldplate T limit               [K]
        flag    :       return value 
        -----------------------------------------------------------------
        '''

        omega_target = 1.35*self.rpm2omega*N                                                 # Conversion of input parameter from rpm to rad/s
        torque_target = 1000*P*self.nominal_operation/omega_target                                                  # Torque target in Nm
        max_d = 2*self.tip_speed/omega_target                                                # Max allowable diameter due to rotating speed and tip speed considerations (m)
        Kslots = (max_d*np.pi - self.nslots*self.alu_fin_thick)/(max_d*np.pi)                  # Active to inactive materials ratio
        Bmax_g = self.Bmax_magnet*self.Kgap*(1 - (self.Kgap*self.Bmax_magnet/self.Bcore))
        if Kslots > 0:
            for bar_length in np.arange(self.bar_len_min, self.bar_len_max, 0.005):
                for Jmax in np.arange(5, 20.5, 0.5):
                    stacked = 0
                    real_torque = 0
                    Kslots = (max_d*np.pi - self.nslots*self.alu_fin_thick)/(max_d*np.pi)      # Active to inactive materials ratio
                    while real_torque < torque_target and stacked < self.stack_limit:
                        stacked += 1
                        real_torque = stacked*Kslots*np.pi/3*(max_d/2)**3*(1 - self.Kr**2)*(1 + self.Kr)*bar_length*Jmax*10**6*self.Kfill*Bmax_g    # calculation of torque in Nm
                    
                    real_torque = torque_target/stacked
                    for i in range(10):
                        d_target = 2*(real_torque/(stacked*Kslots*np.pi/3*(1 - self.Kr**2)*(1 + self.Kr)*bar_length*Jmax*10**6*self.Kfill*Bmax_g))**(1/3)
                        Kslots = (d_target*np.pi - self.nslots*self.alu_fin_thick)/(d_target*np.pi)     # Active to inactive materials ratio
                        if Kslots < 0:
                            break


                    flux = Bmax_g*np.pi/(4*self.npoles)*d_target**2*(1 - self.Kr**2)
                    frequency = omega_target*self.nominal_operation*self.npoles/(4*np.pi)
                    N1 = np.ceil(V/3**0.5/(4.44*frequency*0.5*self.npoles*flux))
                    I_target = 2**0.5*1.12*torque_target/(0.5*self.npoles*N1*self.nslots*self.Kfill*flux)/stacked
                    l_core_slot = flux*self.Kgap*self.npoles/self.nslots/((1 - self.Kr)/2*d_target*self.Bcore)       # thickness of core slot in m
                    A_slot = N1*I_target/Jmax/self.Kfill/10**6
                    slot_thickness = A_slot/(bar_length)
                    d_real = self.nslots*(2*slot_thickness + self.alu_fin_thick + l_core_slot)/np.pi
                    
                    # Calculation of internal dimensions
                    magnet_thickness = 0.015
                    l_shoe = 0.005
                    
                    l_backiron = flux*self.npoles/self.nslots/((1 - self.Kr)/2*d_target*self.Bcore)          # Backiron thickness in m
                    total_length = 2*(l_backiron + l_shoe + self.air_gap + magnet_thickness) + bar_length
                    A_cu_phase =  I_target/Jmax                                                              # Cross area of wire per phase in mm**2
                    parallel_wires = round(A_cu_phase/(np.pi*self.wire_size**2/4)/10**6)                      # number of copper wires in parallel
                    p_iron_kg = 0.95*(frequency/50)**2*(self.Bcore/self.nominal_operation)**2                # parameter of losses in stator per kg of iron
                    stator_iron_weight = ((1 - self.Kr**2)*(d_real/2)**2*2*l_shoe + (1 - self.Kr)*d_real/2*l_core_slot*self.nslots*bar_length)*self.iron_rho
                    wire_length_per_phase = 1.1*(self.nslots/3*(N1*bar_length*2 + np.pi*(4*A_cu_phase*10**( - 6)/np.pi)**0.5) + self.Kr*d_real*np.pi)   # total wire length per phase
                    R_phase_ref = 1.4*1.77*10**( - 8)*wire_length_per_phase/(A_cu_phase*10**( - 6))          # The resistance per phase of the wire in 20deg C temp (Ω)
                    R_phase = R_phase_ref*(1 + 0.00398*(self.T_wire_max - 20))                               # The resistance per phase of the wire at the maximum temp defined in constants section (Ω)
                    Q_wires = 3*R_phase*(I_target/self.nominal_operation)**2                                 # Losses produced inside the wires in total (W)
                    Q_iron_tot = p_iron_kg*stator_iron_weight                                                # Losses produced internally of the iron of the stator (W)
                    Q_stator = Q_iron_tot + Q_wires                                                          # Total losses contributed by the stator (W)
                    
                    
                    # Thermal resistances calculation of half a slot of stator
                    h_conv_coolant = self.heat_transf_coef
                    A_conv_coolant = self.Kr*d_real*np.pi*bar_length/self.nslots/2                                 # Area of convection of the coolant medium of half a slot (m**2)
                    R_th_conv_coolant = 1/(h_conv_coolant*A_conv_coolant)                               # thermal resistance of convection, medium side (K/W)
                    
                    h_conv_air = 160
                    A_conv_air = d_real*np.pi*bar_length/self.nslots/2                                        # Area of convection of the coolant medium of half a slot (m**2)
                    R_th_conv_air = 1/(h_conv_air*A_conv_air)                                           # thermal resistance of convection, medium side (K/W)
                    
                    t_base = 0.003                                                                      # thickness of cooling jacket in m
                    A_jacket = self.Kr*(d_real - 2*t_base)*np.pi*bar_length/self.nslots/2                          # area of conduction of the cooling jacket of half a slot (m**2)
                    R_th_cond_base = t_base/(A_jacket*self.k_al)                                             # thermal resistance of conduction for the jacket (K/W)
                    
                    t_fin = ((1 - self.Kr)/2*d_real)/2
                    A_fin = self.alu_fin_thick/2*bar_length
                    R_th_cond_fin = t_fin/(A_fin*self.k_al)
                    
                    slot_height = (1 - self.Kr)/2*d_real
                    slot_up_width = (d_real*np.pi - self.nslots*self.alu_fin_thick)/self.nslots
                    slot_down_width = self.Kr*slot_up_width
                    ratio_slot = (slot_up_width + slot_down_width)/2/slot_height
                    ratio_width = ratio_slot/(1 + ratio_slot)
                    ratio_height = 1/(1 + ratio_slot)
                    
                    t_resin = (A_slot*(1 - self.Kfill))/(2*2*(2*slot_height + slot_up_width + slot_down_width))
                    t_resin1 = t_resin/(1 + (ratio_height - 0.5)/0.5)                   # half of the equivalent thickness of the resin inside the slot (m)
                    A_resin1 = slot_height*bar_length                                   # area of conduction for the resin inside the slot (m**2)
                    R_th_cond_resin_side = t_resin1/(A_resin1*self.k_resin)                  # thermal resistance of conduction for the resin inside the slot (K/W)
                    t_resin2 = t_resin/(1 + (ratio_width - 0.5)/0.5)/2
                    A_resin2 = slot_down_width*bar_length
                    R_th_cond_resin_down = t_resin2/(A_resin2*self.k_resin)
                    A_resin3 = slot_up_width*bar_length
                    R_th_cond_resin_up = t_resin2/(A_resin3*self.k_resin)
                    
                    R_th_cond_insidedown = R_th_cond_fin + R_th_cond_resin_side + R_th_conv_coolant
                    R_th_cond_insideside = R_th_cond_base + R_th_cond_resin_down + R_th_conv_coolant
                    R_th_cond_insideup = R_th_conv_air + R_th_cond_resin_up
                    R_th_total_half_slot = 1/(1/R_th_cond_insidedown + 1/R_th_cond_insideside + 1/R_th_cond_insideup)   # total thermal resistance at half slot level (K/W)
                    R_th_total_st = R_th_total_half_slot/self.nslots/2                                                       # total thermal resistance of stator at motor level (K/W)
                    
                    DT_stator = R_th_total_st*Q_stator/stacked

                    magnet_weight = (1 - self.Kr**2)*(d_real/2)**2*magnet_thickness*self.magnet_rho*2                        # The magnet's weight (kg)
                    backiron_weight = (1 - self.Kr**2)*(d_real/2)**2*l_backiron*self.iron_rho*2                               # The weight of the backiron (kg)
                    cable_weight = parallel_wires*wire_length_per_phase*3*29.85/1000                                    # Weight of cables (kg) multiplying by 29.85 as it is the constant of weight (kg/km) for the wire size chosen
                    resin_weight = A_slot*(1 - self.Kfill)*bar_length*self.resin_rho*self.nslots                                   # Weight of the resin (kg)
                    alu_core_heatsink_weight = (self.Kr*d_real/2)*np.pi*0.02*(bar_length + 2*l_shoe)*self.alu_rho              # Weight of the core of the aluminum heatsink, a thickness of 20mm was chosen
                    alu_fins_heatsink_area = (1 - self.Kr)*d_real/2*self.alu_fin_thick*self.nslots                                 # Area in the stator assembly captured by the alu heatsink
                    alu_fins_heatsink_weight = alu_fins_heatsink_area*(bar_length)*self.alu_rho                          # Weight of the alu heatsink fins (kg)
                    alu_casing_weight = (np.pi*d_real*0.003*total_length + 2*np.pi*(d_real/2)**2*0.003)*self.alu_rho       # Weight of the casing of the motor, it is considered to be constructed out of 3mm of aluminum sheet (kg)
                    bearings_weight = 1/200*P*self.nominal_operation                                                          # Bearings weight (kg), a specific weight of 200kw/kg is considered
                    inside_diameter = self.Kr*d_real - 0.03 - 0.03                                                           # Outside  -  thickness of heatsink = 2*0.0015  -  thickness of bearings = 2*0.0015
                    alu_axle_weight = np.pi*inside_diameter*0.015*total_length*1.2*self.alu_rho                           # Weight of axle, an aluminum axle with a radial thickness of 0.015m is considered (kg)
                    core_area = (1 - self.Kr**2)*(d_real/2)**2*np.pi                                                          # Area of the stator core (m2)
                    real_Kslots = 1 - alu_fins_heatsink_area/core_area                                                  # Ratio of active core area to core area
                    total_weight = stacked*1.1*(magnet_weight + backiron_weight + cable_weight + resin_weight + alu_core_heatsink_weight + alu_fins_heatsink_weight + alu_casing_weight + bearings_weight + alu_axle_weight + stator_iron_weight)  #Total weight of the EM
                    if self.Dtmax > DT_stator and total_weight < self.eps2acsizing_W_EM:
                        self.eps2acsizing_W_EM  = total_weight
                        ideal_d = d_real
                        ideal_l = bar_length
                        ideal_Jmax = Jmax
                        ideal_DTmax = DT_stator
                        ideal_l_tot = total_length
                        out_alu_core_heatsink_weight = alu_core_heatsink_weight
                        out_alu_fins_heatsink_weight = alu_fins_heatsink_weight
                        ideal_stacked = stacked
                        self.optimized = 1

            if self.optimized > 0:
                eps2thermal_W_Coldplate_EM = ideal_stacked*0.5*(out_alu_core_heatsink_weight + out_alu_fins_heatsink_weight)
                eps2thermal_V_Coldplate_EM = ideal_stacked*0.5*(np.pi*self.Kr*ideal_d*0.01*(ideal_l + 0.03))*1000
                eps2thermal_A_Coldplate_EM = ideal_stacked*0.5*(2*np.pi*ideal_d**2/4 + np.pi*ideal_d*ideal_l_tot)
                eps2thermal_Tlimit_Coldplate_EM = self.T_coolant + 273
                flag = -1
            else:
                flag = 1

        else:
            flag = 1

        return [self.eps2acsizing_W_EM, eps2thermal_W_Coldplate_EM, eps2thermal_V_Coldplate_EM, eps2thermal_A_Coldplate_EM, eps2thermal_Tlimit_Coldplate_EM, flag]

# em = axial_flux_motor()
# res = em.size_motor(600, 2000, 1000)

# print('Specific power [kW/kg] : %f ' %(600/res[0]))