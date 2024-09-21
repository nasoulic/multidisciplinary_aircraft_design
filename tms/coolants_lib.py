class propylene_glycerol_solution(object):

    def __init__(self) -> None:
        '''
        ------------------------------------------------------------------
        Propylene glycerol solution
        ------------------------------------------------------------------
        '''
        self.name = "Propylene Glycerol"

    def define_solution(self, sol):
        '''
        ------------------------------------------------------------------
        Define coolant solution
        ------------------------------------------------------------------
        '''
        self.sol = sol
        self.name = self.name + " {0} %".format(sol)

    def specific_heat(self, T):

        '''
        ------------------------------------------------------------------
        Calculate specific heat of propylene glycol solution

        INPUTS:
        T   : [K] [required]        temperature

        OUTPUTS:
        specific heat [J/kgK]
        ------------------------------------------------------------------
        '''

        solution = [0, 10, 20, 30, 40, 50, 60]
        
        specific_heat_kj = [4.19, 4.1, 4.02, 3.9, 3.75, 3.57, 3.38]

        specific_heat = [i*1e3 for i in specific_heat_kj]

        index = 0
        if self.sol >= solution[-1]:
            index = -1
        for i in range(len(solution) - 1):
            if self.sol >= solution[i] and self.sol < solution[i + 1]:
                index = i
        
        if index > 0:
            cp = specific_heat[index] +\
                (specific_heat[index + 1] - specific_heat[index])*(self.sol - solution[index])/(solution[index + 1] - solution[index])
        else:
            cp = specific_heat[index]

        a = 0.038*self.sol/10 + 0.0162
        Cp = cp + a*(T - 273.15 - 20)

        self.Cp = Cp


    def dynamic_viscocity(self, T):

        '''
        ------------------------------------------------------------------
        Calculate dynamic viscocity of propylene glycol solution

        INPUTS:
        T   : [K] [required]        temperature

        OUTPUTS:
        dybamic viscocity [Pa*s]
        ------------------------------------------------------------------
        '''
        sol = self.sol
        if self.sol < 25:
            sol = 25
        if self.sol > 50:
            sol = 50

        temperature = {}
        viscocity = {}

        temperature['25'] = [   -9.704301075268816, -0.10752688172043179, 10.241935483870968, 20.026881720430104, 
                                30, 40.16129032258064, 49.94623655913979, 60.295698924731184, 70.08064516129032, 
                                80.05376344086021, 89.65053763440861, 100]
        viscocity['25'] = [ 9.625546898543513, 5.786699619144102, 3.7547898513364393, 2.585371876416969, 1.8415917900163623, 
                            1.4158358061785494, 1.0977808581382096, 0.8805446469056267, 0.7368911062284556, 0.6272226472624963, 
                            0.5570014857185542, 0.49885487114617794]

        temperature['30'] = [-13.27956989247312, -9.892473118279568, 0.08064516129032029, 9.865591397849464, 19.838709677419352, 
                            29.811827956989248, 39.97311827956989, 49.56989247311827, 59.91935483870968, 69.89247311827957, 
                            80.24193548387096, 89.83870967741936, 100]
        viscocity['30'] = [15.608823355413257, 12.842678685078823, 7.655576498619088, 4.7611996217486885, 3.195979990209649, 
                            2.2193442774516012, 1.6354150597131025, 1.2573248925511709, 1.0085170417662166, 0.8089449509498885, 
                            0.6885530159555427, 0.5860785152620888, 0.5248964853934742]

        temperature['35'] = [-18.172043010752688, -10.268817204301076, -0.48387096774193594, 10.053763440860216, 19.838709677419352, 
                            30, 40.34946236559139, 50.13440860215054, 60.10752688172043, 70.08064516129032, 79.86559139784946, 89.83870967741936, 100]
        viscocity['35'] = [28.261620048544934, 17.13506749763329, 9.957684899742663, 5.786699619144102, 3.7547898513364393, 2.585371876416969, 
                            1.8572767042082534, 1.3920229928900654, 1.0977808581382096, 0.9032357216605744, 0.7306679765549005, 0.6272226472624963, 0.5430085024385969]

        temperature['40'] = [   -22.876344086021504, -20.053763440860216, -9.892473118279568, -0.10752688172043179, 9.865591397849464, 
                                20.026881720430104, 30.564516129032256, 40.34946236559139, 50.13440860215054, 60.295698924731184, 70.08064516129032, 
                                80.24193548387096, 89.65053763440861, 100.18817204301075]
        viscocity['40'] = [55.22975444649673, 45.44211783690735, 22.669021838139855, 12.10243971995748, 7.214316839033491, 4.486768907786015, 
                            3.037418292116495, 2.182017328471222, 1.5675152922158277, 1.1949454125079844, 0.9503871430425469, 0.7623181849912408, 
                            0.6543919336673174, 0.5570014857185542]

        temperature['45'] = [-28.70967741935484, -19.865591397849464, -9.704301075268816, -0.10752688172043179, 10.053763440860216, 20.215053763440864, 
                            30, 40.16129032258064, 49.94623655913979, 60.483870967741936, 69.70430107526882, 80.24193548387096, 89.83870967741936, 100]
        viscocity['45'] = [122.5738394758897, 59.61043397833872, 28.989903998110744, 15.346299979049013, 8.842865141558987, 5.3614439233423585, 3.598897097143754, 
                            2.4780314503519794, 1.8106182256680863, 1.3342284672699594, 1.0522027863283416, 0.8297909471400268, 0.7003318331819237, 0.5860785152620888]

        temperature['50'] = [-34.543010752688176, -30.026881720430108, -20.053763440860216, -9.892473118279568, 0.26881720430107237, 9.865591397849464, 20.026881720430104, 
                            30.188172043010752, 40.34946236559139, 49.56989247311827, 60.10752688172043, 70.08064516129032, 80.05376344086021, 89.83870967741936, 100]
        viscocity['50'] = [303.7418292116494, 197.08759963575835, 79.53393796021595, 37.38901420435986, 18.970759334153588, 11.308551968075149, 6.627699347213656, 
                            4.192448839779903, 2.8623445844943256, 2.0737612148750952, 1.5281361956829747, 1.1453332267822025, 0.9186870351124716, 0.7368911062284556, 0.6063016723103778]

        for key, item in temperature.items():
            temperature[key] = [i + 273.15 for i in item]
            viscocity[key] = [j*1e-3 for j in viscocity[key]]

        index = 0
        if T >= temperature[str(int(sol))][-1]:
            index = -1
        for i in range(len(temperature[str(int(sol))]) - 1):
            if T >= temperature[str(int(sol))][i] and T < temperature[str(int(sol))][i + 1]:
                index = i

        if index > 0:
            mi = viscocity[str(int(sol))][index] +\
                (viscocity[str(int(sol))][index + 1] - viscocity[str(int(sol))][index])*(T - temperature[str(int(sol))][index])/(temperature[str(int(sol))][index + 1] - temperature[str(int(sol))][index])
        else:
            mi = viscocity[str(int(sol))][index]

        self.mi = mi

    def prandtl_number(self, T):

        Temp = [273, 278, 283, 293, 298, 303, 323, 348, 373] # [K]
        Prandtl = [13.6, 11.2, 9.46, 6.99, 6.13, 5.43, 3.56, 2.39, 1.76] # [-]

        index = 0
        if T >= Temp[-1]:
            index = -1
        for i in range(len(Temp) - 1):
            if T >= Temp[i] and T < Temp[i + 1]:
                index = i

        if index > 0:
            Pr = Prandtl[index] +\
                (Prandtl[index + 1] - Prandtl[index])*(T - Temp[index])/(Temp[index + 1] - Temp[index])
        else:
            Pr = Prandtl[index]

        self.Pr = Pr

    def thermal_conductivity(self, T):

        Temp_dt = [0.01, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99.6]

        Temp = [i + 273.15 for i in Temp_dt]

        thermal_conductivity = [555.75, 578.64, 598.03, 614.5, 628.56, 640.6,
                                650.91, 659.69, 667.02, 672.88, 677.03]

        index = 0
        if T >= Temp[-1]:
            index = -1
        for i in range(len(Temp) - 1):
            if T >= Temp[i] and T < Temp[i + 1]:
                index = i

        if index > 0:
            k = thermal_conductivity[index] +\
                (thermal_conductivity[index + 1] - thermal_conductivity[index])*(T - Temp[index])/(Temp[index + 1] - Temp[index])
        else:
            k = thermal_conductivity[index]

        self.k = k*1e-3


