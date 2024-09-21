import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata, interp2d
from gasturbine.filter_data import find_in_data
import os

class map_builder(object):

    def __init__(self):
        self.home_dir = os.getcwd()
        self.eff_points = []

    def build_map(self, surge_line, rpm_lines, efficiency_map, npoints):

        '''
        --------------------------------------------------
        Create map from points

        INPUTS:
        surge           :           surge line curve
        efficiency map  :           efficiency contours
        rpm             :           rpm curves
        npoints         :           points to divide the grid to

        --------------------------------------------------
        '''

        surge_line = np.loadtxt(surge_line)
        # efficiency = np.loadtxt(efficiency_map)
        rpm_lines = np.loadtxt(rpm_lines)
        
        for item in efficiency_map:
            self.load_efficiency_points(item)
            
        self.eff_points = np.array(self.eff_points)

        mflow = np.linspace(min(rpm_lines[:, 0]), max(rpm_lines[:, 0]), num = npoints, endpoint = True)
        presr = np.linspace(min(rpm_lines[:, 1]), max(rpm_lines[:, 1]), num = npoints, endpoint = True)

        m, pr = np.meshgrid(mflow, presr)

        # eff = griddata(efficiency[:, 0:2], efficiency[:, 2], (m, pr), method = 'cubic')
        eff = griddata(self.eff_points[:, 0:2], self.eff_points[:, 2], (m, pr), method = 'cubic')

        self.efficiency_map = eff
        self.surge = surge_line
        self.rpm = rpm_lines
        # self.eff_points = efficiency
        self.npoints = npoints

    def load_efficiency_points(self, filename):
        
        eff_pts = np.loadtxt(filename)
        for i, item in enumerate(eff_pts):
            self.eff_points.append([eff_pts[i, 0], eff_pts[i, 1], eff_pts[i, 2]])

    def get_ref_info(self):

        with open("ref_info.map", "r") as f:
            lines = f.readlines()
        f.close()

        res = {}
        for line in lines:
            tmp = line.strip("\n").split(",")
            res[tmp[0]] = float(tmp[1])

        self.Tin = res["inlet temperature"]
        self.PR = res["pressure ratio"]
        self.Wc = res["corrected mass flow rate"]
        self.mc = res["mass flow rate"]
        self.N = res['reference rotational speed']
        self.Pin = res["inlet pressure"]

    def find_point_on_map(self, point):

        '''
        --------------------------------------------------
        Interpolate in map to find efficiency for pair of values
        --------------------------------------------------
        '''

        mflow = np.linspace(min(self.rpm[:, 0]), max(self.rpm[:, 0]), num = self.npoints, endpoint = True)
        presr = np.linspace(min(self.rpm[:, 1]), max(self.rpm[:, 1]), num = self.npoints, endpoint = True)

        init_map = self.efficiency_map
        init_map[np.isnan(init_map)] = 0

        eta = interp2d(mflow, presr, init_map, kind = 'linear')

        return eta(point[0], point[1])
    
    def export_map(self, mapname):

        '''
        --------------------------------------------------
        Export .map file
        --------------------------------------------------
        '''

        mflow = np.linspace(min(self.rpm[:, 0]), max(self.rpm[:, 0]), num = self.npoints, endpoint = True)
        presr = np.linspace(min(self.rpm[:, 1]), max(self.rpm[:, 1]), num = self.npoints, endpoint = True)

        outputfile = self.efficiency_map
        outputfile = np.r_[outputfile, [mflow]]
        outputfile = np.c_[outputfile, np.append(presr, [0])]
        np.savetxt(mapname, outputfile)

    def plot_map(self, filled = True, save_map = True, fname = "lpc_centrifugal_map"):

        '''
        --------------------------------------------------
        Plot the generated map and save image
        --------------------------------------------------
        '''

        mflow = np.linspace(min(self.rpm[:, 0]), max(self.rpm[:, 0]), num = self.npoints, endpoint = True)
        presr = np.linspace(min(self.rpm[:, 1]), max(self.rpm[:, 1]), num = self.npoints, endpoint = True)

        efficiency_levels, eff_ind = find_in_data(self.eff_points)
        rpm_levels, rpm_ind = find_in_data(self.rpm)

        plt.figure()
        if filled:
            cont = plt.contourf(mflow, presr, self.efficiency_map, cmap = 'jet', alpha = 0.3)
            plt.colorbar()
    
        plt.plot(self.surge[:, 0], self.surge[:, 1], c = 'k', linestyle = '-.', linewidth = 1.2)
        for i in rpm_ind:
            plt.plot(self.rpm[:, 0][i], self.rpm[:, 1][i], c = 'k', linewidth = 1.7)
        for i in eff_ind:
            plt.plot(self.eff_points[:, 0][i], self.eff_points[:, 1][i], c = 'k', linestyle = '--', linewidth = 1.2)


        if save_map:
            plt.savefig('{0}.png'.format(fname), dpi = 600)

    def add_point_on_map(self, point):

        '''
        --------------------------------------------------
        Add point to existing map plot
        --------------------------------------------------
        '''

        plt.scatter(point[0], point[1], c = 'k')

    def navigate_to_path(self, folder_tree):

        '''
        --------------------------------------------------
        Navigate to directory
        --------------------------------------------------
        '''

        for folder in folder_tree:
            cwd = os.getcwd()
            os.chdir(os.path.join(cwd, folder))

    def reset_path(self):

        '''
        --------------------------------------------------
        Return to home directory
        --------------------------------------------------
        '''

        os.chdir(self.home_dir)

    def show_map(self):
        
        '''
        --------------------------------------------------
        Show map plot
        --------------------------------------------------
        '''

        plt.show()      
        
    def close_map(self):
        
        '''
        --------------------------------------------------
        Close map plot
        --------------------------------------------------
        '''

        plt.close()    

if __name__ == '__main__':

    lpc_map = map_builder()
    lpc_map.navigate_to_path(["component_maps", "lpc_centrifugal"])
    lpc_map.get_ref_info()
    # lpc_map.build_map("surge_line.map", "rpm_lines.map", "lpc_efficiency.map", 100)
    lpc_map.build_map('surge_line.map', 'rpm_lines.map', ["70eff.map", "75eff.map", "80eff.map", "82eff.map"], 50)
    lpc_map.export_map('lpc_centrifugal.map')
    lpc_map.plot_map(filled = True, save_map = True, fname = "lpc_centrifugal_map")
    lpc_map.show_map()
    
    lpc_map.reset_path()

    hpc_map = map_builder()
    hpc_map.navigate_to_path(["component_maps", "hpc_centrifugal"])
    hpc_map.get_ref_info()
    # hpc_map.build_map("surge_line.map", "rpm_lines.map", "hpc_efficiency.map", 100)
    hpc_map.build_map("surge_line.map", "rpm_lines.map", ["eff65.map", "eff70.map", "eff75.map", "eff80.map", "eff82.map", "eff84.map", "eff86.map"], 50)
    hpc_map.export_map("hpc_centrifugal.map")
    hpc_map.plot_map(filled = True, save_map = True, fname = "hpc_centrifugal_map")
    hpc_map.show_map()

    hpc_map.reset_path()