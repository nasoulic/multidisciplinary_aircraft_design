class flow_mix(object):
    def __init__(self) -> None:

        '''
        ------------------------------------------------------------------
        Thermodynamic mixing of flows
        ------------------------------------------------------------------
        '''

        pass
        
    def flow_mixing(self, branches):

        '''
        ------------------------------------------------------------------
        Apply thermodynamic mixing of multiple flows

        INPUTS
        branches [list] [required]  list of branch objects of which the flows will mix

        EXAMPLE
        my_branch_list = [branch1, branch2]

        the flow_mix().flow_mixing(my_branch_list) will mix the flows of the
        two branches.
        NOTE: branch1, and branch2 must have objs and operating_conditions
        as attributes
        ------------------------------------------------------------------
        '''
        
        T = []
        m_sys = []

        for branch in branches:
            T.append(branch.objs[-1].Tlim)
            m_sys.append(branch.operating_conditions[-1])

        T_mix = 0
        m_mix = 0

        for temp, mdot in zip(T, m_sys):
            T_mix = T_mix + (mdot*temp)
            m_mix = m_mix + mdot

        self.m_mix = m_mix
        self.T_mix = T_mix/m_mix