class air(object):
    
    def __init__(self) -> None:

        '''
        ------------------------------------------------------------------
        Air thermal properties
        ------------------------------------------------------------------
        '''

        self.name = "Air"

    def specific_heat(self, T):

        '''
        ------------------------------------------------------------------
        Calculate air specific heat

        INPUTS:
        T   : [K] [required]        temperature

        OUTPUTS:
        specific heat [J/kgK]
        ------------------------------------------------------------------
        '''

        Temp_dt = [ -213,-194,-192,-173,-153,-133,-113,-93.2,-73.2,-53.2,
                    -33.2,-13.2,0,6.9,15.6,26.9,46.9,66.9,86.9,107,127,
                    227,327,427,527,627,827,1227,1627]

        Temp = [i + 273.15 for i in Temp_dt]

        specific_heat = [1.901,1.933,1.089,1.04,1.022,1.014,1.011,1.008,1.007,1.006,
                        1.006,1.006,1.006,1.006,1.006,1.006,1.007,1.009,1.01,1.012,
                        1.014,1.03,1.051,1.075,1.099,1.121,1.159,1.21,1.241]

        index = 0
        if T >= Temp[-1]:
            index = -1
        for i in range(len(Temp) - 1):
            if T >= Temp[i] and T < Temp[i + 1]:
                index = i

        if index > 0:
            cp = specific_heat[index] +\
                (specific_heat[index + 1] - specific_heat[index])*(T - Temp[index])/(Temp[index + 1] - Temp[index])
        else:
            cp = specific_heat[index]

        self.Cp = cp*1e3

    def dynamic_viscocity(self, T):

        Temp_dt = [-75., -50., -25., -15., -10., -5.,
                    0., 5., 10., 15., 20., 25., 30., 40.,
                    50., 60., 80., 100., 125., 150., 175., 
                    200., 225., 300., 412., 500., 600., 700.,
                    800., 900., 1000., 1100.]

        Temp = [273.15 + i for i in Temp_dt] # [K]

        dyn_vis = [ 13.18, 14.56, 15.88, 16.4, 16.65, 16.9,
                    17.15, 17.4, 17.64, 17.89, 18.13, 18.37, 
                    18.6,  19.07, 19.53, 19.99, 20.88, 21.74, 
                    22.79, 23.8, 24.78, 25.73, 26.66, 29.28,
                    32.87, 35.47, 38.25, 40.85, 43.32, 45.66,
                    47.88, 50.01] # [-]

        index = 0
        if T >= Temp[-1]:
            index = -1
        for i in range(len(Temp) - 1):
            if T >= Temp[i] and T < Temp[i + 1]:
                index = i

        if index > 0:
            mi = dyn_vis[index] +\
                (dyn_vis[index + 1] - dyn_vis[index])*(T - Temp[index])/(Temp[index + 1] - Temp[index])
        else:
            mi = dyn_vis[index]

        self.mi = mi*1e-6

    def prandtl_number(self, T):

        Temp_dt = [-100., -50., 0., 25., 50., 100., 
                        150., 200., 250., 300.] 

        Temp = [273.15 + i for i in Temp_dt] # [K]

        Prandtl = [0.734, 0.72, 0.711, 0.707, 0.705, 
                   0.701, 0.699, 0.698, 0.699, 0.702] # [-]

        index = 0
        if T >= Temp[-1]:
            index = -1
        for i in range(len(Temp) - 1):
            if T >= Temp[i] and T < Temp[i + 1]:
                index = i

        if index > 0:
            Pr = Prandtl[index] +\
                (Prandtl[index + 1] - Prandtl[index])*(T - Temp[index])/(Temp[index + 1] - Temp[index])
        else:
            Pr = Prandtl[index]

        self.Pr = Pr

    def thermal_conductivity(self, T):

        Temp_dt = [ -190., -150., -100., -75., -50.,
                    -25., -15., -10., -5., 0., 5.,
                    10., 15., 20., 25., 30., 40., 50.,
                    60., 80., 100., 125., 150., 175.,
                    200., 225., 300., 412., 500., 600.,
                    700., 800., 900., 1000., 1100]

        Temp = [i + 273.15 for i in Temp_dt]

        thermal_conductivity = [7.82, 11.69, 16.2, 18.34,
                                20.41, 22.41, 23.2, 23.59, 23.97, 24.36,
                                24.74, 25.12, 25.5, 25.87, 26.24, 26.62, 
                                27.35, 28.08, 28.8, 30.23, 31.62, 33.33, 
                                35, 36.64, 38.25, 39.83, 44.41, 50.92,
                                55.79, 61.14, 66.32, 71.35, 76.26, 81.08, 
                                85.83]

        index = 0
        if T >= Temp[-1]:
            index = -1
        for i in range(len(Temp) - 1):
            if T >= Temp[i] and T < Temp[i + 1]:
                index = i

        if index > 0:
            k = thermal_conductivity[index] +\
                (thermal_conductivity[index + 1] - thermal_conductivity[index])*(T - Temp[index])/(Temp[index + 1] - Temp[index])
        else:
            k = thermal_conductivity[index]

        self.k = k*1e-3
