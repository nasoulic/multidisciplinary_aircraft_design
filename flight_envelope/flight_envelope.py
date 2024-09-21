import numpy as np
import matplotlib.pyplot as plt
from acsizing.standard_atmosphere import Standard_Atmosphere

class Flight_Envelope():

    def __init__(self, input_data):
        self.MTOW = input_data['MTOW']
        self.S = input_data['Sref']
        self.Vc = input_data['Cruise Speed']
        self.rho_s = input_data['Sea level density']
        self.CLmax = input_data['CLmax']
        self.CLmin = input_data['CLmin']
        self.n_pos = input_data['Limit load factor']
        self.g = input_data['Gravity']
        self.a = input_data['Lift curve slope']
        self.C_bar = input_data['Wing MAC']
        self.FL = input_data['Cruise Altitude']
        self.rho = Standard_Atmosphere("Metric", self.FL*0.3048)[1]
        
        # self.CL = input_data['Instant CL']

    def get_gust_speed(self, case):
        ''' CS23.333 Gust Envelope'''
        if case == 'Cruise':
            if self.FL < 20000:
                Ude = 50 # fps
            else:
                Ude = 50 + (25-50)*(self.FL*100 - 20000)/(50000 - 20000)
        elif case == "Dive":
            if self.FL < 20000:
                Ude = 25
            else:
                Ude = 25 + (12.5 - 25)*(self.FL*100 - 20000)/(50000 - 20000)
        elif case == 'Rough_air':
            if self.FL < 20000:
                Ude = 66
            else:
                Ude = 66 + (38 - 66)*(self.FL*100 - 20000)/(50000 - 20000)
        Ude = Ude*0.3048 # Convert to m/s
        return Ude
    
    def calibrate_cruise_factor(self, wing_loading):
        ''' CS23.335'''
        if wing_loading > 20:
            factor = 33 + (28.6 - 33)*(wing_loading - 20)/(100 - 20)
        else:
            factor = 33
        return factor

    def calibrate_dive_factor(self, wing_loading):
        ''' CS23.335'''
        if wing_loading > 20:
            factor = 1.4 + (1.35 - 1.4)*(wing_loading - 20)/(100 - 20)
        else:
            factor = 1.4
        return factor

    def gust_load_factor(self, EAS, rho, case):
        ''' CS23.341 paragraph (c)'''
        #span = (11*self.S)**0.5
        Ude = self.get_gust_speed(case)
        mg = 2*(self.MTOW/self.S*self.g)/(rho*self.C_bar*self.a*self.g)
        #mg = 2*self.MTOW*self.g*span/(rho*self.g*self.S**2*self.a)
        kg = 0.88*mg/(5.3 + mg)
        n_gust_load_pos =1 + kg*self.rho_s*Ude*EAS*self.a/(2*(self.MTOW/self.S)*self.g)
        n_gust_load_neg =1 - kg*self.rho_s*Ude*EAS*self.a/(2*(self.MTOW/self.S)*self.g)
        return n_gust_load_pos, n_gust_load_neg

    def get_flight_envelope(self):
        
        MTOW_fps = self.MTOW*2.20462262 # Convert kg to lbs
        S_fps = self.S/0.3048**2 # Convert m2 to ft2
        VC = self.Vc/0.514444 # Convert m/s to knots
        W_S_fps = MTOW_fps/S_fps
        
        VS_pos = (2*self.MTOW*self.g/(self.rho_s*self.S*self.CLmax))**0.5
        VS_neg = (2*self.MTOW*self.g/(self.rho_s*self.S*abs(self.CLmin)))**0.5
        n_pos_check = 2.1 + 24000/(MTOW_fps + 10000) # CS23.337 (a) (1)
        if self.n_pos < n_pos_check:
            self.n_pos = n_pos_check # CS23.337 (a) (1)
        if self.n_pos > 3.8:
            self.n_pos = 3.8 # CS23.337 (a) (1)

        n_neg = -0.4*self.n_pos # CS23.337 (b) (1)
        
        factor = self.calibrate_cruise_factor(W_S_fps)
        VC_min = factor*(W_S_fps)**0.5 # in knots ## CS23.335 (a) (1)

        if VC < VC_min:
            VC = VC_min # CS23.335 (a) (1)
            factor = self.calibrate_dive_factor(W_S_fps)
            VD = factor*VC # CS23.335 (b) (2)
        else:
            VD = 1.25*VC # CS23.335 (b) (1)

        VC = VC*0.51444 # convert back to m/s
        VD = VD*0.51444 # convert back to m/s

        VA_pos = VS_pos*self.n_pos**0.5 # CS23.335 (c) (1)
        VA_neg = VS_neg*abs(n_neg)**0.5 # CS23.335 (c) (1)

        VB = 85 # Estimation to be checked in plot ## # CS23.335 (d) (1)

        cases = ['Cruise', 'Dive']
        Velocity = [VC, VD]
        Density = [self.rho, self.rho]
        n_gust_pos = []
        n_gust_neg = []

        for i, case in enumerate(cases):
            V = Velocity[i]
            rho = Density[i]
            n_gust_load_pos, n_gust_load_neg = self.gust_load_factor(V, rho, case)
            n_gust_pos.append(n_gust_load_pos)
            n_gust_neg.append(n_gust_load_neg)

        VS1 = VS_pos
        if VB < VA_pos:
            VB = VA_pos
        if VB < VS1*n_gust_pos[0]**0.5:
            VB = VS1*n_gust_pos[0]**0.5
        if VB > VC:
            VB = VC - 10

        n_gust_load_pos, n_gust_load_neg = self.gust_load_factor(VB, self.rho, 'Rough_air')
        n_gust_pos.append(n_gust_load_pos)
        n_gust_neg.append(n_gust_load_neg)

        Vel_vector = np.arange(0, VD, 0.1)
        output_data = {
            'Positive Stall Speed' : VS_pos,
            'Negative Stall Speed' : VS_neg,
            'Positive Stall Line' : 0.5*self.rho_s*Vel_vector**2*self.S*self.CLmax/(self.MTOW*self.g),
            'Negative Stall Line' : 0.5*self.rho_s*Vel_vector**2*self.S*self.CLmin/(self.MTOW*self.g),
            'Instant Stall Speed' : VS1,
            'Cruise Speed' : VC,
            'Dive Speed' : VD,
            'Positive Maneouver Speed' : VA_pos,
            'Negative Maneouver Speed' : VA_neg,
            'Max Gust Intensity Speed' : VB,
            'Positive load factor' : self.n_pos,
            'Negative load factor' : n_neg,
            'Positive gust load factor' : n_gust_pos,
            'Negative gust load factor' : n_gust_neg
        }
        
        return output_data

