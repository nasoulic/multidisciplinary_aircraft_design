class battery_pack(object):

    def __init__(self) -> None:
        pass

    def pack_dimensions(self, pack2cellRatio = 0.86):

        '''
        -----------------------------------------------------------------
        Dimensions constants section
        -----------------------------------------------------------------
        '''

        self.pack2cell_ratio = pack2cellRatio                  # pack to cell ratio         [-]
        

    def cell_dimensions(self, h = 0.11, t = 0.01, w = 0.08, Vnom = 3.6,
                         Vmax = 4.12, eta1C = 0.9525, etaC2 = 0.976,
                         etaC3 = 0.984, etaC4 = 0.9885, etaC5 = 0.9915):

        '''
        -----------------------------------------------------------------
        Dimensions constants section
        -----------------------------------------------------------------
        '''

        self.cell_height = h                      # cell height                         [m]
        self.cell_thickness = t                   # cell thickness                      [m]
        self.cell_width = w                       # cell width                          [m]
        self.cell_V_nom = Vnom                    # cell nominal Voltage                [V]
        self.cell_V_max = Vmax                    # cell maxumum Voltage                [V]
        self.efficiency_1C = eta1C                # cell efficiency                     [-]
        self.efficiency_C2 = etaC2                # cell efficiency                     [-]
        self.efficiency_C3 = etaC3                # cell efficiency                     [-]
        self.efficiency_C4 = etaC4                # cell efficiency                     [-]
        self.efficiency_C5 = etaC5                # cell efficiency                     [-]

    def cell_efficiency(self, C):

        '''
        -----------------------------------------------------------------
        Interpolate to find battery efficiency according to C rate
        -----------------------------------------------------------------
        '''

        found = False
        
        efficiency = [self.efficiency_C5, self.efficiency_C4, self.efficiency_C3, self.efficiency_C2, self.efficiency_1C]
        c_rate = [1/5, 1/4, 1/3, 1/2, 1.]

        for i in range(len(c_rate) - 1):
            if not found:
                if C >= c_rate[i] and C <= c_rate[i + 1]:
                    found = True
                    eff = efficiency[i] + (efficiency[i + 1] - efficiency[i])*(C - c_rate[i])/(c_rate[i + 1] - c_rate[i])
            else:
                break
        
        if not found:
            eff = 0

        return eff



    def operating_constraints(self, DoD = 0.8, EoL = 0.2):
        
        '''
        -----------------------------------------------------------------
        Battery operating constraints section
        -----------------------------------------------------------------
        '''

        self.DOD = DoD
        self.aging = EoL

    def size_battery(self, P, E, Se, V, chrg_r, dis_r):

        '''
        -----------------------------------------------------------------
        INPUTS
        P       :           Pack power output                [kW]
        E       :           Pack capacity                    [kWh]
        Se      :           Cell gravimetric specific energy [kWh/kg]
        Sp      :           Cell gravimetric specific power  [kW/kg]
        V       :           Voltage output                   [V]
        chrg_r  :           Battery charge rate              [C]
        dis_r   :           Battery discharge rate           [C]
        -----------------------------------------------------------------
        '''

        Sv = 2*Se                                   # Volumetric scpecific energy [kWh/l]

        Vcell = self.cell_width*self.cell_thickness*self.cell_height*1e3

        E_cell = Sv*Vcell
        
        nseries = round(V/self.cell_V_max) + 1      # Number of batteries in series

        ncells = E/E_cell                           # Total batteries number

        nparallel = round(ncells/nseries) + 1       # Number of parallel batteries

        ncells = nseries*nparallel                  # New total number of batteries
        
        C_cell = E_cell/self.cell_V_nom*1e3         # Battery capacity [Ah]

        t_chrg = 60/chrg_r                          # Time to fully charge cell                     [min]
        t_dis = 60/dis_r                            # Time to fully discharge cell                  [min]
        Idc_bat_chrg = C_cell*chrg_r                # Maximum I DC battery cell charge current      [A]
        Idc_bat_dis = C_cell*dis_r                  # Maximum I DC battery cell discharge current   [A]

        Idc_inv_chrg = nparallel*Idc_bat_chrg       # Maximum pack charging current                 [A]
        Idc_inv_dis = nparallel*Idc_bat_dis         # Maximum pack discharging current              [A]

        self.chrg_eff = self.cell_efficiency(chrg_r)
        self.dis_eff = self.cell_efficiency(dis_r)

        Pchrg = V*Idc_inv_chrg*1e-3/self.chrg_eff        # Maximum pack charge power                     [kW]
        Pdis = V*Idc_inv_dis*1e-3*self.dis_eff           # Maximum pack discharge power                  [kW]

        Se_pack = Se*self.pack2cell_ratio*self.DOD*(1- self.aging)

        pack_mass = E/Se_pack

        if Pdis < P:
            # print('Maxumum Power Requirement exceeds maximum discharge Power')
            flag = 1
        else:
            flag = -1

        return pack_mass, nseries, nparallel, Pchrg, Pdis, t_chrg, t_dis, C_cell, Se_pack, flag

    def battery_sizing_LiFePO4(self, P, Pgt, mission_t, E, V, elmode, Se):

        from Li_Fe_PO4 import battery_cell

        '''
        -----------------------------------------------------------------
        INPUTS
        P           :           Pack power output profile        [kW]
        Pgt         :           Gas turbine generator power      [kW]
        mission_t   :           Mission profile duration         [min]
        E           :           Pack capacity                    [kWh]
        V           :           Voltage output                   [V]
        elmode      :           Phases in electric mode          [list]
        Se          :           Batteries Specific Energy        [kWh/kg]
        -----------------------------------------------------------------
        '''

        lifepo4 = battery_cell()

        E_cell = lifepo4.Vnom*lifepo4.Cnom/1e3

        ncells = E/E_cell                           # Total batteries number
        
        nseries = round(V/lifepo4.Vmax) + 1      # Number of batteries in series

        nparallel = round(ncells/nseries) + 1       # Number of parallel batteries

        V_cell = lifepo4.Vmax
        soc = 1.
        Vsys = V

        for phase in mission_t.keys():

            converged1 = False
            previous_soc = soc

            while not converged1:

                nseries_old = nseries
                nparallel_old = nparallel

                dt = mission_t[phase]/60
                power = P[phase]
                if Pgt > power:
                    if phase in elmode:
                        power = power
                    else:
                        Pchrg = Vsys*lifepo4.Cnom/3*nparallel*1e-3
                        if Pchrg <= abs(power - Pgt):
                            power = - Pchrg
                        else:
                            power = - abs(power - Pgt)
                else:
                    power = power - Pgt

                converged = False

                while not converged:

                    I_DC = power*1e3/Vsys
                    i_dc_cell = I_DC/nparallel
                    P_cell = i_dc_cell*V_cell
                    c_rate = lifepo4.cell_c_rate(i_dc_cell)
                    V_cell = lifepo4.get_Vcell_discharge(previous_soc, i_dc_cell)
                    P_cell_new = V_cell*i_dc_cell
                    Vsys = V_cell*nseries

                    if abs(P_cell - P_cell_new) < 1e-3:
                        converged = True
                    
                    if V_cell <= lifepo4.Vcut:
                        nparallel += 1

                soc = lifepo4.cell_soc(i_dc_cell, dt, previous_soc)

                if soc < 0.2:
                    nparallel += 1

                if abs(nseries - nseries_old) < 1 and abs(nparallel - nparallel_old) < 1:
                    converged1 = True                

        Se_pack = Se*self.pack2cell_ratio*self.DOD*(1- self.aging)

        pack_mass = E/Se_pack

        pchrg = Vsys*lifepo4.Cnom/3*nparallel*1e-3

        return pack_mass, nseries, nparallel, pchrg, lifepo4.Cnom, lifepo4.Vnom
