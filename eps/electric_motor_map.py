import math
import pandas as pd
from dataclasses import make_dataclass
from scipy import interpolate
import matplotlib.pyplot as plt
import numpy as np

class ElectricMotor(object):

    def __init__(self):
        self.efficiency_map = None
        self.power_torque_curves = None

    def load_eff_points(self):

        # Point Coordinates x=N and y=T
        Point = make_dataclass("Point", [("N", float), ("T", float)])

        # Initialization of dataframe
        df = pd.DataFrame()
        # Points with known efficiency (from the related EMRAX348 map, assumptions for 98%, 82%, 78%, 74%, 70%)
        df_98 = pd.DataFrame([Point(1930, 920)])
        df_98.insert(2, "eff", 0.98)
        df_96 = pd.DataFrame([Point(1187, 1202), Point(1426, 800), Point(1504, 742), Point(1700, 667), Point(2005, 674),
                                Point(2248, 705), Point(2499, 756), Point(2660, 800), Point(2950, 1001), Point(2503, 1199),
                                Point(2150, 1219), Point(1998, 1233), Point(1751, 1253), Point(1504, 1257)])
        df_96.insert(2, "eff", 0.96)
        df_95 = pd.DataFrame([Point(940, 1358), Point(944, 1201), Point(1002, 1068), Point(1151, 856), Point(1249, 757),
                                Point(1504, 597), Point(1700, 556), Point(2001, 580), Point(2403, 645), Point(2750, 726),
                                Point(2605, 686), Point(3004, 805), Point(3470, 1200), Point(3306, 1344), Point(3249, 914),
                                Point(3200, 1382), Point(3000, 1433), Point(2503, 1498), Point(2005, 1529), Point(1751, 1529),
                                Point(1802, 1529), Point(2601, 1491), Point(1500, 1511), Point(1249, 1477), Point(1002, 1402),
                                Point(3353, 969), Point(3459, 1061), Point(3482, 1136)])
        df_95.insert(2, "eff", 0.95)
        df_94 = pd.DataFrame([Point(4000, 1764), Point(3300, 1764), Point(2850, 1764), Point(2500, 1764), Point(1900, 1764),
                                Point(1504, 1750), Point(1241, 1686), Point(1002, 1569), Point(756, 1031), Point(752, 924),
                                Point(748, 703), Point(1202, 539), Point(1500, 498), Point(2001, 501), Point(2503, 505),
                                Point(2797, 525), Point(3000, 556), Point(3400, 737), Point(3451, 764), Point(3666, 1017),
                                Point(4000, 1324), Point(4000, 1399), Point(4000, 1400), Point(2248, 504), Point(4000, 1701),
                                Point(4000, 1700), Point(4000, 1500), Point(4000, 1501)])
        df_94.insert(2, "eff", 0.94)
        df_90 = pd.DataFrame([Point(4000, 1904), Point(3228, 1982), Point(2001, 1989), Point(1802, 1993), Point(1202, 2000),
                                Point(501, 1093), Point(497, 804), Point(1002, 391), Point(2875, 395), Point(3741, 797),
                                Point(4000, 1083), Point(810, 446), Point(1500, 361), Point(2000, 361), Point(2200, 361),
                                Point(2500, 361)])
        df_90.insert(2, "eff", 0.90)
        df_86 = pd.DataFrame([Point(4000, 1993), Point(2499, 2122), Point(2001, 2129), Point(1802, 2132), Point(916, 2136),
                                Point(411, 1594), Point(211, 800), Point(246, 395), Point(999, 180), Point(2906, 224),
                                Point(3702, 613), Point(4000, 940), Point(1500, 166), Point(2005, 166), Point(2500, 166)])
        df_86.insert(2, "eff", 0.86)
        df_82 = pd.DataFrame([Point(2000, 2200), Point(4000, 2200)])
        df_82.insert(2, "eff", 0.82)
        df_78 = pd.DataFrame([Point(0, 0), Point(0, 2200)])
        df_78.insert(2, "eff", 0.78)
        df_74 = pd.DataFrame([Point(2000, 0)])
        df_74.insert(2, "eff", 0.74)
        df_70 = pd.DataFrame([Point(4000, 0)])
        df_70.insert(2, "eff", 0.70)
        # Defining a step for the mesh
        step = 10
        # Defining the mesh
        mesh = pd.DataFrame(Point(N, T) for N in range(0, 4000+step, step)
                            for T in range(0, 2200+step, step))
        # Defining the known efficiency dataframe
        data = pd.concat([df, df_70, df_74, df_78, df_82, df_86, df_90, df_94, df_95, df_96, df_98], ignore_index=True)
        # 2D cubic interpolation using python's griddata
        interp = interpolate.griddata(list(zip(data["N"], data["T"])), data["eff"], mesh, method='cubic')
        # Inserting the efficiency values in the mesh dataframe
        mesh.insert(2, "eff", interp)
        # Defining the final dataframe for interpolated efficiency values
        data = mesh
        # From dataframe to pivot table - Preprocessing for plotting
        eff_map = pd.pivot_table(data, values="eff", index=["N"], columns=["T"], dropna=False)

        self.efficiency_map = eff_map

    def load_power_points(self):

        # Initialization of dataframe
        df = pd.DataFrame()
        # Points with known Power and Torque (from the related EMRAX348 curves)
        df.insert(0, "N", pd.Series([0, 500, 1000, 1500, 2000, 2500, 2700, 2900, 3100, 3500, 3700, 4000]))
        df.insert(1, "P_Continuous", pd.Series([0, 56, 107, 159, 209, 264, 284, 302, 320, 346, 356, 370]))
        df.insert(2, "P_Peak", pd.Series([0, 108, 212, 317, 426, 535, 575, 615, 649, 697, 717, 740]))
        df.insert(3, "T_Continuous", pd.Series([822, 899, 967, 1000, 1020, 1020, 1020, 1010, 1000, 967, 942, 929]))
        df.insert(4, "T_Peak", pd.Series([1800, 1894, 1981, 2015, 2024, 2024, 2010, 1991, 1971, 1923, 1890, 1875]))
        # Defining a step for the mesh
        step = 10
        # Defining the mesh
        mesh = pd.DataFrame()
        mesh.insert(0, "N", np.arange(0, 4000+step, step))
        # 1D cubic interpolation using python's interp1d
        f = interpolate.interp1d(df["N"], df["P_Continuous"], kind='cubic')
        g = interpolate.interp1d(df["N"], df["P_Peak"], kind='cubic')
        h = interpolate.interp1d(df["N"], df["T_Continuous"], kind='cubic')
        i = interpolate.interp1d(df["N"], df["T_Peak"], kind='cubic')
        # Calculating the power and torque values for the mesh
        Continuous_P_new = f(mesh["N"])
        Peak_P_new = g(mesh["N"])
        Continuous_T_new = h(mesh["N"])
        Peak_T_new = i(mesh["N"])
        # Inserting the power and torque values in the mesh dataframe
        mesh.insert(1, "P_Continuous", Continuous_P_new)
        mesh.insert(2, "P_Peak", Peak_P_new)
        mesh.insert(3, "T_Continuous", Continuous_T_new)
        mesh.insert(4, "T_Peak", Peak_T_new)
        # Defining the final dataframe of interpolated data
        PT_curves = mesh

        self.power_torque_curves = PT_curves

    def plot_eff_map(self):

        eff_map = self.efficiency_map
        PT_curves = self.power_torque_curves

        # Plotting the map (with the same iso-lines as in the literature)
        X = eff_map.columns.values
        Y = eff_map.index.values
        Z = eff_map.values
        X, Y = np.meshgrid(X, Y)
        iso = plt.contour(Y, X, Z, [0.86, 0.90, 0.94, 0.95, 0.96], alpha=1, cmap=plt.cm.Dark2)
        plt.yticks(np.arange(0, 2400, 400))
        # plt.pcolor(Y, X, Z, shading='auto', cmap=plt.cm.rainbow)
        # cbar = plt.colorbar(ticks=[0.7, 0.74, 0.78, 0.82, 0.86, 0.9, 0.94, 0.98])
        # cbar.set_label('Efficiency[-]')
        plt.grid(linewidth=1)
        plt.clabel(iso, inline=1, fontsize=10)
        plt.xlabel("N [RPM]")
        plt.ylabel("T [Nm]")
        plt.savefig('motor_eff_map.png', dpi=300)
        plt.plot(PT_curves["N"], PT_curves["T_Continuous"], 'k--', label='Continuous Torque', linewidth=2)
        plt.plot(PT_curves["N"], PT_curves["T_Peak"], 'k--', label='Peak Torque', linewidth=2)
        plt.text(200, 1050, 'Continuous Torque', color='k', fontsize='medium')
        plt.text(1500, 2100, 'Peak Torque', color='k', fontsize='medium')
        plt.yticks(np.arange(0, 2600, step=400))
        plt.xlabel("N[RRM]")
        plt.ylabel("T[Nm]")
        plt.savefig('motor_power_torque_eff.png', dpi=300)
        plt.close()
    
    def plot_power_torque_curves(self):

        PT_curves = self.power_torque_curves
        # fig, ax = plt.subplots()
        plt.plot(PT_curves["N"], PT_curves["P_Continuous"], 'g-', label='Continuous Power', linewidth=2)
        plt.plot(PT_curves["N"], PT_curves["P_Peak"], 'r-', label='Peak Power', linewidth=2)
        plt.text(2500, 200, 'Continuous Power', color='g', fontsize='large')
        plt.text(3000, 550, 'Peak Power', color='r', fontsize='large')
        plt.xlim([0, 4000])
        plt.ylim([0, 1000])
        plt.yticks(np.arange(0, 1100, step=100))
        plt.grid(which='minor', axis='x', linewidth=0.8)
        plt.grid(which='major', axis='x', linewidth=1.5)
        plt.grid(which='minor', axis='y', linewidth=0.8)
        plt.grid(which='major', axis='y', linewidth=1.5)
        plt.xlabel("N [RRM]")
        plt.ylabel("P [kW]")
        plt.savefig('motor_power_torque.png', dpi=300)
        plt.close()

    def motor_efficiency(self, N, T, step=10):
        return self.efficiency_map.loc[int(math.ceil(N/step))*step, int(math.ceil(T/step))*step]

    def motor_power_torque(self, N):
        return [self.power_torque_curves["P_Continuous"].loc[self.power_torque_curves['N'] == N].item(), self.power_torque_curves["P_Peak"].loc[self.power_torque_curves['N'] == N].item(),
                self.power_torque_curves["T_Continuous"].loc[self.power_torque_curves['N'] == N].item(), self.power_torque_curves["T_Peak"].loc[self.power_torque_curves['N'] == N].item()]

    def write_eff_csv(self):
        return self.efficiency_map.to_csv('electric_motor_efficiency.csv')

    def write_power_torque_csv(self):
        return self.power_torque_curves.to_csv('electric_motor_power_torque.csv', index=False)
    
if __name__ == "__main__":

    e_motor = ElectricMotor()
    e_motor.load_eff_points()
    e_motor.load_power_points()

    e_motor.write_eff_csv()
    e_motor.write_power_torque_csv()

    e_motor.plot_eff_map()
    e_motor.plot_power_torque_curves()