def plot_flight_envelope(env_data, plot_gust = False, plot_verticals = False, print_labels = False, append_graph = False):

    VS_pos_line = env_data['Positive Stall Line']
    VS_neg_line = env_data['Negative Stall Line']
    VS_pos = env_data['Positive Stall Speed']
    VS_neg = env_data['Negative Stall Speed']
    VC = env_data['Cruise Speed']
    VD = env_data['Dive Speed']
    VB = env_data['Max Gust Intensity Speed']
    VA_pos = env_data['Positive Maneouver Speed']
    VA_neg = env_data['Negative Maneouver Speed']
    n_max = env_data['Positive load factor']
    n_min = env_data['Negative load factor']
    n_gust_pos = env_data['Positive gust load factor']
    n_gust_neg = env_data['Negative gust load factor']

    # Draw CLmax V-n line
    Velocity = np.arange(0, VD, 0.1)
    load_factor_pos = VS_pos_line
    load_factor_pos[load_factor_pos > n_max] = n_max

    # Draw CLmin V-n line
    load_factor_neg = VS_neg_line
    load_factor_neg[load_factor_neg < n_min] = n_min

    # Gust Line VD
    pos_line_VD = [0, VD]
    pos_line_n_VD = np.array([1, n_gust_pos[1]])
    neg_line_n_VD = np.array([1, n_gust_neg[1]])
    full_body_line_VD = np.arange(0, VD, 0.1)
    full_body_line_n_VD_pos = pos_line_n_VD[0] + (pos_line_n_VD[1] - pos_line_n_VD[0])/(pos_line_VD[1] - pos_line_VD[0])*(full_body_line_VD -  pos_line_VD[0])
    full_body_line_n_VD_neg = neg_line_n_VD[0] + (neg_line_n_VD[1] - neg_line_n_VD[0])/(pos_line_VD[1] - pos_line_VD[0])*(full_body_line_VD -  pos_line_VD[0])

    # Gust Line VC
    pos_line_VC = [0, VC]
    pos_line_n_VC = np.array([1, n_gust_pos[0]])
    neg_line_n_VC = np.array([1, n_gust_neg[0]])
    full_body_line_VC = np.arange(0, VC, 0.1)
    full_body_line_n_VC_pos = pos_line_n_VC[0] + (pos_line_n_VC[1] - pos_line_n_VC[0])/(pos_line_VC[1] - pos_line_VC[0])*(full_body_line_VC -  pos_line_VC[0])
    full_body_line_n_VC_neg = neg_line_n_VC[0] + (neg_line_n_VC[1] - neg_line_n_VC[0])/(pos_line_VC[1] - pos_line_VC[0])*(full_body_line_VC -  pos_line_VC[0])

    # Gust Line VB
    pos_line_VB = [0, VB]
    pos_line_n_VB = np.array([1, n_gust_pos[2]])
    neg_line_n_VB = np.array([1, n_gust_neg[2]])
    full_body_line_VB = np.arange(0, VB, 0.1)
    full_body_line_n_VB_pos = pos_line_n_VB[0] + (pos_line_n_VB[1] - pos_line_n_VB[0])/(pos_line_VB[1] - pos_line_VB[0])*(full_body_line_VB -  pos_line_VB[0])
    full_body_line_n_VB_neg = neg_line_n_VB[0] + (neg_line_n_VB[1] - neg_line_n_VB[0])/(pos_line_VB[1] - pos_line_VB[0])*(full_body_line_VB -  pos_line_VB[0])

    # Connect Gust lines
    gust_conn_v_line_1 = np.linspace(VB, VC, 1000)
    gust_conn_v_line_2 = np.linspace(VC, VD, 1000)
    conn_pos_gust_line_1 = n_gust_pos[2] + (n_gust_pos[0] - n_gust_pos[2])/(VC - VB)*(gust_conn_v_line_1 - VB)
    conn_pos_gust_line_2 = n_gust_pos[0] + (n_gust_pos[1] - n_gust_pos[0])/(VD - VC)*(gust_conn_v_line_2 - VC)
    conn_neg_gust_line_1 = n_gust_neg[2] + (n_gust_neg[0] - n_gust_neg[2])/(VC - VB)*(gust_conn_v_line_1 - VB)
    conn_neg_gust_line_2 = n_gust_neg[0] + (n_gust_neg[1] - n_gust_neg[0])/(VD - VC)*(gust_conn_v_line_2 - VC)

    if pos_line_n_VB.max() > n_max or pos_line_n_VC.max() > n_max:
        V_1_p_interx = InterX(0, n_max, VD, n_max, pos_line_VB[0], pos_line_n_VB[0], pos_line_VB[1], pos_line_n_VB[1])
        if V_1_p_interx < VA_pos:
            V_1_p_interx = VA_pos
        if pos_line_n_VC.max() > n_max:
            V_2_p_interx = InterX(0, n_max, VD, n_max, VC, n_gust_pos[0], VD, n_gust_pos[1])
        else:
            V_2_p_interx = InterX(0, n_max, VD, n_max, VB, n_gust_pos[2], VC, n_gust_pos[0])
        index_pos = np.logical_and(Velocity >= V_1_p_interx, Velocity < V_2_p_interx)
    else:
        V_1_p_interx = VD
        V_2_p_interx = VD
        index_pos = np.logical_and(Velocity >= V_1_p_interx, Velocity < V_2_p_interx)
    
    if neg_line_n_VB.min() < n_min or neg_line_n_VC.min() < n_min:
        if neg_line_n_VC.min() < n_min and neg_line_n_VB.min() > n_min:
            V_1_n_interx = InterX(0, n_min, VD, n_min, VB, n_gust_neg[2], VC, n_gust_neg[0])
        else:
            V_1_n_interx = InterX(0, n_min, VD,n_min, pos_line_VB[0], neg_line_n_VB[0], pos_line_VB[1], neg_line_n_VB[1])
        if neg_line_n_VC.min() < n_min:
            V_2_n_interx = InterX(0, n_min, VD, n_min, VC, n_gust_neg[0], VD, n_gust_neg[1])
        else:
            V_2_n_interx = InterX(0, n_min, VD, n_min, VB, n_gust_neg[2], VC, n_gust_neg[0])
        index_neg = np.logical_and(Velocity > V_1_n_interx, Velocity < V_2_n_interx)
    else:
        V_1_n_interx = VD
        V_2_n_interx = VD
        index_neg = np.logical_and(Velocity > V_1_n_interx, Velocity < V_2_n_interx)

    # Positive VS
    VS_p = [VS_pos, VS_pos]
    nS_p = [0, 1]

    # Negative VS
    VS_n = [VS_neg, VS_neg]
    nS_n = [-1, 0]

    # Close maneouver V-n diagram
    dive_line_v = [VD, VD]
    dive_line_n = [min(n_min, neg_line_n_VD.min()) , max(n_max, pos_line_n_VD.max())]
    stall_line_v = [VS_neg, VS_pos]
    stall_line_n = [0, 0]

    if not append_graph:
        plt.figure(figsize = (8, 6))

    plt.rcParams['font.size'] = '16'
    plt.xlabel('Equivalent air speed [m/s]')
    plt.ylabel('Load factor')
    #plt.title(' V - n Diagram')
    plt.xlim([0, VD + 10])
    plt.grid()
    box = dict(facecolor = 'white', alpha = 0.9)

    # Maneuver Folder
    draw_solid_1 = np.logical_and(Velocity >= VS_pos, Velocity <= V_1_p_interx)
    draw_solid_2 = Velocity >= V_2_p_interx
    draw_solid_3 = np.logical_and(Velocity >= VS_neg, Velocity <= V_1_n_interx)
    draw_solid_4 = Velocity >= V_2_n_interx
    plt.plot(Velocity[Velocity < VS_pos], load_factor_pos[Velocity < VS_pos], '--', linewidth = 1, color = 'k')
    plt.plot(Velocity[index_pos], load_factor_pos[index_pos], '--', linewidth = 1, color = 'k')
    plt.plot(Velocity[draw_solid_1], load_factor_pos[draw_solid_1], color = 'k')
    plt.plot(Velocity[draw_solid_2], load_factor_pos[draw_solid_2], color = 'k')
    plt.plot(Velocity[Velocity < VS_neg], load_factor_neg[Velocity < VS_neg], '--', linewidth = 1, color = 'k')
    plt.plot(Velocity[index_neg], load_factor_neg[index_neg], '--', linewidth = 1, color = 'k')
    plt.plot(Velocity[draw_solid_3], load_factor_neg[draw_solid_3], color = 'k')
    plt.plot(Velocity[draw_solid_4], load_factor_neg[draw_solid_4], color = 'k')
    plt.plot(dive_line_v, dive_line_n, color = 'k')
    plt.plot(VS_n, nS_n, color = 'k')
    plt.plot(VS_p, nS_p, color = 'k')
    plt.plot(stall_line_v, stall_line_n, color = 'k')

    if plot_gust:

        # Gust Line Dive
        plt.plot(full_body_line_VD, full_body_line_n_VD_pos, '--', color = 'k', linewidth = 1)
        trans_angle = plt.gca().transData.transform_angles(np.array((np.rad2deg((pos_line_n_VD[1] - pos_line_n_VD[0])/(pos_line_VD[1] - pos_line_VD[0])),)), pos_line_n_VD.reshape((1, 2)))[0]
        trans_angle1 = 14
        plt.plot(full_body_line_VD, full_body_line_n_VD_neg, '--', color = 'k', linewidth = 1,)
        trans_angle = plt.gca().transData.transform_angles(np.array((np.rad2deg((neg_line_n_VD[1] - neg_line_n_VD[0])/(pos_line_VD[1] - pos_line_VD[0])),)), neg_line_n_VD.reshape((1, 2)))[0]
        trans_angle2 = -14

        # Gust Line Cruise
        plt.plot(full_body_line_VC, full_body_line_n_VC_pos, '--', color = 'k', linewidth = 1)
        trans_angle = plt.gca().transData.transform_angles(np.array((np.rad2deg((pos_line_n_VC[1] - pos_line_n_VC[0])/(pos_line_VC[1] - pos_line_VC[0])),)), pos_line_n_VC.reshape((1, 2)))[0]
        trans_angle3 = 27
        plt.plot(full_body_line_VC, full_body_line_n_VC_neg, '--', color = 'k', linewidth = 1,)
        trans_angle = plt.gca().transData.transform_angles(np.array((np.rad2deg((neg_line_n_VC[1] - neg_line_n_VC[0])/(pos_line_VC[1] - pos_line_VC[0])),)), neg_line_n_VC.reshape((1, 2)))[0]
        trans_angle4 = -27
        

        # Gust Line Rough Air
        trans_angle = plt.gca().transData.transform_angles(np.array((np.rad2deg((pos_line_n_VB[1] - pos_line_n_VB[0])/(pos_line_VB[1] - pos_line_VB[0])),)), pos_line_n_VB.reshape((1, 2)))[0]
        trans_angle5 = 33
        
        plt.plot(full_body_line_VB[full_body_line_VB < V_1_p_interx], full_body_line_n_VB_pos[full_body_line_VB < V_1_p_interx], '--', color = 'k', linewidth = 1,)
        plt.plot(full_body_line_VB[full_body_line_VB >= V_1_p_interx], full_body_line_n_VB_pos[full_body_line_VB >= V_1_p_interx], color = 'k',)
        trans_angle = plt.gca().transData.transform_angles(np.array((np.rad2deg((neg_line_n_VB[1] - neg_line_n_VB[0])/(pos_line_VB[1] - pos_line_VB[0])),)), neg_line_n_VB.reshape((1, 2)))[0]
        trans_angle6 = -33
        
        plt.plot(full_body_line_VB[full_body_line_n_VB_neg >= n_min], full_body_line_n_VB_neg[full_body_line_n_VB_neg >= n_min], '--', linewidth = 1, color = 'k')
        plt.plot(full_body_line_VB[full_body_line_n_VB_neg < n_min], full_body_line_n_VB_neg[full_body_line_n_VB_neg < n_min], color = 'k')

        # Connect Gust Lines
        plt.plot(gust_conn_v_line_1[conn_pos_gust_line_1 > n_max], conn_pos_gust_line_1[conn_pos_gust_line_1 > n_max], color = 'k')
        plt.plot(gust_conn_v_line_1[conn_pos_gust_line_1 <= n_max], conn_pos_gust_line_1[conn_pos_gust_line_1 <= n_max], '--', color = 'k', linewidth = 1)
        plt.plot(gust_conn_v_line_2[conn_pos_gust_line_2 > n_max], conn_pos_gust_line_2[conn_pos_gust_line_2 > n_max], color = 'k')
        plt.plot(gust_conn_v_line_2[conn_pos_gust_line_2 <= n_max], conn_pos_gust_line_2[conn_pos_gust_line_2 <= n_max], '--', color = 'k', linewidth = 1)
        plt.plot(gust_conn_v_line_1[conn_neg_gust_line_1 < n_min], conn_neg_gust_line_1[conn_neg_gust_line_1 < n_min], color = 'k')
        plt.plot(gust_conn_v_line_1[conn_neg_gust_line_1 >= n_min], conn_neg_gust_line_1[conn_neg_gust_line_1 >= n_min], '--', color = 'k', linewidth = 1)
        plt.plot(gust_conn_v_line_2[conn_neg_gust_line_2 < n_min], conn_neg_gust_line_2[conn_neg_gust_line_2 < n_min], color = 'k')
        plt.plot(gust_conn_v_line_2[conn_neg_gust_line_2 >= n_min], conn_neg_gust_line_2[conn_neg_gust_line_2 >= n_min], '--', color = 'k', linewidth = 1)

        if print_labels:
            plt.text(0.5*sum(pos_line_VD), 0.5*sum(pos_line_n_VD), '+ gust line VD', rotation = trans_angle1, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
            plt.text(0.5*sum(pos_line_VB), 0.5*sum(neg_line_n_VB), '- gust line VB', rotation = trans_angle6, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
            plt.text(0.5*sum(pos_line_VB), 0.5*sum(pos_line_n_VB), '+ gust line VB', rotation = trans_angle5, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
            plt.text(0.5*sum(pos_line_VC), 0.5*sum(neg_line_n_VC), '- gust line VC', rotation = trans_angle4, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
            plt.text(0.5*sum(pos_line_VC), 0.5*sum(pos_line_n_VC), '+ gust line VC', rotation = trans_angle3, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
            plt.text(0.5*sum(pos_line_VD), 0.5*sum(neg_line_n_VD), '- gust line VD', rotation = trans_angle2, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)

    # Plot Ultimate load factor
    x_ax = [0, np.max(pos_line_VD)]
    y_ax = np.array([1, 1])*1.5*np.max(n_max)
    y_ax_neg = np.array([1, 1])*1.5*n_min

    plt.plot(x_ax, y_ax, '--', c = 'r')
    plt.plot(x_ax, y_ax_neg, '--', c = 'r')

    if plot_verticals:

        # Velocities dashed lines
        VA_pos_n_vec = np.linspace(0, max(n_max, pos_line_n_VB.max(), pos_line_n_VC.max(), pos_line_n_VD.max()), num = 100, endpoint = True)
        VA_pos_vec = np.ones([len(VA_pos_n_vec), 1])*VA_pos
        point_n_VB_VA = pos_line_n_VB[0] + (pos_line_n_VB[1] - pos_line_n_VB[0])/(pos_line_VB[1] - pos_line_VB[0])*(VA_pos -  pos_line_VB[0])
        master_true = np.logical_and(VA_pos_n_vec >= n_max, VA_pos_n_vec <= point_n_VB_VA)
        plt.plot(VA_pos_vec[master_true], VA_pos_n_vec[master_true], color = 'k', linewidth = 1)
        plt.plot(VA_pos_vec[np.logical_not(master_true)], VA_pos_n_vec[np.logical_not(master_true)], '--', color = 'k', linewidth = 1)
        plt.plot([VA_neg, VA_neg], [0, min(n_min, neg_line_n_VB.min(), neg_line_n_VC.min(), neg_line_n_VD.min())], '--', color = 'k', linewidth = 1)
        plt.plot([VB, VB], [min(n_min, neg_line_n_VB.min(), neg_line_n_VC.min(), neg_line_n_VD.min()), max(n_max, pos_line_n_VB.max(), pos_line_n_VC.max(), pos_line_n_VD.max())], '--', color = 'k', linewidth = 1)
        plt.plot([VC, VC], [min(n_min, neg_line_n_VB.min(), neg_line_n_VC.min(), neg_line_n_VD.min()), max(n_max, pos_line_n_VB.max(), pos_line_n_VC.max(), pos_line_n_VD.max())], '--', color = 'k', linewidth = 1)
        #plt.plot([VA_pos, VA_pos], [0, max(n_max, pos_line_n_VB.max(), pos_line_n_VC.max(), pos_line_n_VD.max())], '--', color = 'k', linewidth = 1)

    if print_labels:
        plt.text(0.5*sum([VA_pos, VA_pos]), 0.5*sum([0, max(n_max, pos_line_n_VB.max(), pos_line_n_VC.max(), pos_line_n_VD.max())]) - 0.5, 'VA+', rotation = 90, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
        plt.text(0.5*sum([VA_neg, VA_neg]), 0.5*sum([0, min(n_min, neg_line_n_VB.min(), neg_line_n_VC.min(), neg_line_n_VD.min())]) - 0.2, 'VA-', rotation = 90, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
        plt.text(0.5*sum([VB, VB]), 0.5*sum([min(n_min, neg_line_n_VB.min(), neg_line_n_VC.min(), neg_line_n_VD.min()), max(n_max, pos_line_n_VB.max(), pos_line_n_VC.max(), pos_line_n_VD.max())]) - 0.2, 'VB', rotation = 90, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
        plt.text(0.5*sum([VC, VC]), 0.5*sum([min(n_min, neg_line_n_VB.min(), neg_line_n_VC.min(), neg_line_n_VD.min()), max(n_max, pos_line_n_VB.max(), pos_line_n_VC.max(), pos_line_n_VD.max())]), 'VC', rotation = 90, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
        plt.text(0.5*sum([VD, VD]), 0.5*sum([min(n_min, neg_line_n_VB.min(), neg_line_n_VC.min(), neg_line_n_VD.min()), max(n_max, pos_line_n_VB.max(), pos_line_n_VC.max(), pos_line_n_VD.max())]), 'VD', rotation = 90, rotation_mode = 'anchor', horizontalalignment = 'center', verticalalignment = 'top', multialignment = 'center', bbox = box)
        
    if not append_graph:
        plt.tight_layout()
        plt.savefig('envelope.png', dpi = 300)
        plt.close()

def InterX(x0, y0, x1, y1, x2, y2, x3, y3):
    lambda1 = (y1 - y0)/(x1 - x0)
    lambda2 = (y3 - y2)/(x3 - x2)
    x_int = (y2 - y0 -lambda2*x2 + lambda1*x0)/(lambda1 - lambda2)
    return x_int


if __name__ == "__main__":

    inputs = {
        'MTOW' : 8489,
        'Sref' : 24.61,
        'Cruise Speed' : 115,
        'Sea level density' : 1.225,
        'CLmax' : 2.8,
        'CLmin' : -1.,
        'Limit load factor' : 3.1,
        'Gravity' : 9.81,
        'Lift curve slope' : 5.8,
        'Wing MAC' : 1.47,
        'Flight Lane' : 100, }

    flight_envelope = Flight_Envelope(inputs)
    envelope = flight_envelope.get_flight_envelope()

    plot_flight_envelope(envelope)