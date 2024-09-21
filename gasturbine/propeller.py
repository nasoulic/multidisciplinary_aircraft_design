import pandas as pd
from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt

class Propeller(object):

    def __init__(self):
        self.ncurve = None

    def load_nprop_points(self):
        # Initialization of dataframe
        df = pd.DataFrame()
        # Points with known efficiency (from the related nprop curve)
        df.insert(0, "J", pd.Series([2.2030455999598777, 2.19593910968842, 2.185279103186008, 2.1710658515478665, 2.1532993547739965,
                                     2.131130774655462, 2.095552630146491, 2.0421854133830344, 1.9994917485481492, 1.906988627112764,
                                     1.800254193585851, 1.7041930405478078, 1.6045743987865098, 1.5049554855855096, 1.4017788122215535,
                                     1.3021601704602546, 1.198983497096298, 1.0958068237323413, 0.9001270289330002, 0.693773682205087,
                                     0.49809388740574567, 0.29529857228049033, 0.16700509678390033, 0]))
        df.insert(1, "nprop", pd.Series([0, 0.10320276412145586, 0.19928819922059363, 0.3024910990963987, 0.4021351987066954,
                                         0.5017922577936194, 0.5985664535472883, 0.6989248230695331, 0.7491040761943879, 0.8100358506249712,
                                         0.8398575855423789, 0.8434163858078874, 0.8362989210312198, 0.8220639914778849, 0.7971529326367234,
                                         0.7598567342275812, 0.7025089968381092, 0.645161396176102, 0.526881884356047, 0.4121865463045677,
                                         0.29749120825308845, 0.17562752266445752, 0.10676156438696426, 0]))
        # Defining a step for the mesh
        step = 0.001
        # Defining the mesh
        mesh = pd.DataFrame()
        mesh.insert(0, "J", np.arange(0, 2.203+step, step))
        # 1D cubic interpolation using python's interp1d
        f = interpolate.interp1d(df["J"], df["nprop"], kind='cubic')
        nprop = f(mesh["J"])
        # Inserting the propeller efficiency values in the mesh dataframe
        mesh.insert(1, "nprop", nprop)
        # Defining the final dataframe of interpolated data
        ncurve = mesh
        self.ncurve = ncurve

    def plot_nprop_curve(self):
        ncurve = self.ncurve

        fig, ax = plt.subplots()
        plt.plot(ncurve["J"], ncurve["nprop"], 'k-', linewidth=2.5)
        plt.xlim([0, 2.8])
        plt.ylim([0, 1])
        plt.yticks(np.arange(0, 1.2, step=0.2))
        plt.xticks(np.arange(0, 3, step=0.2))
        ax.set_xticks(np.arange(0, 2.8, 0.1), minor=True)
        ax.set_yticks(np.arange(0, 1, 0.1), minor=True)
        plt.grid(which='minor', axis='x', linewidth=1.5)
        plt.grid(which='major', axis='x', linewidth=1.5)
        plt.grid(which='minor', axis='y', linewidth=1.5)
        plt.grid(which='major', axis='y', linewidth=1.5)
        plt.xlabel("Advance Ratio J [-]")
        plt.ylabel("nprop [-]")
        plt.savefig('propeller_efficiency.png', dpi=600)
        plt.close()

    def propeller_eff(self, Vinf, D=3.93, N=1212):  # Vinf-->J + step=0.001 for validation
        # return self.ncurve["nprop"].loc[round(J/step)] #  for validation
        J = round(Vinf*60/D/N, 3)
        return self.ncurve["nprop"].loc[np.isclose(self.ncurve['J'], J)].item()

    def write_nprop_csv(self):
        return self.ncurve.to_csv('propeller_efficiency.csv', index=False)