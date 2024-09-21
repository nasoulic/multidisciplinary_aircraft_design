class component(object):

    def __init__(self) -> None:

        '''
        ------------------------------------------------------------------
        Call class constructor and initialize default values
        ------------------------------------------------------------------
        '''

        self.name = 'component'         # component name
        self.Tlim = 320.                # component limit temperature                   [K]
        self.Q = 1.                     # component thermal load                        [kW]
        self.A = 1.                     # component convection area                     [m2]
        self.h = 2.                     # convection coefficient                        [W/m2K]
        self.Tamb = 297.                # component's environment ambient temperature   [K]
        self.Tin = 280.                 # component cooling cycle inlet temperature     [K]
        self.Toper = 300.               # component operating temperature               [K]

    def add_name(self, name):

        '''
        ------------------------------------------------------------------
        Define component name
        ------------------------------------------------------------------
        '''

        self.name = name

    def add_thermal_attributes(self, Q, A, Tlim):

        '''
        ------------------------------------------------------------------
        Set component thermal attributes
        ------------------------------------------------------------------
        '''

        self.Q = Q
        self.A = A
        self.Tlim = Tlim
