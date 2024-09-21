from acsizing.standard_atmosphere import Standard_Atmosphere as SA
from acsizing.find_intersection import InterX, sum_values_up_to_key
import numpy as np

class mission_profile(object):

    def __init__(self):
        pass

    def load_mission_inputs(self, climb_alt_60, climb_mach, cruise_alt, cruise_mach,
                            loiter_alt, loiter_mach, reserves_alt, mission_range, mission_reserves, end_takeoff, 
                            max_climb_angle, max_dive_angle, climb_angle, dive_angle):
        self.climb_angle = climb_angle
        self.climb_alt_60 = climb_alt_60
        self.climb_mach = climb_mach
        self.cruise_alt = cruise_alt
        self.cruise_mach = cruise_mach
        self.dive_angle = dive_angle
        self.loiter_alt = loiter_alt
        self.loiter_mach = loiter_mach
        self.reserves_alt = reserves_alt
        self.mission_range = mission_range
        self.mission_reserves = mission_reserves
        self.take_off_end_alt = end_takeoff
        self.max_climb_angle = max_climb_angle
        self.max_dive_angle = max_dive_angle
        self.max_divclimb_angle = self.max_climb_angle

        self.inputs = [self.mission_range, self.mission_reserves, self.loiter_alt, self.take_off_end_alt,
                       self.cruise_alt, self.cruise_alt, self.climb_mach, self.cruise_mach, self.cruise_mach,
                       self.climb_mach, self.loiter_mach, self.max_climb_angle, self.max_dive_angle, self.max_divclimb_angle]


    def build_mission_phases(self):

        self.mission_phases = {
            #    'Design Point' : { 'a' : 0, 'i' : 0, 'gamma' : 3, 'alt' : 3048., 'M' : 0.32, 'accel' : 0, 'ang_accel' : 0 },
            'Climb' : { 'a' : 0, 'i' : 0, 'gamma' : self.climb_angle, 'alt' : self.climb_alt_60, 'M' : self.climb_mach, 'accel' : 0, 'ang_accel' : 0 },
            'Cruise' : { 'a' : 0, 'i' : 0, 'gamma' : 0, 'alt' : self.cruise_alt, 'M' : self.cruise_mach, 'accel' : 0, 'ang_accel' : 0 },
            'Descent' : { 'a' : 0, 'i' : 0, 'gamma' : self.dive_angle, 'alt' : self.climb_alt_60, 'M' : self.climb_mach, 'accel' : 0, 'ang_accel' : 0 },
            'Hold' : { 'a' : 0, 'i' : 0, 'gamma' : 0, 'alt' : self.loiter_alt, 'M' : self.loiter_mach, 'accel' : 0, 'ang_accel' : 0},
            'DivCruise' : { 'a' : 0, 'i' : 0, 'gamma' : 0, 'alt' : self.reserves_alt, 'M' : self.cruise_mach, 'accel' : 0, 'ang_accel' : 0},
            }

    def define_mision(self):

        self.build_mission_phases()

        self.toc_alt = self.mission_phases["Cruise"]["alt"] # m
        self.div_toc_alt = self.mission_phases["DivCruise"]["alt"] # m
        self.divclimb_mach = self.mission_phases["Climb"]["M"]
        self.divcruise_mach = self.mission_phases["DivCruise"]["M"]
        self.cruise_mach = self.mission_phases["Cruise"]["M"]
        self.climb_mach = self.mission_phases["Climb"]["M"]
        self.approach_mach = self.loiter_mach
                
        self.timetable = {
            'Taxi-out' : 9,
            'Take-off' : 2,
            'Climb' : 0,
            'Cruise' : 0,
            'Descent' : 0,
            'Approach and Landing' : 6,
            'Taxi-in' : 5,
            'Overshoot' : 6,
            'DivClimb' : 0,
            'DivCruise' : 0,
            'DivDescent' : 0,
            'Hold' : 30,
            'Div Approach and Landing' : 6,
        }

        self.alttable = {
            'Taxi-out' : 0,
            'Take-off' : self.take_off_end_alt,
            'Climb' : self.toc_alt,
            'Cruise' : self.toc_alt,
            'Descent' : self.loiter_alt,
            'Approach and Landing' : 0,
            'Taxi-in' : 0,
            'Overshoot' : self.take_off_end_alt,
            'DivClimb' : self.div_toc_alt,
            'DivCruise' : self.div_toc_alt,
            'DivDescent' : self.loiter_alt,
            'Hold' : self.loiter_alt,
            'Div Approach and Landing' : 0,
        }

        self.distance = {
            'Taxi-out' : 0,
            'Take-off' : 2000,
            'Climb' : 0,
            'Cruise' : 0,
            'Descent' : 0,
            'Approach and Landing' : 0,
            'Overshoot' : 2000,
            'DivClimb' : 0,
            'DivCruise' : 0,
            'DivDescent' : 0,
            'Hold' : 62*1800,
            'Div Approach and Landing' : 0,
            'Taxi-in' : 0,
        }

    def build_mission(self):

        roc_avg, glide0 = self.climb('Climb', self.take_off_end_alt, self.toc_alt, self.climb_mach, self.cruise_mach, self.max_climb_angle, 0.1)
        self.distance['Climb'] = glide0
        rod_avg, glide1 = self.climb('Descent', self.toc_alt, self.loiter_alt, self.cruise_mach, self.approach_mach, 0.1, abs(self.max_dive_angle))
        self.distance['Descent'] = glide1
        self.cruise('Cruise', self.toc_alt, self.cruise_mach, glide0, glide1, self.mission_range)
        self.distance['Cruise'] = self.mission_range - glide0 - glide1
        divroc_avg, div_glide0 = self.climb('DivClimb', self.loiter_alt, self.div_toc_alt, self.divclimb_mach, self.divcruise_mach, self.max_climb_angle, 0.1)
        self.distance['DivClimb'] = div_glide0
        divrod_avg, div_glide1 = self.climb('DivDescent', self.div_toc_alt, self.loiter_alt, self.divcruise_mach, self.approach_mach, 0.1, abs(self.max_dive_angle))
        self.distance['DivDescent'] = div_glide1
        self.cruise('DivCruise', self.div_toc_alt, self.divcruise_mach, div_glide0, div_glide1, self.mission_reserves)
        self.distance['DivDescent'] = div_glide1

        
        res = InterX().intersection_point((sum_values_up_to_key(self.timetable, "Overshoot"), self.alttable["Overshoot"]), (sum_values_up_to_key(self.timetable, "DivClimb"), self.alttable["DivClimb"]),
                                          (sum_values_up_to_key(self.timetable, "DivCruise"), self.alttable["DivCruise"]), (sum_values_up_to_key(self.timetable, "DivDescent"), self.alttable["DivDescent"]))

        res1 = InterX().intersection_point((sum_values_up_to_key(self.timetable, "Take-off"), self.alttable["Take-off"]), (sum_values_up_to_key(self.timetable, "Climb"), self.alttable["Climb"]),
                                          (sum_values_up_to_key(self.timetable, "Cruise"), self.alttable["Cruise"]), (sum_values_up_to_key(self.timetable, "Descent"), self.alttable["Descent"]))
        
        if res:
            if res[1] < self.div_toc_alt:
                roc_avg, glide0 = self.climb('Climb', self.take_off_end_alt, self.toc_alt, self.climb_mach, self.cruise_mach, self.max_climb_angle, 0.1)
                self.distance['Climb'] = glide0
                rod_avg, glide1 = self.climb('Descent', self.toc_alt, self.loiter_alt, self.cruise_mach, self.approach_mach, 0.1, abs(self.max_dive_angle))
                self.distance['Descent'] = glide1
                self.cruise('Cruise', self.toc_alt, self.cruise_mach, glide0, glide1, self.mission_range)
                self.distance['Cruise'] = self.mission_range - glide0 - glide1
                divroc_avg, div_glide0 = self.climb('DivClimb', self.loiter_alt, res[1], self.divclimb_mach, self.divcruise_mach, self.max_climb_angle, 0.1)
                self.distance['DivClimb'] = div_glide0
                divrod_avg, div_glide1 = self.climb('DivDescent', res[1], self.loiter_alt, self.divcruise_mach, self.approach_mach, 0.1, abs(self.max_dive_angle))
                self.distance['DivDescent'] = div_glide1
                self.timetable["DivCruise"] = 0
                self.distance["DivCruise"] = 0
                self.alttable["DivClimb"] = res[1]
                self.alttable["DivCruise"] = res[1]
                self.distance['DivDescent'] = div_glide1

        if res1:
            if res1[1] < self.toc_alt:

                roc_avg, glide0 = self.climb('Climb', self.take_off_end_alt, res1[1], self.climb_mach, self.cruise_mach, self.max_climb_angle, 0.1)
                self.distance['Climb'] = glide0
                rod_avg, glide1 = self.climb('Descent', res1[1], self.loiter_alt, self.cruise_mach, self.approach_mach, 0.1, abs(self.max_dive_angle))
                self.distance['Descent'] = glide1
                self.timetable["Cruise"] = 0
                self.distance["Cruise"] = 0
                self.alttable["Climb"] = res1[1]
                self.alttable["Cruise"] = res1[1]
                self.distance['Cruise'] = self.mission_range - glide0 - glide1
                if res[1] < self.div_toc_alt:
                    div_toc_alt = res[1]
                else:
                    div_toc_alt = self.div_toc_alt
                divroc_avg, div_glide0 = self.climb('DivClimb', self.loiter_alt, div_toc_alt, self.divclimb_mach, self.divcruise_mach, self.max_climb_angle, 0.1)
                self.distance['DivClimb'] = div_glide0
                divrod_avg, div_glide1 = self.climb('DivDescent', div_toc_alt, self.loiter_alt, self.divcruise_mach, self.approach_mach, 0.1, abs(self.max_dive_angle))
                self.distance['DivDescent'] = div_glide1
                self.timetable["DivCruise"] = 0
                self.distance["DivCruise"] = 0
                self.alttable["DivClimb"] = div_toc_alt
                self.alttable["DivCruise"] = div_toc_alt
                self.distance['DivDescent'] = div_glide1

        self.total_mission_time = 0
        for key, item in self.timetable.items():
            self.total_mission_time = self.total_mission_time + item

    def mission_strategy_series(self, power_requirement, Pgt, Pem, Nem, Pmax_chrg, electric_mode, conventional_mode):
        
        power_strategy = {}

        for key in self.timetable.keys():
            power_strategy[key] = { 'Ptotal' : 0, 'Pel' : 0, 'Pgt' : 0, 'P_chrg avail' : 0, 'Etotal' : 0, 'Eel' : 0, 'Egt' : 0, 'Echrg' : 0 }

        for phase in electric_mode:
            power_strategy[phase] = { 'Ptotal' : power_requirement[phase], 'Pel' : power_requirement[phase],
                                      'Pgt' : 0, 'P_chrg avail' : Pgt,
                                      'Etotal' : power_requirement[phase]*self.timetable[phase]/60,
                                      'Eel' :  power_requirement[phase]*self.timetable[phase]/60,
                                      'Egt' : 0,
                                      'Echrg' : 0 }
        
        for phase in conventional_mode:
            if Pgt - power_requirement[phase] > 0:
                power_strategy[phase] = { 'Ptotal' : power_requirement[phase], 'Pel' : 0,
                                        'Pgt' : power_requirement[phase], 'P_chrg avail' : Pgt - power_requirement[phase],
                                        'Etotal' : power_requirement[phase]*self.timetable[phase]/60,
                                        'Eel' :  0,
                                        'Egt' : power_requirement[phase]*self.timetable[phase]/60,
                                        'Echrg' :  (Pgt - power_requirement[phase])*self.timetable[phase]/60}
            else:
                raise ValueError(' P_gt < P_th required for mission phase %s . Increase gas generator power.' %phase)


        for phase in power_requirement.keys():
            if phase not in electric_mode and phase not in conventional_mode:
                if power_requirement[phase] - Pgt < 0:
                    power_strategy[phase] = {   'Ptotal' : power_requirement[phase], 'Pel' : 0,
                                                'Pgt' : Pgt, 'P_chrg avail' : 0,
                                                'Etotal' : power_requirement[phase]*self.timetable[phase]/60,
                                                'Eel' :  (power_requirement[phase] - Pgt)*self.timetable[phase]/60,
                                                'Egt' : Pgt*self.timetable[phase]/60,
                                                'Echrg' : 0 }
                else:
                    power_strategy[phase] = {   'Ptotal' : power_requirement[phase], 'Pel' : power_requirement[phase] - Pgt,
                                                'Pgt' : Pgt, 'P_chrg avail' : 0,
                                                'Etotal' : power_requirement[phase]*self.timetable[phase]/60,
                                                'Eel' :  (power_requirement[phase] - Pgt)*self.timetable[phase]/60,
                                                'Egt' : Pgt*self.timetable[phase]/60,
                                                'Echrg' : 0 }

        recup_en = 0
        for phase, items in power_strategy.items():
            if not items['Pel'] > 0:
                if items['P_chrg avail'] > Pmax_chrg:
                    items['Echrg'] = Pmax_chrg*self.timetable[phase]/60
                else:
                    items['Echrg'] = items['P_chrg avail']*self.timetable[phase]/60
                recup_en = recup_en + items['Echrg']
            if items['Pel'] > Nem*Pem:
                raise ValueError('Pel required > 4*Pem. Increase power per EM.')
        
        return power_strategy, recup_en

    def mission_strategy_parallel(self, power_requirement, DoH, electric_mode, conventional_mode):
        
        power_strategy = {}

        for key in self.timetable.keys():
            power_strategy[key] = { 'Ptotal' : 0, 'Pel' : 0, 'Pgt' : 0, 'P_chrg avail' : 0, 'Etotal' : 0, 'Eel' : 0, 'Egt' : 0, 'Echrg' : 0 }

        for phase in electric_mode:
            power_strategy[phase] = { 'Ptotal' : power_requirement[phase], 'Pel' : power_requirement[phase],
                                      'Pgt' : 0, 'P_chrg avail' : power_requirement[phase]*(1 - DoH),
                                      'Etotal' : power_requirement[phase]*self.timetable[phase]/60,
                                      'Eel' :  power_requirement[phase]*self.timetable[phase]/60,
                                      'Egt' : 0,
                                      'Echrg' : 0 }
        
        for phase in conventional_mode:
            # if power_requirement[phase]*(1 - DoH) - power_requirement[phase] > 0:
                power_strategy[phase] = { 'Ptotal' : power_requirement[phase], 'Pel' : 0,
                                        'Pgt' : power_requirement[phase], 'P_chrg avail' : 0,
                                        'Etotal' : power_requirement[phase]*self.timetable[phase]/60,
                                        'Eel' :  0,
                                        'Egt' : power_requirement[phase]*self.timetable[phase]/60,
                                        'Echrg' :  0 }
            # else:
                # raise ValueError(' P_gt < P_th required for mission phase %s . Increase gas generator power.' %phase)


        for phase in power_requirement.keys():
            if phase not in electric_mode and phase not in conventional_mode:
                power_strategy[phase] = {   'Ptotal' : power_requirement[phase], 'Pel' : power_requirement[phase]*DoH,
                                            'Pgt' : power_requirement[phase]*(1 - DoH), 'P_chrg avail' : 0,
                                            'Etotal' : power_requirement[phase]*self.timetable[phase]/60,
                                            'Eel' :  power_requirement[phase]*DoH*self.timetable[phase]/60,
                                            'Egt' : power_requirement[phase]*(1 - DoH)*self.timetable[phase]/60,
                                            'Echrg' : 0 }

        recup_en = 0
        
        return power_strategy, recup_en

    def mission_simulation(self, power_strategy, soc, mf, mf_seg, e_mode, allow_chrg):

        flag = False
        
        phases = [key for key in power_strategy.keys()]

        energy_flow = {}
        phases2emode = []

        for i in range(len(phases) - 1):
            if allow_chrg:
                recup_ebat = power_strategy[phases[i]]['Echrg']
            else:
                recup_ebat = 0.
            soc = soc - power_strategy[phases[i]]['Eel'] + recup_ebat
            mf = mf - mf_seg[phases[i]]
            energy_flow[phases[i]] = { 'SOC' : soc, 'Fuel mass' : mf}

            if soc > power_strategy[phases[i + 1]]['Etotal']:
                if phases[i + 1] not in e_mode:
                    phases2emode.append(phases[i + 1])
            
            if soc < 0:
                flag = True

        return energy_flow, phases2emode, flag
    
    def climb(self, name, alt0, alt1, m0, m1, gamma0, gamma1):

        ## Climb Phase BEGIN ##

        climb_alt = np.linspace(alt0, alt1, num = 21, endpoint = True)
        climb_mach = np.linspace(m0, m1, num = 21, endpoint = True)
        climb_vel = np.array([])
        roc = np.array([])

        for i, m in enumerate(climb_mach):
            atm = SA('Metric', climb_alt[i])
            climb_vel = np.append(climb_vel, atm[3]*m)

        time2climb = np.array([])
        climb_angle = np.radians(np.linspace(gamma0, gamma1, num = 21, endpoint = True))
        glide = 0

        for i in range(len(climb_alt) - 1):
            dy = abs(climb_alt[i + 1] - climb_alt[i])
            v_avg = 0.5*(climb_vel[i] + climb_vel[i + 1])
            vv = v_avg*np.sin(climb_angle[i])
            roc = np.append(roc, vv)
            vx = v_avg*np.cos(climb_angle[i])
            glide = glide + vx*dy/vv
            time2climb = np.append(time2climb, dy/vv)

        self.timetable[name] = sum(time2climb)/60

        ## Climb Phase END ##

        return np.average(roc), glide

    def cruise(self, name, alt, m, glide0, glide1, mission_range):

        ## Cruise Phase BEGIN ##

        cr_atm = SA('Metric', alt)
        cruise_vel = np.array([ m for i in range(15)])*cr_atm[3]
        cruise_range = np.linspace(glide0, mission_range - glide1, num = 15, endpoint = True)
        
        time2cruise = np.array([])

        for i in range(len(cruise_range) - 1):
            v_avg = 0.5*(cruise_vel[i] + cruise_vel[i + 1])
            dx = cruise_range[i + 1] - cruise_range[i]
            time2cruise = np.append(time2cruise, dx/v_avg)

        self.timetable[name] = sum(time2cruise)/60

        ## Cruise Phase END ##

    def plot_misison_profile(self, showfig = False):

        import matplotlib.pyplot as plt

        t = []
        a = []

        for key, item in self.timetable.items():
            t.append(item)
            a.append(self.alttable[key]/100/0.3048)

        plt.figure()
        plt.plot(np.cumsum(t), a)
        plt.scatter(np.cumsum(t), a)
        plt.xlabel('Mission time [min]')
        plt.ylabel('Flight altitude [FL]')
        plt.grid()
        plt.tight_layout()
        plt.savefig('mission.png', dpi = 300)
        
        if showfig:
            plt.show()
        else:
            plt.close()

    def export_csv(self):

        self.build_mission()

        with open('mission_duration.csv', 'w+') as f:
            for key, item in self.timetable.items():
                f.write('%s, %f, %f\n' %(key, item, self.distance[key]))
        f.close()

