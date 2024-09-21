class cables(object):

    def __init__(self) -> None:        
        pass

    def cable_characteristics(self, J = 3.9e6, rho = 3100, cos_phi = 0.95):

        '''
        J:          Cable current flux [A/m]
        rho:        Cable material density [kg/m3]
        cos_phi:    AC power factor
        '''

        self.J = J               # cable current flux [A/m]
        self.rho = rho              # cable density [kg/m3]
        self.cos_phi = cos_phi          # ac power factor

    def dc_cable_sizing(self, P, V):

        i_dc = P*1000/V             # [A]
        A_dc = i_dc/self.J*1e6      # [mm2]

        m_dc = 2*self.rho*P*1000/(V*self.J)

        return m_dc, A_dc

    def ac_cable_sizing(self, P, V):

        i_ac = P*1000/(3**0.5*V*self.cos_phi)       # [A]
        A_ac = i_ac/self.J*1e6                      # [mm2]

        m_ac = 6**0.5*self.rho*P*1000/(V*self.J*self.cos_phi)

        return m_ac, A_ac