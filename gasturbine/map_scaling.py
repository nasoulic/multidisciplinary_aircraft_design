from gasturbine.gas_properties import gas_properties
import numpy as np
import copy
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from gasturbine.filter_data import find_in_data
import os

class Map_Scaling():

    def __init__(self, comp_map):
        self.map2scale = comp_map
        self.rpm = copy.deepcopy(comp_map.rpm)
        self.gas = gas_properties()
        self.home_dir = os.getcwd()

    def _calc_His(self, T, pr):
        cp = self.gas.cp_cold(T)
        gamma = self.gas.gamma(cp, self.gas.R_cold)
        return cp*T*(pr**((gamma -1)/gamma) - 1)
    
    def _calc_isentropic_efficiency(self, T, pr, eta_p):
        cp = self.gas.cp_cold(T)
        gamma = self.gas.gamma(cp, self.gas.R_cold)
        return (pr**((gamma - 1)/gamma) - 1)/(pr**((gamma - 1)/(gamma*eta_p)) - 1)
    
    def _calc_polytropic_efficiency(self, T, pr, nis):
        cp = self.gas.cp_cold(T)
        gamma = self.gas.gamma(cp, self.gas.R_cold)
        return (gamma - 1)*np.log(pr)/(gamma*np.log((pr**((gamma - 1)/gamma) - 1)/nis + 1))
    
    def axial_compressor(self, PR_ref):
        PR_rel_50W = 0.1961 + 0.08*np.log(PR_ref)
        Wc_Nc_50W = 1.1037*PR_ref**-0.2223
        Wc_80N = 0.1751*np.exp(-0.1042*PR_ref)
        return [PR_rel_50W, Wc_Nc_50W, Wc_80N]
    
    def centrifugal_compressor(self, PR_ref):
        PR_rel_50W = 0.33
        Wc_Nc_50W = 1.1037*PR_ref**-0.2223
        Wc_80N = 0.14
        return [PR_rel_50W, Wc_Nc_50W, Wc_80N]
    
    def scale_factor(self, gamma, PR_new, PR_ref):
        return (PR_new**((gamma - 1)/gamma) - 1)/(PR_ref**((gamma - 1)/gamma) - 1)
    
    def adjust_mass_flow(self, PR_new, PR_ref, ctype = "centrifugal"):

        if ctype == "centrifugal":
            ref_values = self.centrifugal_compressor(PR_ref)
            new_values = self.centrifugal_compressor(PR_new)
        elif ctype == "axial":
            ref_values = self.axial_compressor(PR_ref)
            new_values = self.axial_compressor(PR_new)
        else:
            raise ValueError("Compressor type not supported.")

        self.get_corr_rotational_speed()
        
        for N in self.diff_N:
            filtered_N = self.map2scale.rpm[self.map2scale.rpm[:, 2] == N]
            Wc_max = max(filtered_N[:, 0])
            Wc_orig = self.map2scale.rpm[self.map2scale.rpm[:, 2] == N][:, 0]
            Wc_new = Wc_max - new_values[-1]/ref_values[-1]*(Wc_max - Wc_orig)
            filtered_N[:, 0] = Wc_new
            self.rpm[self.rpm[:, 2] == N] = filtered_N
    
    def scale_map(self, PR_new, ctype, npoints = 100):
        
        self.npoints = npoints
        
        self.adjust_mass_flow(PR_new, self.map2scale.PR, ctype)

        cp = self.gas.cp_cold(self.map2scale.Tin)
        gamma = self.gas.gamma(cp, self.gas.R_cold)
        fscale = self.scale_factor(gamma, PR_new, self.map2scale.PR)

        his_orig = self._calc_His(self.map2scale.Tin, self.rpm[:, 1])
        his_new = fscale*his_orig

        his_orig_N2 = his_orig/(self.rpm[:, 2]*self.map2scale.N)**2
        Nc_new = (his_new/(fscale*his_orig_N2))**0.5

        PR = (fscale/(cp*self.map2scale.Tin)*his_orig_N2*Nc_new**2 + 1)**(gamma/(gamma - 1))                
        self.rpm[:, 1] = PR
        
        self.scale_efficiency_map(PR_new, ctype)
        self.get_surge_line()
        
        self.mc, self.pr = np.meshgrid(np.linspace(min(self.rpm[:, 0]), max(self.rpm[:, 0]), num = npoints, endpoint = True), np.linspace(min(self.rpm[:, 1]), max(self.rpm[:, 1]), num = npoints, endpoint = True))
        
        self.efficiency_points = self.efficiency_points[~np.isnan(self.efficiency_points).any(axis = 1)]
        
        self.efficiency_map_scaled = griddata(self.efficiency_points[:, 0:2], self.efficiency_points[:, 2], (self.mc, self.pr), method = "cubic")

    def scale_efficiency_map(self, PR_new, ctype):

        cp = self.gas.cp_cold(self.map2scale.Tin)
        gamma = self.gas.gamma(cp, self.gas.R_cold)
        fscale = self.scale_factor(gamma, PR_new, self.map2scale.PR)

        his_orig = self._calc_His(self.map2scale.Tin, self.map2scale.eff_points[:, 1])
        his_new = fscale*his_orig

        interp_N = self.get_int_corr_rotational_speed(self.map2scale.eff_points[:, 0], self.map2scale.eff_points[:, 1])

        his_orig_N2 = his_orig/(interp_N*self.map2scale.N)**2

        Nc_new = (his_new/(fscale*his_orig_N2))**0.5

        PR = (fscale/(cp*self.map2scale.Tin)*his_orig_N2*Nc_new**2 + 1)**(gamma/(gamma - 1))

        self.efficiency_points = copy.deepcopy(self.map2scale.eff_points)
        self.efficiency_points[:, 1] = PR
        
    def find_point_on_map(self, wc, pr):
        
        '''
        --------------------------------------------------
        Interpolate in map to find efficiency for pair of values
        --------------------------------------------------
        '''
        
        # mflow_corr = np.linspace(min(self.rpm[:, 0]), max(self.rpm[:, 0]), num = self.npoints, endpoint = True)
        # pr_corr = np.linspace(min(self.rpm[:, 1]), max(self.rpm[:, 1]), num = self.npoints, endpoint = True)

        eff_val = griddata((self.efficiency_points[:, 0], self.efficiency_points[:, 1]), self.efficiency_points[:, 2], (wc, pr), method = "cubic")
        rpm_val = griddata((self.rpm[:, 0], self.rpm[:, 1]), self.rpm[:, 2], (wc, pr), method = "cubic")

        return eff_val, rpm_val

    def get_int_corr_rotational_speed(self, x, y):
        return griddata((self.rpm[:, 0], self.rpm[:, 1]), self.rpm[:, 2], (x, y), method = "cubic")

    def get_surge_line(self):
        
        self.get_corr_rotational_speed()
        surgeline = []
        for N in self.diff_N:
            filtered_N = self.rpm[self.rpm[:, 2] == N]
            Wcmin = min(filtered_N[:, 0])
            surgeline.append(filtered_N[filtered_N[:, 0] == Wcmin][0])

        self.surgeline = np.array(surgeline)

    def get_corr_rotational_speed(self):

        self.diff_N = []
        for item in self.map2scale.rpm:
            if item[-1] not in self.diff_N:
                self.diff_N.append(item[-1])
                
    def export_map(self, mapname):
        
        '''
        --------------------------------------------------
        Export .map file
        --------------------------------------------------
        '''
        
        mflow = np.linspace(min(self.rpm[:, 0]), max(self.rpm[:, 0]), num = self.npoints, endpoint = True)
        presr = np.linspace(min(self.rpm[:, 1]), max(self.rpm[:, 1]), num = self.npoints, endpoint = True)
        
        outputfile = self.efficiency_map_scaled
        outputfile = np.r_[outputfile, [mflow]]
        outputfile = np.c_[outputfile, np.append(presr, [0])]
        np.savetxt(mapname, outputfile)
        

    def plot_map(self, show_original = False, filled = False):

        plt.figure()

        for N in self.diff_N:
            filtered_data = self.rpm[self.rpm[:, 2] == N]
            plt.plot(filtered_data[:, 0], filtered_data[:, 1], color = 'k')
            if show_original:
                original_map = self.map2scale.rpm[self.map2scale.rpm[:, 2] == N]
                plt.plot(original_map[:, 0], original_map[:, 1], linestyle = "--", color = 'k', linewidth = 0.5)
        
        if show_original:   
            eff_levels, eff_ind = find_in_data(self.map2scale.eff_points)
            for i in eff_ind:
                plt.plot(self.map2scale.eff_points[:, 0][i], self.map2scale.eff_points[:, 1][i], c = 'k', linestyle = '--', linewidth = 1.2)
        
        plt.plot(self.surgeline[:, 0], self.surgeline[:, 1], color = 'k')
        if show_original:
            plt.plot(self.map2scale.surge[:, 0], self.map2scale.surge[:, 1], linestyle = "--", color = 'k', linewidth = 0.5)
        
        eff_levels, eff_ind = find_in_data(self.efficiency_points)
        
        for i in eff_ind:
            plt.plot(self.efficiency_points[:, 0][i], self.efficiency_points[:, 1][i], c = 'k', linestyle = '--', linewidth = 1.2)

        if filled:
            plt.contourf(self.mc, self.pr, self.efficiency_map_scaled, cmap = "jet", alpha = 0.3)
            plt.colorbar()       
        
    def navigate_to_path(self, folder_tree):

        '''
        --------------------------------------------------
        Navigate to directory
        --------------------------------------------------
        '''

        for folder in folder_tree:
            cwd = os.getcwd()
            
            if not os.path.exists(os.path.join(cwd, folder)):
                os.mkdir(os.path.join(cwd, folder))
                
            os.chdir(os.path.join(cwd, folder))
            
    def reset_path(self):
        
        '''
        --------------------------------------------------
        Reset path to home directory
        --------------------------------------------------
        '''
        
        os.chdir(self.home_dir)
        
    def save_map_fig(self, figname):
        
        '''
        --------------------------------------------------
        Save map figure to path
        --------------------------------------------------
        '''
        
        plt.savefig(figname, dpi = 600)
        
    def show_map_fig(self):
        
        '''
        --------------------------------------------------
        Show plot
        --------------------------------------------------
        '''
        
        plt.show()
        
    def close_map_fig(self):
        
        '''
        --------------------------------------------------
        Show plot
        --------------------------------------------------
        '''
        
        plt.close()


