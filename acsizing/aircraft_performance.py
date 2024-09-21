import numpy as np
from acsizing.standard_atmosphere import Standard_Atmosphere as SA

class aircraft_performance(object):

    def __init__(self):
        pass

    def mission_phase(self, mission):

        self.a = mission['a']
        self.i = mission['i']
        self.gamma = mission['gamma']
        self.alt = mission['alt']
        self.mach = mission['M']
        self.dV_dt = mission['accel']
        self.dg_dt = mission['ang_accel']

    def aircraft_characteristics(self, mtow = 8618, tsls = 30000, eta_p = 0.8, Sref = 44.5, CD0 = 0.0286, AR = 11., CLmax = 2.4):

        self.Sref = Sref
        self.CD0 = CD0
        self.m = mtow
        self.g = 9.81
        self.AR = AR
        self.CLmax = CLmax
        self.Tsls = tsls
        self.etap = eta_p

        self.rho = SA('Metric', self.alt)[1]
        self.rho_TO = SA('Metric', 0)[1]
        self.V = self.mach*SA('Metric', self.alt)[3]
        self.e = 1.78*(1 - 0.045*self.AR**0.68) - 0.64
        self.K = 1/(self.AR*self.e*np.pi)
        self.W = self.m*self.g

        self.entered = False

        if self.mach == 0:
            raise ValueError('Sea-level static thrust is calculated from the Gas Turbine performance and not aircraft performance')

    def power_calculation(self):

        thrust = self.thrust_calculation(0, 1e9, self.thust)
        power = thrust*self.V/self.etap

        return power

    def thrust_calculation(self, a, b, eqn1):
        
        hf = 0.5*(a + b)
        f1 = eqn1(a, self.cl(a))
        f2 = eqn1(hf, self.cl(hf))
        f3 = eqn1(b, self.cl(b))
        
        if f1*f2 < 0:
            self.entered = True
            if abs(f1 - f2) > 1e-3:
                otp = self.thrust_calculation(a, hf, eqn1)
            else:
                otp = 0.5*(a + b)
        elif f2*f3 < 0:
            self.entered = True
            if abs(f2 - f3) > 1e-3:
                otp = self.thrust_calculation(hf, b, eqn1)
            else:
                otp = 0.5*(a + b)
        elif self.entered:
            print('Found root in (%f, %f).' %(a, b))
            otp = 0.5*(a + b)
        else:
            print(self.alt)
            print('No root in (%f, %f) for M %f.' %(a, b, self.mach))
            otp = 0

        return otp

    def TOFL_calculation(self):
        vstall = (2*self.W/(self.rho_TO*self.Sref*self.CLmax))**0.5
        v = np.linspace(0, 1.3*vstall)
        dvdt = self.dv_dt(self.Tsls, self.CLmax, v)
        s = 0
        for i in range(len(v) - 1):
            s = s + v[i]*(1/dvdt[i])*(v[i + 1] - v[i])

        return s

    def dv_dt(self, T, CL, V):
        return (T*np.cos(np.radians(self.a + self.i)) - 0.5*self.rho*V**2*self.Sref*(self.CD0 + self.K*CL**2) - self.W*np.sin(np.radians(self.gamma)))/self.m

    def thust(self, T, CL):
        return T*np.cos(np.radians(self.a + self.i)) - 0.5*self.rho*self.V**2*self.Sref*(self.CD0 + self.K*CL**2) - self.W*np.sin(np.radians(self.gamma)) - self.m*self.dV_dt

    def cl(self, T):
        return (self.m*self.V*self.dg_dt + self.W*np.cos(np.radians(self.gamma))  - T*np.sin(np.radians(self.a + self.i)))/(0.5*self.rho*self.V**2*self.Sref)

