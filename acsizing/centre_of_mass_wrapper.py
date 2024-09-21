from acsizing.centre_of_mass import Center_of_Gravity
import pandas as pd

class getCoG():

    def __init__(self, aircraft):
        
        self.CoG = {}
        self.aircraft = aircraft

    def evaluate_CoG(self):

        self.aircraft_cog = Center_of_Gravity(self.aircraft)
        self.aircraft_cog.build_assembly()
        
        weights = {}
        weights["Fuselage"] = self.aircraft.mass_matrix["Aircraft"]["Fuselage"]
        weights["Main_Wing"] = self.aircraft.mass_matrix["Aircraft"]["Main_Wing"]
        weights["Horizontal_Tail"] = self.aircraft.mass_matrix["Aircraft"]["Horizontal_Tail"]
        weights["Vertical_Tail"] = self.aircraft.mass_matrix["Aircraft"]["Vertical_Tail"]
        weights["Landing_Gear"] = 0.85*self.aircraft.mass_matrix["Aircraft"]["Landing_Gear"] + 1/3*(self.aircraft.mass_matrix["Aircraft"]["Batteries"] + self.aircraft.mass_matrix["EPS"]["DC Cables"])

        weights["Engine"] = self.aircraft.mass_matrix["Aircraft"]["Installed_Engines"] + self.aircraft.mass_matrix["EPS"]["Motor"] + self.aircraft.mass_matrix["EPS"]["Inverter"] + self.aircraft.mass_matrix["EPS"]["AC Cables"]*2/3

        weights['Wing_Reinforcement'] = 0
        weights["Cockpit"] = self.aircraft.mass_matrix["Aircraft"]["Crew"]
        weights["Cabin"] = self.aircraft.mass_matrix["Aircraft"]["Payload"]
        weights["Cargo Box 1"] = 1/3*(self.aircraft.mass_matrix["Aircraft"]["Batteries"] + self.aircraft.mass_matrix["EPS"]["DC Cables"])
        weights["Cargo Box 2"] = self.aircraft.mass_matrix["TMS"]["Cooling System"]
        weights["Cargo Box 3"] = 0
        weights["Cargo Box 4"] = 0.15*self.aircraft.mass_matrix["Aircraft"]["Landing_Gear"] + 1/3*(self.aircraft.mass_matrix["Aircraft"]["Batteries"] + self.aircraft.mass_matrix["EPS"]["DC Cables"])
        weights["Duct"] = self.aircraft.mass_matrix["EPS"]["Generator"] + self.aircraft.mass_matrix["EPS"]["Converter"] + self.aircraft.mass_matrix["EPS"]["AC Cables"]*1/3 + self.aircraft.mass_matrix["EPS"]["DCDC"]
        weights["Else"] = self.aircraft.mass_matrix["Aircraft"]["Else"]
        weights["Fuel"] = self.aircraft.mass_matrix["Aircraft"]["Fuel"]

        self.aircraft_cog.CoG["Fuel"] = self.aircraft_cog.CoG["Main_Wing"]

        item_xloc = []
        item_mass = []
        it_nm = []
        for key, item in self.aircraft_cog.CoG.items():
            item_xloc.append(item["x"])
            item_mass.append(weights[key])
            it_nm.append(key)

        item_xloc, item_mass, it_nm = zip(*sorted(zip(item_xloc, item_mass, it_nm)))

        cases = ['Empty', 'Crew_No_Fuel', 'Loaded_No_Fuel',
                 'Crew_and_Fuel', 'Loaded_and_Fuel']
        xcg = []

        self.CoG = {}

        for case in cases:
            item_names = self.aircraft_cog.get_loading_scenario(self.aircraft_cog.CoG, case)
            case_cog, case_mass = self.aircraft_cog.calc_CoG(item_names, self.aircraft_cog.CoG, weights)
            xcg.append(case_cog[0])
            self.CoG.update( { case : { "mass" : case_mass, "CoG" : case_cog } } )

        self.most_aft = max(xcg)
        self.most_fwd = min(xcg)

        mass_distr = pd.DataFrame()
        mass_distr["name"] = it_nm
        mass_distr["xloc"] = item_xloc
        mass_distr["mass"] = item_mass
        mass_distr.to_csv("mass_distribution.csv")

        with open("CoG_report.dat", "w+") as myfile:
            myfile.write("{0}, {1}, {2}, {3}, {4} \n".format("Case", "Mass", "X", "Y", "Z"))
            for key, item in self.CoG.items():
                x, y, z = item["CoG"]
                myfile.write("{0}, {1}, {2}, {3}, {4} \n".format(key, item["mass"], x, y, z))
        myfile.close()