if __name__ == "__main__":
    
    from compressor_map import map_builder

    lpc_map = map_builder()
    lpc_map.navigate_to_path(["component_maps", "lpc_centrifugal"])
    lpc_map.get_ref_info()
    lpc_map.build_map('surge_line.map', 'rpm_lines.map', ["70eff.map", "75eff.map", "80eff.map", "82eff.map"], 100)
    lpc_map.eff_points = np.array(lpc_map.eff_points)
    lpc_map.export_map('lpc_centrifugal.map')
    lpc_map.close_map()
    lpc_map.reset_path()

    scaled_map = Map_Scaling(lpc_map)
    scaled_map.scale_map(4.2, 28780, "centrifugal")
    # scaled_map.scale_map(4.05, 28780)
    scaled_map.plot_map(False, True)
    # scaled_map.export_map()
    scaled_map.navigate_to_path(["results", "lpc_compressor"])
    scaled_map.export_map("lpc_compressor.map")
    scaled_map.save_map_fig("lpc_compressor_map.png")
    # scaled_map.show_map_fig()
    scaled_map.reset_path()
    
    hpc_map = map_builder()
    hpc_map.navigate_to_path(["component_maps", "hpc_centrifugal"])
    hpc_map.get_ref_info()
    hpc_map.build_map("surge_line.map", "rpm_lines.map", ["eff65.map", "eff70.map", "eff75.map", "eff80.map", "eff82.map", "eff84.map", "eff86.map"], 50)
    hpc_map.export_map("hpc_centrifugal.map")
    hpc_map.plot_map(filled = True, save_map = True, fname = "hpc_centrifugal_map")
    hpc_map.close_map()
    hpc_map.reset_path()
    
    scaled_map_hpc = Map_Scaling(hpc_map)
    scaled_map_hpc.scale_map(2.6, 39000, "centrifugal")
    scaled_map_hpc.plot_map(False, True)
    scaled_map_hpc.navigate_to_path(["results", "hpc_compressor"])
    scaled_map_hpc.export_map("hpc_compressor.map")
    scaled_map_hpc.save_map_fig("hpc_compressor_map.png")
    scaled_map_hpc.reset_path()