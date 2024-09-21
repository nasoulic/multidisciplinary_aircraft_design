from acsizing.Stability_and_Control import Stability_and_Trim
from acsizing.centre_of_mass_wrapper import getCoG

class getStaticMargin():

    def __init__(self, aircraft, home_dir, output_dir):
        self.aircraft_conf = aircraft
        self.isStable = False
        self.iterCount = 0
        self.staticMargin = 1e-10
        self.home_dir = home_dir
        self.output_dir = output_dir

    def evaluate_stability(self, SMThreshold):

        x_wing = self.aircraft_conf.GEOMETRY["Main_Wing"]["Relative Position X"]
        fuselage_length = self.aircraft_conf.GEOMETRY["Fuselage"]["Length"]
        horizontal_tailarm = self.aircraft_conf.GEOMETRY["Fuselage"]["Horizontal Tailarm"]
        vertical_tailarm = self.aircraft_conf.GEOMETRY["Fuselage"]["Vertical Tailarm"]
        ht_croot = self.aircraft_conf.GEOMETRY["Horizontal_Tail"]["Croot"]
        vt_croot = self.aircraft_conf.GEOMETRY["Vertical_Tail"]["Croot"]
        w_croot = self.aircraft_conf.GEOMETRY["Main_Wing"]["Croot"]
        x_lg = self.aircraft_conf.GEOMETRY["Landing_Gear"]["Relative Position X"]
        x_wr = self.aircraft_conf.GEOMETRY["Wing_Reinforcement"]["Relative Position X"]

        # Eval stability
        while not self.isStable:

            x_wr = x_wing - 0.04
            x_eng = x_wing - 0.04
            x_prop = x_eng + 0.0366
            x_ht = x_wing + (horizontal_tailarm - 0.25*ht_croot)/fuselage_length
            x_vt = x_wing + (vertical_tailarm - 0.25*vt_croot - 0.25*w_croot)/fuselage_length

            # Overwrite ititial values
            self.aircraft_conf.GEOMETRY["Main_Wing"]["Relative Position X"] = x_wing
            self.aircraft_conf.GEOMETRY["PT6A - 67D L"]["Relative Position X Eng"] = x_eng
            self.aircraft_conf.GEOMETRY["PT6A - 67D R"]["Relative Position X Eng"] = x_eng
            self.aircraft_conf.GEOMETRY["PT6A - 67D L"]["Relative Position X Prop"] = x_prop
            self.aircraft_conf.GEOMETRY["PT6A - 67D R"]["Relative Position X Prop"] = x_prop
            self.aircraft_conf.GEOMETRY["Horizontal_Tail"]["Relative Position X"] = x_ht
            self.aircraft_conf.GEOMETRY["Vertical_Tail"]["Relative Position X"] = x_vt
            self.aircraft_conf.GEOMETRY["Landing_Gear"]["Relative Position X"] = x_lg
            self.aircraft_conf.GEOMETRY["Wing_Reinforcement"]["Relative Position X"] = x_wr

            aircraft_cog = getCoG(self.aircraft_conf)
            aircraft_cog.evaluate_CoG()

            aircraft_stability = Stability_and_Trim(self.aircraft_conf, self.home_dir, self.output_dir)
            self.staticMargin = aircraft_stability.Static_Margin(aircraft_cog.most_aft)*100

            if self.staticMargin >= SMThreshold:
                self.isStable = True
            else:
                x_wing = x_wing + 0.01
                x_lg = x_lg - 0.01
                horizontal_tailarm = horizontal_tailarm - 0.01*fuselage_length
                vertical_tailarm = vertical_tailarm - 0.01*fuselage_length

            if self.iterCount > 20:
                self.isStable = True

            self.iterCount += 1

    def overwrite_vsp_input_file(self):

        with open("./vsp_aircraft_input_file.dat", "w+") as f:
            for key, item in self.aircraft_conf.GEOMETRY.items():
                f.write("Name={0}\n".format(key))
                for inkey, initem in item.items():
                    f.write("{1}={0}\n".format(initem, inkey))
                f.write("Fuselage Length={0}\n".format(self.aircraft_conf.GEOMETRY["Fuselage"]["Length"]))
                f.write("#########################################\n")
        f.close()

    def exportStaticMaringReport(self):

        with open("./static_margin.dat", "w+") as myfile:
            myfile.write("{0}, {1}\n".format("Static Margin", self.staticMargin))
            myfile.write("Static Margin {0} reached after {1} iterations.\n".format(self.staticMargin, self.iterCount))
        myfile.close()