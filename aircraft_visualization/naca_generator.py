import numpy as np
import matplotlib.pyplot as plt

class naca(object):

    def __init__(self) -> None:
        pass

    def create_airfoil(self, naca_dgts, alpha = 0, chord = 1, points = 1000, spacing = 0, closed_te = True, create_output = False):

        '''
        ----------------------------------------------------------------------------------------------------------
        INPUTS:
        naca_dgts :    Naca profile series                    (4, 5, or 6 digits)
        alpha       :    angle of attack                        [deg]
        chord       :    airfoil chord                          [m]
        points      :    number of points in airfoil            [-]
        spacing     :    linear or cosine spacing               (0 for linear, 1 for cosine)
        closed_te   :    closed trailing edge                   (True for closed, False for open)
        ----------------------------------------------------------------------------------------------------------
        '''

        naca_digits = int(naca_dgts)

        if np.floor(naca_digits/1e6) < 1.:
            if np.floor(naca_digits/1e5) < 1.:
                if np.floor(naca_digits/1e4) < 1.:
                    ndigits = 4
                else:
                    ndigits = 5
            else:
                ndigits = 6
        else:
            raise ValueError('NACA generator only supports 4, 5, and 6 digit Series.')
        
        if spacing < 1:
            x = np.linspace(0, 1, points, endpoint = True)
        else:
            beta = np.linspace(0, np.pi, num = points, endpoint = True)
            x = (1 - np.cos(beta))/2

        thickness = (naca_digits % 100)/100
        alpha = np.radians(alpha)

        yt = self.get_thickness(x, thickness, closed_te)
        y_c = []
        dy_dx = []
        nacaname = 'NACA{0}{1}{2}.dat'.format(0, 0, 0)

        if ndigits == 4:
            max_camber = np.floor(naca_digits/1e3)/100
            max_camber_pos = (np.floor(naca_digits/100) % 10)/10
            for item in x:
                y_c.append(self.get_camber4digit(max_camber, max_camber_pos, alpha, item))
                dy_dx.append(self.get_gradient4digit(max_camber, max_camber_pos, item))
            if int(naca_digits % 100) < 10:
                nacaname = 'NACA{0}{1}{2}{3}.dat'.format(int(np.floor(naca_digits/1e3)), int(np.floor(naca_digits/1e2) % 10), 0, int(naca_digits % 100))
            else:
                nacaname = 'NACA{0}{1}{2}.dat'.format(int(np.floor(naca_digits/1e3)), int(np.floor(naca_digits/1e2) % 10), int(naca_digits % 100))
        elif ndigits == 5:
            design_cl = np.floor(naca_digits/1e4)*3/20
            max_camber_pos = (np.floor(naca_digits/1e3) % 10)/20
            camber_type = (np.floor(naca_digits/100) % 10)
            for item in x:
                y_c.append(self.get_camber5digit(design_cl, max_camber_pos, item, alpha, camber_type))
                dy_dx.append(self.get_gradient5digit(design_cl, max_camber_pos, item, alpha, camber_type))
            if int(naca_digits % 100) < 10:
                nacaname = 'NACA{0}{1}{2}{3}{4}.dat'.format(int(np.floor(naca_digits/1e4)), int(np.floor(naca_digits/1e3) % 10), int(np.floor(naca_digits/1e2) % 10), 0, int(naca_digits % 100))
            else:
                nacaname = 'NACA{0}{1}{2}{3}.dat'.format(int(np.floor(naca_digits/1e4)), int(np.floor(naca_digits/1e3) % 10), int(np.floor(naca_digits/1e2) % 10), int(naca_digits % 100))
        elif ndigits == 6:
            series = np.floor(naca_digits/1e5)
            a = (np.floor(naca_digits/1e4) % 10)/10
            cl_design = (np.floor(naca_digits/100) % 10)/10
            g = -1/(1 - a)*(a**2*(0.5*np.log(a) - 0.25) + 0.25)
            h = 1/(1 - a)*(0.5*(1 - a)**2*np.log(1 - a) - 0.25*(1 - a)**2) + g
            if int(np.floor(naca_digits/1e3) % 10) > 0:
                raise ValueError('Error detected in NACA 6-series definition. NACA XX{0}XXX detected instead of XX-XXX. Replace digit with 0.'.format(int(np.floor(naca_digits/1e3) % 10)))
            if series == 6:
                for item in x:
                    y_c.append(self.get_camber6digit(cl_design, a, g, h, alpha, item))
                    dy_dx.append(self.get_gradient6digit(cl_design, a, g, h, alpha, item))
                if int(naca_digits % 100) < 10:
                    nacaname = 'NACA{0}{1}{2}{3}{4}{5}.dat'.format(int(np.floor(naca_digits/1e5)), int(np.floor(naca_digits/1e4) % 10), int(0), int(np.floor(naca_digits/1e2) % 10), 0, int(naca_digits % 100))
                else:
                    nacaname = 'NACA{0}{1}{2}{3}{4}.dat'.format(int(np.floor(naca_digits/1e5)), int(np.floor(naca_digits/1e4) % 10), int(0), int(np.floor(naca_digits/1e2) % 10), int(naca_digits % 100))
            else:
                raise ValueError('NACA 6 Series must begin with 6, not {0}'.format(int(series)))
        else:
            raise ValueError('NACA generator only supports 4, 5, and 6 digit Series.')

        ### Rotate airfoil according to alpha
        theta = np.arctan(np.array(dy_dx))
        # x = 0.5 - (0.5 - x)*np.cos(alpha)

        ### Calculate coordinates
        upper_x = (x - yt*np.sin(theta))*chord
        lower_x = (x + yt*np.sin(theta))*chord
        upper_y = (y_c + yt*np.cos(theta))*chord
        lower_y = (y_c - yt*np.cos(theta))*chord
        
        if create_output:
            with open(nacaname, 'w') as f:
                for i, item in enumerate(upper_x):
                    f.write('%f\t%f\n' %(upper_x[-i - 1], upper_y[-i -1]))
                for i, item in enumerate(lower_x):
                    f.write('%f\t%f\n' %(lower_x[i], lower_y[i]))
            f.close()

            self.plot_profile(upper_x, lower_x, upper_y, lower_y, x, y_c, nacaname)

        self.x_u = upper_x
        self.x_l = lower_x
        self.y_u = upper_y
        self.y_l = lower_y

    def get_thickness(self, x, T, closed_te):

        a0 = 0.2969
        a1 = -0.126
        a2 = -0.3516
        a3 = 0.2843
        if closed_te:
            a4 = -0.1036
        else:
            a4 = -0.1015

        yt = T/0.2*(a0*x**0.5 + a1*x + a2*x**2 + a3*x**3 + a4*x**4)

        return yt
    
    def get_camber6digit(self, c_li, a, g, h, alpha, x):

        if x == 0:
            x = 1e-8
        if x == 1:
            x = .99999999999

        y_c = c_li/(2*np.pi*(a + 1))*(1/(1 - a)*(0.5*(a - x)**2*np.log(abs(a - x)) -\
         0.5*(1 - x)**2*np.log(1 - x) + 0.25*(1 - x)**2 - 0.25*(a - x)**2) -\
             x*np.log(x) + g - h*x) + (0.5 - x)*np.sin(alpha)
        return y_c

    def get_gradient6digit(self, c_li, a, h, alpha, x):

        if x == 0:
            x = 1e-8
        if x == 1:
            x = .99999999999

        dyc_dx = -(c_li*(h + np.log(x) - (x/2 - a/2 + (np.log(1 - x)*(2*x - 2))/2 +\
         (np.log(abs(a - x))*(2*a - 2*x))/2 +\
         (np.sign(a - x)*(a - x)**2)/(2*abs(a - x)))/(a - 1) + 1))/(2*np.pi*(a + 1)*np.cos(alpha)) -\
         np.tan(alpha)
        return dyc_dx

    def get_camber5digit(self, l, p, x, alpha, camber_type):
        
        if camber_type == 0:
            # r = 3.33*p**3 + 0.70*p**2+1.19*p - 0.00399
            # k1 = 1514933.33*p**4 - 1087744.0*p**3 + 286455.26*p**2 - 32968.47*p + 1420.185
            r = l/0.3*(2.2*p**2 + p + 0.003)
            k1 = l/0.3*(0.0599*p** - 2.919)
            if x < r:
                y_c = k1/6*(x**3 - 3*r*x**2 + r**2*(3 - r)*x) + (0.5 - x)*np.sin(alpha)
            else:
                y_c = k1*r**3/6*(1 - x) + (0.5 - x)*np.sin(alpha)
        elif camber_type == 1:
            # r = 10.66*p**3 - 2.0*p**2 + 1.73*p - 0.034
            # k1 = -27973.33*p**3 + 17972.80*p**2 - 3888.40*p + 289.07
            # k2_k1 = 85.528*p**3 - 34.983*p**2 + 4.803*p - 0.215
            r = (3.6*p**2 + 0.808*p + 0.0136)*l/0.3
            k1 = (0.0482*p**-3.041)*l/0.3
            k2_k1 = (85.528*p**3 - 34.983*p**2 + 4.803*p - 0.2153)*l/0.3

            if x < r:
                y_c = k1/6*((x - r)**3 - k2_k1*(1 - r)**3*x - r**3*x + r**3) + (0.5 - x)*np.sin(alpha)
            else:
                y_c = k1/6*(k2_k1*(x - r)**3 - k2_k1*(1 - r)**3*x - r**3*x + r**3) + (0.5 - x)*np.sin(alpha)
        else:
            raise ValueError('Error in NACA LP{0}XX profile. Q can either be 0 or 1, not {0}.'.format(int(camber_type)))

        return y_c

    def get_gradient5digit(self, l, p, x, alpha, camber_type):
        
        if camber_type == 0:
            # r = 3.33*p**3 + 0.70*p**2+1.19*p - 0.00399
            # k1 = 1514933.33*p**4 - 1087744.0*p**3 + 286455.26*p**2 - 32968.47*p + 1420.185
            r = l/0.3*(2.2*p**2 + p + 0.003)
            k1 = l/0.3*(0.0599*p** - 2.919)

            if x < r:
                dy_dx = k1/6*(3*x**2 - 6*r*x + r**2*(3 - r))/np.cos(alpha) - np.tan(alpha)
            else:
                dy_dx = - k1*r**3/(6*np.cos(alpha)) - np.tan(alpha)
        elif camber_type == 1:
            # r = 10.66*p**3 - 2.0*p**2 + 1.73*p - 0.034
            # k1 = -27973.33*p**3 + 17972.80*p**2 - 3888.40*p + 289.07
            # k2_k1 = 85.528*p**3 - 34.983*p**2 + 4.803*p - 0.215
            r = (3.6*p**2 + 0.808*p + 0.0136)*l/0.3
            k1 = (0.0482*p** - 3.041)*l/0.3
            k2_k1 = (85.528*p**3 - 34.983*p**2 + 4.803*p - 0.2153)*l/0.3

            if x < r:
                dy_dx = k1/6*(3*(x - r)**2 - k2_k1*(1 - r)**3 - r**3)/np.cos(alpha) - np.tan(alpha)
            else:
                dy_dx = k1/6*(3*k2_k1*(x - r)**2 - k2_k1*(1 - r)**3 - r**3)/np.cos(alpha) - np.tan(alpha)
        else:
            raise ValueError('Error in NACA LP{0}XX profile. Q can be either 0 or 1, not {0}.'.format(int(camber_type)))

        return dy_dx
    
    def get_camber4digit(self, M, P, alpha, x):

        if x >= 0 and x < P:
            yc = M/P**2*(2*P*x - x**2) + (0.5 - x)*np.sin(alpha)
        else:
            yc = M/(1 - P)**2*(1 -2*P + 2*P*x - x**2) + (0.5 - x)*np.sin(alpha)

        return yc

    def get_gradient4digit(self, M, P, x):

        if x >= 0 and x < P:
            dyc_dx = 2*M/P**2*(P - x)
        else:
            dyc_dx = 2*M/(1 - P)**2*(P - x)
        
        return dyc_dx

    def plot_profile(self, xu, xl, yu, yl, x, yc, nacaname):

        plt.figure()
        plt.grid()
        plt.plot(xl, yl, color = 'black')
        plt.plot(xu, yu, color = 'black')
        # plt.plot(x, yc, color = 'r', linestyle = '--', linewidth = 1)
        plt.axis('equal')
        plt.xlim([min(xl), max(xl)])
        plt.tight_layout()
        plt.savefig(nacaname.replace('.dat', '.png'), dpi = 300)
        plt.close()
