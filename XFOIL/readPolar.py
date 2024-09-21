import numpy as np
import matplotlib.pyplot as plt
import os
from scipy import interpolate

class airfoil_polar(object):

    def __init__(self, naca4digit, Re):

        self.airfoil_profile = naca4digit
        self.Re = Re
        self.home_dir = os.getcwd()

    def zero_angle_moment_coefficient(self):

        polarfile = self.find_polar_file()

        pdata = np.loadtxt(fname = polarfile, skiprows= 12)

        angle = pdata[:, 0]
        cl = pdata[:, 1]
        cd = pdata[:, 2]
        cdp = pdata[:, 3]
        cm = pdata[:, 4]

        cmom = interpolate.interp1d(angle, cm, kind = 'linear')

        return cmom(0)

    def zero_lift_angle(self):

        polarfile = self.find_polar_file()

        pdata = np.loadtxt(fname = polarfile, skiprows= 12)

        angle = pdata[:, 0]
        cl = pdata[:, 1]
        cd = pdata[:, 2]
        cdp = pdata[:, 3]
        cm = pdata[:, 4]

        aoa = interpolate.interp1d(cl, angle, kind = 'linear')
        
        return aoa(0)

    def find_polar_file(self):

        fp = os.path.join(self.home_dir, "NACA{0}_Re{1}".format(self.airfoil_profile, int(self.Re)))
        fl = os.listdir(fp)

        os.chdir(fp)

        for fn in fl:
            if '.p' in fn:
                polarfile = fn

        pfpath = os.path.join(fp, polarfile)

        os.chdir(self.home_dir)

        return pfpath

    def plot_polar(self):

        polarfile = self.find_polar_file()

        pdata = np.loadtxt(fname = polarfile, skiprows= 12)

        angle = pdata[:, 0]
        cl = pdata[:, 1]
        cd = pdata[:, 2]
        cdp = pdata[:, 3]
        cm = pdata[:, 4]

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, sharex = False, sharey = False, figsize = (10, 10/1.33))
        ax1.plot(angle, cd)
        ax1.set_title('Cd - alpha - ' + str(self.airfoil_profile))
        ax2.plot(angle, cl, 'tab:orange')
        ax2.set_title('Cl - alpha - ' + str(self.airfoil_profile))
        ax3.plot(angle, cm, 'tab:green')
        ax3.set_title('Cm - alpha - ' + str(self.airfoil_profile))
        ax4.plot(cd, cl, 'tab:red')
        ax4.set_title('Cl - Cd - ' + str(self.airfoil_profile))

        if not os.path.exists(os.path.join(self.home_dir, "NACA{0}_Re{1}".format(self.airfoil_profile, int(self.Re)))):
            os.mkdir(os.path.join(self.home_dir, "NACA{0}_Re{1}".format(self.airfoil_profile, int(self.Re))))

        os.chdir(os.path.join(self.home_dir, "NACA{0}_Re{1}".format(self.airfoil_profile, int(self.Re))))
        
        plt.savefig("NACA{0}_Re{1}_Polar.png".format(self.airfoil_profile, int(self.Re)), dpi = 600)
        plt.close()

        os.chdir(self.home_dir)