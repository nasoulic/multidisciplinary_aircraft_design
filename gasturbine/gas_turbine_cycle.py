from gasturbine.ambient_conditions import ambient_conditions
from gasturbine.intake import intake
from gasturbine.pressure_drop import pressure_drop
from gasturbine.compressor import compressor
from gasturbine.burner import burner
from gasturbine.turbine import turbine
from gasturbine.power_turbine import power_turbine
from gasturbine.nozzle import nozzle
from gasturbine.properties import air_properties, kerosene_properties
from gasturbine.propeller import Propeller
from gasturbine.compressor_map import map_builder
from gasturbine.map_scaling import Map_Scaling
from gasturbine.gas_properties import gas_properties
import matplotlib.pyplot as plt
import numpy as np

class gas_turbine_cycle_builder():
    
    def __init__(self, gen_inps):
        self.LHV = gen_inps["Hf"]*1e6
        self.intake_nis = gen_inps["ninlet"]
        self.intake_dp = gen_inps["delta_P_intake"]
        self.hpc_eta_poly = 0.83 # calculated from map
        self.comp_dp = gen_inps["delta_P_c"]
        self.turbine_dp = gen_inps["delta_P_T"]
        self.eta_burner = gen_inps["ncc"]
        self.comb_dp = gen_inps["delta_P_CC"]
        self.bleed_air = gen_inps["bleed"]
        self.eta_mech_hpt = gen_inps["nmech_HPS"]
        self.hpt_eta_poly = gen_inps["nHPT_pol"]
        self.eta_mech_lpt = gen_inps["nmech_LPS"]
        self.lpt_eta_poly = gen_inps["nLPT_pol"]
        self.eta_nozzle = gen_inps["nn"]
        self.eta_gearbox = gen_inps["ngb"]
        self.eta_adiabatic_pt = gen_inps["nPT"]
        self.eta_mech_pt = gen_inps["nmech_PS"]
        self.nozzle_dp = gen_inps["delta_P_N"]
    
    def load_design_point(self, design_parms, name):
        self.name = "{0}_design_point".format(name)
        self.TET = design_parms["TET"]
        self.mair = design_parms["mc"]
        self.alt = design_parms["Alt"]
        self.vinf = design_parms["Vinf"]
        self.PR = design_parms["PR"]
        self.PR_lpc = design_parms["LPC_PR"]
        self.PR_hpc = self.PR/self.PR_lpc
        
        propeller_map = Propeller()
        propeller_map.load_nprop_points()
        
        self.eta_propeller = propeller_map.propeller_eff(self.vinf)        
    
    def define_working_media(self):
        
        self.air_data = air(air_properties)
        self.fuel_data = fuel(kerosene_properties)
        self.fuel_data.LHV = self.LHV
    
    def open_brayton_cycle(self):
        
        m0, To0, Po0, ho0, So0 = ambient_conditions(self.mair, self.alt, self.vinf)        
        m1, To1, Po1, ho1, So1 = intake(self.intake_nis, [Po0, To0, m0, So0])        
        m2, To2, Po2, ho2, So2 = pressure_drop(self.intake_dp, [Po1, To1, m1, So1], cold = True)        
        
        lpc_ref_map = map_builder()
        lpc_ref_map.navigate_to_path(["gasturbine", "component_maps", "lpc_centrifugal"])
        lpc_ref_map.get_ref_info()
        lpc_ref_map.build_map('surge_line.map', 'rpm_lines.map', ["70eff.map", "75eff.map", "80eff.map", "82eff.map"], 100)
        lpc_ref_map.reset_path()
        
        lpc_scaled_map = Map_Scaling(lpc_ref_map)
        lpc_scaled_map.scale_map(self.PR_lpc, "centrifugal")
        
        wc_new_lpc = self.mair/lpc_ref_map.mc*np.sqrt(To2/lpc_ref_map.Tin)/(Po2/lpc_ref_map.Pin)
        
        lpc_eta_is, rpm_lpc = lpc_scaled_map.find_point_on_map(wc_new_lpc, self.PR_lpc)
        gas_props = gas_properties()
        cp = gas_props.cp_cold(To2)
        gamma = gas_props.gamma(cp, gas_props.R_cold)
        lpc_scaled_poly = (gamma - 1)/gamma*np.log(self.PR_lpc)/(np.log((self.PR_lpc**((gamma - 1)/gamma) - 1)/lpc_eta_is + 1))
           
        m3, To3, Po3, ho3, So3 = compressor(lpc_scaled_poly, self.PR_lpc, [Po2, To2, m2, So2])        
        m4, To4, Po4, ho4, So4 = pressure_drop(self.comp_dp, [Po3, To3, m3, So3], cold = True)
        
        hpc_ref_map = map_builder()
        hpc_ref_map.navigate_to_path(["gasturbine", "component_maps", "hpc_centrifugal"])
        hpc_ref_map.get_ref_info()
        hpc_ref_map.build_map("surge_line.map", "rpm_lines.map", ["eff65.map", "eff70.map", "eff75.map", "eff80.map", "eff82.map", "eff84.map", "eff86.map"], 100)
        hpc_ref_map.reset_path()
        
        hpc_scaled_map = Map_Scaling(hpc_ref_map)
        hpc_scaled_map.scale_map(self.PR_hpc, "centrifugal")
        
        wc_hpc_new = self.mair/hpc_ref_map.mc*np.sqrt(To4/hpc_ref_map.Tin)/(Po4/hpc_ref_map.Pin)
        
        hpc_eta_is, rpm_hpc = hpc_scaled_map.find_point_on_map(wc_hpc_new, self.PR_hpc)
        cp = gas_props.cp_cold(To4)
        gamma = gas_props.gamma(cp, gas_props.R_cold)
        hpc_scaled_poly = (gamma - 1)/gamma*np.log(self.PR_hpc)/(np.log((self.PR_hpc**((gamma - 1)/gamma) - 1)/hpc_eta_is + 1))
        
        m5, To5, Po5, ho5, So5 = compressor(hpc_scaled_poly, self.PR_hpc, [Po4, To4, m4, So4])
        m6, To6, Po6, ho6, So6, far, q = burner(self.eta_burner, self.TET, self.comb_dp, self.fuel_data.LHV, self.bleed_air, [Po5, To5, m5, So5])
        m7, To7, Po7, ho7, So7, nt_is_hpt, PRt_hpt, delta_h_hpt = turbine(far, ho5 - ho4, self.eta_mech_hpt, self.hpt_eta_poly, self.bleed_air, [Po6, To6, m6, So6])
        m8, To8, Po8, ho8, So8 = pressure_drop(self.turbine_dp, [Po7, To7, m7, So7], cold = False, far = far)
        m9, To9, Po9, ho9, So9, nt_is_lpt, PRt_lpt, delta_h_lpt = turbine(far, ho3 - ho2, self.eta_mech_lpt, self.lpt_eta_poly, self.bleed_air, [Po8, To8, m8, So8])
        m10, To10, Po10, ho10, So10 = pressure_drop(self.turbine_dp, [Po9, To9, m9, So9], cold = False, far = far)
        m11, To11, Po11, ho11, So11, PRpt, Dh_pt, l_opt, delta_h_avg_pt = power_turbine(Po0, To0, far, self.bleed_air, [Po10, To10, m10, So10], self.vinf, self.eta_nozzle, self.eta_propeller, self.eta_gearbox, self.eta_adiabatic_pt, self.eta_mech_pt)
        m12, To12, Po12, ho12, So12 = pressure_drop(self.nozzle_dp, [Po11, To11, m11, So11], cold = False, far = far)
        m13, To13, Po13, ho13, So13, vjet, pr_noz = nozzle(far, Po0, To0, self.eta_nozzle, l_opt, delta_h_avg_pt, [Po12, To12, m12, So12])
        
        self.entropy = [So0, So1, So2, So3, So4, So5, So6, So7, So8, So9, So10, So11, So12, So13]
        self.enthalpy = [ho0, ho1, ho2, ho3, ho4, ho5, ho6, ho7, ho8, ho9, ho10, ho11, ho12, ho13]
        self.pressure = [Po0, Po1, Po2, Po3, Po4, Po5, Po6, Po7, Po8, Po9, Po10, Po11, Po12, Po13]
        self.temperature = [To0, To1, To2, To3, To4, To5, To6, To7, To8, To9, To10, To11, To12, To13]
        self.mass_flow = [m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12, m13]
        
        mf = (1 - self.bleed_air)*far*self.mair
        mgas = ((1 - self.bleed_air)*(1 + far) + self.bleed_air)*self.mair
        mb = self.bleed_air*self.mair
        jet_thrust = mgas*vjet - self.mair*self.vinf
        thrust_prop = mgas*self.eta_propeller*self.eta_gearbox*self.eta_mech_pt*self.eta_adiabatic_pt*l_opt*delta_h_avg_pt/self.vinf
        thrust = jet_thrust + thrust_prop
        P_jet = jet_thrust*self.vinf
        P_prop = thrust_prop*self.vinf
        P_shaft = P_prop/self.eta_propeller
        P_eshaft = P_jet + P_shaft
        bsfc = mf*3.6e6/P_eshaft
        
        self.bsfc = bsfc
        self.mfuel = mf
        self.equivalent_shaft_power = P_eshaft
        self.shaft_power = P_shaft
        self.jet_thrust = jet_thrust
        self.propeller_thrust = thrust_prop
        self.total_thrust = thrust
        
    def export_design_report(self):

        data = {
            "Turbine Inlet Temperature [K]" : self.temperature[6],
            "Inter-Turbine Temperature [K]" : self.temperature[8],
            "BSFC [g/(kWh)]" : self.bsfc*1e3,
            "Jet Thrust [N]" : self.jet_thrust,
            "Thermo Power [kW]" : self.equivalent_shaft_power*1e-3,
            "Shaft Power [kW]" : self.shaft_power*1e-3,
            "Fuel flow [kg/s]" : self.mfuel,
        }
        
        with open("{0}_report.dat".format(self.name), "w+") as f:
            for key, item in data.items():
                f.write("{0}, {1}\n".format(key, item))
            f.close()
        
    def create_open_cycle_plot(self, name):
        
        plt.figure()
        plt.plot(self.entropy, self.enthalpy)
        plt.scatter(self.entropy, self.enthalpy)
        plt.savefig(name, dpi = 600)

class air():
    
    def __init__(self, air_props):
        self.R = air_props()[1]
        self.MW = air_props()[0]
        
class fuel():
    
    def __init__(self, fuel_props):
        self.R = fuel_props()[1]
        self.MW = fuel_props()[0]
        self.LHV = 1e-9
        
class mixt():
    
    def __init__(self, mix):
        self.R = mix[0]
        self.Cp = mix[1]
        self.gamma = mix[2]
        self.R = mix[3]
        
        
if __name__ == "__main__":
    
    gt_test = gas_turbine_cycle_builder()
    gt_test.define_working_media()
    gt_test.load_design_point()
    gt_test.open_brayton_cycle()
    gt_test.export_design_report()
    gt_test.create_open_cycle_plot()