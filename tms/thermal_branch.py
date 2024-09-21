from scipy.optimize import fsolve
from tms.thermal_component import component

class thermal_branch_builder(object):

    def __init__(self) -> None:

        '''
        ------------------------------------------------------------------
        Call class constructor and initialize default values
        ------------------------------------------------------------------
        '''
        
        self.name = 'Default_branch'
        self.objs = []
        self.operating_conditions = []
        self.coolant_medium = None
        self.flow_conditions = []
        self.component_list = []

    def rename_branch(self, name):

        '''
        ------------------------------------------------------------------
        Define branch name
        ------------------------------------------------------------------
        '''

        self.name = name

    def add_component(self):

        '''
        ------------------------------------------------------------------
        Add branch component
        ------------------------------------------------------------------
        '''

        self.component = component()

        self.component_list.append(self.component)
        
    
    def check_inputs(self, objs):

        '''
        ------------------------------------------------------------------
        Check input validity

        INPUTS
        objs    [list]  [required]  A list of objects. Each object is a 
                                    component to be cooled
        ------------------------------------------------------------------
        '''

        for obj in objs:
            if obj.Tlim <= obj.Tin:
                raise ValueError("Component {2} Tlim : {0} is less than or equal to cooling cycle Tin {1}. Please check inputs...".format(obj.Tlim, obj.Tin, obj.name))
            if obj.Tlim <= obj.Tamb:
                print("Reverse heat transfer flow detected for free conveciton (component is heated instead of cooled by heat convection). Component {0}'s Tlim : {1} is less than or equal to rooms ambient temperature Tamb : {2}.".format(obj.name, obj.Tlim, obj.Tamb))

    def define_cooling_sequence(self, objs):

        '''
        ------------------------------------------------------------------
        Sort components in ascending Tlim order

        INPUTS
        objs    [list]  [required]  A list of objects. Each object is a 
                                    component to be cooled
        ------------------------------------------------------------------
        '''

        self.check_inputs(objs)

        component_temp = []
        component_name = []
        for obj in objs:
            component_temp.append(obj.Tlim)
            component_name.append(obj.name)

        component_temp, objs = zip(*sorted(zip(component_temp, objs)))
        self.objs = objs

    def forced_convection(self, hconv):

        '''
        ------------------------------------------------------------------
        Consider forced convection
        ------------------------------------------------------------------
        '''

        for obj in self.objs:
            obj.h = hconv

    def initial_guess(self):

        '''
        ------------------------------------------------------------------
        Form initial guess vector
        ------------------------------------------------------------------
        '''

        p = []
        for i in range(len(self.objs)):
            p.append(1e3 + i + 1)
            p.append(1e2 + i + 1)
        
        for i in range(len(self.objs) - 1):
            p.append(300 + i + 1)
        
        p.append(1.)
        return p


    def heat_transfer_equations(self, p):

        '''
        ------------------------------------------------------------------
        Build heat transfer equations system for branch

        INPUTS
        p   [list] [required]   Initial guess for each iteration
        ------------------------------------------------------------------
        '''

        msys = p[-1]
        temps = [self.objs[-1].Tlim]
        loads = []

        for i in range(len(self.objs) - 1):
            temps.append(p[-2 - i])

        temps.append(self.objs[0].Tin)

        for i in range(2*len(self.objs)):
            loads.append(p[i])

        temps = sorted(temps)

        self.branch_temperatures = temps

        eqns = []

        i = 0
        j = 0
        for obj in self.objs:
            self.coolant_medium.specific_heat(0.5*(temps[j + 1] + temps[j]))
            eqns.append(loads[i] - msys*self.coolant_medium.Cp*(temps[j + 1] - temps[j]))
            eqns.append(loads[i + 1] - obj.h*obj.A*(temps[j + 1] - obj.Tamb))
            eqns.append(obj.Q - loads[i] - loads[i + 1])
            i += 2
            j += 1

        return tuple(eqns)

    def solve_heat_transfer_equations(self, func2solve, init_vector):

        '''
        ------------------------------------------------------------------
        Solve non-linear heat transfer equation system

        INPUTS
        func2solve      [function or class method]  [required]  function or class method to be solved
        init_vector     [list]                      [required]  initial guess
        ------------------------------------------------------------------
        '''

        self.operating_conditions = fsolve(func2solve, init_vector)
        return -1
        
    def get_branch_flow_properties(self):

        msys = self.operating_conditions[-1]
        Tin = self.branch_temperatures[0]
        Tout = self.branch_temperatures[-1]
        self.coolant_medium.specific_heat(0.5*(Tin + Tout))
        cp = self.coolant_medium.Cp

        self.flow_conditions = [msys, cp, Tin, Tout]

        i = 1
        for obj in self.objs:
            obj.Toper = self.branch_temperatures[i]
            i += 1

    def add_coolant(self, coolant, sol = 1e10):

        '''
        ------------------------------------------------------------------
        Define coolant for each branch

        INPUTS
        coolant [class] [required]      Pass the coolant class as argument
        sol     [const] [optional]      If coolant is a solution define solution percentage
        ------------------------------------------------------------------
        '''

        self.coolant_medium = coolant()
        if sol < 1e10:
            self.coolant_medium.define_solution(sol)