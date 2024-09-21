from acsizing.Stability_and_Control import Stability_and_Trim

class trimAnalysisWrapper():

    def __init__(self, aircraft, aircraft_CoG, home_dir, output_dir):
        self.aircraft_conf = aircraft
        self.aircraft_CoG = aircraft_CoG
        self.home_dir = home_dir
        self.output_dir = output_dir

    def evaluateTrim(self, configure_trim_angle, configure_trim_elevator):
        
        trim = Stability_and_Trim(self.aircraft_conf, self.home_dir, self.output_dir)
        flag = trim.trim_aircraft(self.aircraft_CoG.most_fwd, aircraft_angle = configure_trim_angle, df = configure_trim_elevator, CL_tot = trim.get_cruise_CL(), Cm_cg = 0)
        trim.make_trim_plot(self.aircraft_CoG.most_fwd, df = configure_trim_elevator, i_w = trim.i_w, i_ht = trim.i_ht)
