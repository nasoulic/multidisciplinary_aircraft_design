from acsizing.aircraft_performance import aircraft_performance
from acsizing.aircraft_energy_requirements import energy_requirements
from acsizing.electric_motor_sizing import axial_flux_motor
from acsizing.cable_sizing import cables
from acsizing.battery_sizing import battery_pack
from acsizing.gas_turbine_model import gas_turbine
from acsizing.aircraft_sizing import aircraft_sizing
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QProgressBar
import json
import random
import copy
import threading

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculating...")
        self.progress_bar = QProgressBar(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)

class aircraft_sizing_wrapper(object):

    def __init__(self, window):
        self.window = window
        self.mass_matrix = {}

    def run_acsizing_wrapper(self, mission, propulsion, settings, tlars, uncertainty = False, DoE = False, doe_iter = 0):

        # self.acsizing_wrapper(mission, propulsion, settings, tlars)
        
        self.loading_dialog = LoadingDialog(self.window)
        self.loading_dialog.show()

        self.worker_thread = threading.Thread(target=self.acsizing_wrapper, args=(mission, propulsion, settings, tlars, uncertainty, DoE, doe_iter))
        self.worker_thread.run()

    def acsizing_wrapper(self, mission, propulsion, settings, tlars, uncertainty = False, DoE = False, doe_iter = 0):


        '''
        ----------------------------------------------------------------------------------------------
                                U   N   P   A   C   K       I   N   P   U   T   S 
        ----------------------------------------------------------------------------------------------
        '''

        # Unpack inputs here
        AR = float(tlars["Target Aspect Ratio [-]"])
        CLmax = float(tlars["Target Max Lift Coefficient [-]"])
        PAX = int(tlars["PAX"])
        Crew = int(tlars["Crew"])
        WPAX = float(tlars["Passenger weight [kg]"])
        N = float(propulsion.eps.eps_inputs["Electric motor revolutions per min [rpm]"].text())
        Nem = float(propulsion.eps.eps_inputs["Number of electric motors [-]"].text())
        
        if uncertainty:
            source_hybridization_factor = random.uniform(float(propulsion.powertrain_specs_lb["Fuel to Total Energy ratio"].text()), float(propulsion.powertrain_specs_ub["Fuel to Total Energy ratio"].text()))
            load_hybridization_factor = random.uniform(float(propulsion.powertrain_specs_lb["Electric to Total Power ratio"].text()), float(propulsion.powertrain_specs_ub["Electric to Total Power ratio"].text()))
            eta_b2s = random.uniform(float(propulsion.eps.eps_inputs_lb["Battery to shaft efficiency [%]"].text())/100, float(propulsion.eps.eps_inputs_ub["Battery to shaft efficiency [%]"].text())/100)
            Vsys = random.uniform(float(propulsion.eps.eps_inputs_lb["System voltage [V]"].text()), float(propulsion.eps.eps_inputs_ub["System voltage [V]"].text()))            
            Sp_dcdc = random.uniform(float(propulsion.eps.eps_inputs_lb["Specific power (electronics) [kW/kg]"].text()), float(propulsion.eps.eps_inputs_ub["Specific power (electronics) [kW/kg]"].text()))
            Sp_inv = random.uniform(float(propulsion.eps.eps_inputs_lb["Specific power (electronics) [kW/kg]"].text()), float(propulsion.eps.eps_inputs_ub["Specific power (electronics) [kW/kg]"].text()))
            Sp_conv = random.uniform(float(propulsion.eps.eps_inputs_lb["Specific power (electronics) [kW/kg]"].text()), float(propulsion.eps.eps_inputs_ub["Specific power (electronics) [kW/kg]"].text()))
            Sp_gen = random.uniform(float(propulsion.eps.eps_inputs_lb["Specific power (electronics) [kW/kg]"].text()), float(propulsion.eps.eps_inputs_ub["Specific power (electronics) [kW/kg]"].text()))
            Se = random.uniform(float(propulsion.eps.eps_inputs_lb["Battery specific energy [kWh/kg]"].text()), float(propulsion.eps.eps_inputs_ub["Battery specific energy [kWh/kg]"].text()))
            sfc_reduciton_to_2014 = random.uniform(float(propulsion.powertrain_specs_lb["Gas Turbine SFC reduction compared to EIS 2014 [%]"].text())/100, float(propulsion.powertrain_specs_ub["Gas Turbine SFC reduction compared to EIS 2014 [%]"].text())/100)
            tms_mass = random.uniform(float(propulsion.powertrain_specs_lb["Thermal Management System Mass [kg]"].text()), float(propulsion.powertrain_specs_ub["Thermal Management System Mass [kg]"].text()))
            P_gas_gen = random.uniform(float(propulsion.powertrain_specs_lb["Gas Generator power output [kW]"].text()), float(propulsion.powertrain_specs_ub["Gas Generator power output [kW]"].text()))
        elif DoE:            
            source_hybridization_factor = propulsion.include_in_doe["Fuel to Total Energy ratio"][doe_iter]
            load_hybridization_factor = propulsion.include_in_doe["Electric to Total Power ratio"][doe_iter]
            eta_b2s = propulsion.eps.include_in_doe["Battery to shaft efficiency [%]"][doe_iter]/100
            Vsys = propulsion.eps.include_in_doe["System voltage [V]"][doe_iter]
            Sp_dcdc = propulsion.eps.include_in_doe["Specific power (electronics) [kW/kg]"][doe_iter]
            Sp_inv = propulsion.eps.include_in_doe["Specific power (electronics) [kW/kg]"][doe_iter]
            Sp_conv = propulsion.eps.include_in_doe["Specific power (electronics) [kW/kg]"][doe_iter]
            Sp_gen = propulsion.eps.include_in_doe["Specific power (electronics) [kW/kg]"][doe_iter]
            Se = propulsion.eps.include_in_doe["Battery specific energy [kWh/kg]"][doe_iter]
            sfc_reduciton_to_2014 = propulsion.include_in_doe["Gas Turbine SFC reduction compared to EIS 2014 [%]"][doe_iter]/100
            tms_mass = propulsion.include_in_doe["Thermal Management System Mass [kg]"][doe_iter]
            P_gas_gen = propulsion.include_in_doe["Gas Generator power output [kW]"][doe_iter]
        else:
            source_hybridization_factor = float(propulsion.powertrain_specs["Fuel to Total Energy ratio"].text())
            load_hybridization_factor = float(propulsion.powertrain_specs["Electric to Total Power ratio"].text())
            eta_b2s = float(propulsion.eps.eps_inputs["Battery to shaft efficiency [%]"].text())/100
            Vsys = float(propulsion.eps.eps_inputs["System voltage [V]"].text())
            Sp_dcdc = float(propulsion.eps.eps_inputs["Specific power (electronics) [kW/kg]"].text())
            Sp_inv = float(propulsion.eps.eps_inputs["Specific power (electronics) [kW/kg]"].text())
            Sp_conv = float(propulsion.eps.eps_inputs["Specific power (electronics) [kW/kg]"].text())
            Sp_gen = float(propulsion.eps.eps_inputs["Specific power (electronics) [kW/kg]"].text())
            Se = float(propulsion.eps.eps_inputs["Battery specific energy [kWh/kg]"].text())
            sfc_reduciton_to_2014 = float(propulsion.powertrain_specs["Gas Turbine SFC reduction compared to EIS 2014 [%]"].text())/100
            tms_mass = float(propulsion.powertrain_specs["Thermal Management System Mass [kg]"].text())
            P_gas_gen = float(propulsion.powertrain_specs["Gas Generator power output [kW]"].text())

        data = {
                'source_hybridization_factor': source_hybridization_factor,
                'load_hybridization_factor': load_hybridization_factor,
                'eta_b2s': eta_b2s,
                'Vsys': Vsys,
                'Sp_dcdc': Sp_dcdc,
                'Sp_inv': Sp_inv,
                'Sp_conv': Sp_conv,
                'Sp_gen': Sp_gen,
                'Se': Se,
                'sfc_reduction_to_2014': sfc_reduciton_to_2014,
                'tms_mass': tms_mass,
                'P_gas_gen': P_gas_gen
            }
        
        # Write the dictionary to a JSON file
        with open('acsizing_inputs.json', 'w') as f:
            json.dump(data, f, indent=4)
        f.close()

        # Initial guesses
        CD0 = 0.0286    # Parasite Drag Initial Guess
        MTOW = 8618.    # Maximum Take-Off Mass Initial Guess [kg]
        Sref = 45.      # Main Wing Reference Area Initial Guess [m2]
        

        '''
        ----------------------------------------------------------------------------------------------
                                S   I   Z   I   N   G       L   O   O   P   
        ----------------------------------------------------------------------------------------------
        '''

        flag = False
        converged = False
        iteration = 0
        cum_err = 0

        while not converged:

            '''
            ----------------------------------------------------------------------------------------------
            S   T   A   R   T       P   O   W   E   R       R   E   Q   U   I   R   E   M   E   N   T   

                                        E   S   T   I   M   A   T   I   O   N    
            ----------------------------------------------------------------------------------------------
            '''

            power_requirement = {}

            aircraft_per = aircraft_performance()
            for key, item in mission.mission_phases.items():
                aircraft_per.mission_phase(item)
                aircraft_per.aircraft_characteristics(mtow = MTOW, tsls = 30000, eta_p = propulsion.propeller.efficiency[key], Sref = Sref, CD0 = CD0, AR = AR, CLmax = CLmax)
                power = aircraft_per.power_calculation()
                power_requirement[key] = round(power/1000)


            power_requirement['Take-off'] = round(power_requirement['Climb']/0.85)
            power_requirement['Taxi-out'] = round(0.07*power_requirement['Take-off'])
            power_requirement['Approach and Landing'] = power_requirement['Descent']
            power_requirement['Taxi-in'] = power_requirement['Taxi-out']
            power_requirement['Overshoot'] = power_requirement['Take-off']
            power_requirement['DivClimb'] = power_requirement['Climb']
            power_requirement['DivCruise'] = power_requirement['Cruise']
            power_requirement['DivDescent'] = power_requirement['Descent']
            power_requirement['Div Approach and Landing'] = power_requirement['Approach and Landing']

            '''
            ----------------------------------------------------------------------------------------------
            S   T   A   R   T       E   N   E   R   G   Y       R   E   Q   U   I   R   E   M   E   N   T   

                                        E   S   T   I   M   A   T   I   O   N    
            ----------------------------------------------------------------------------------------------
            '''

            aircraft_energy_req = energy_requirements()
            energy, total_energy = aircraft_energy_req.energy_calculation(mission, power_requirement)

            '''
            ----------------------------------------------------------------------------------------------
            P   R   O   P   U   L   S   I   O   N       S   Y   S   T   E   M       S   I   Z   I   N   G  
            ----------------------------------------------------------------------------------------------
            '''

            e_bat = total_energy*(1 - source_hybridization_factor)  # Battery energy                      [kWh]

            Pmax = power_requirement['Take-off']

            if not "Conventional" in settings.configuration:
                if "Parallel" in settings.configuration:
                    P_gt = Pmax*(1 - load_hybridization_factor)
                    P_em = Pmax*load_hybridization_factor

                    Pbat = P_em/eta_b2s

                    m_generator = 0
                    m_converter = 0

                else:
                    P_gt = P_gas_gen                                            # Initial Guess Gas Generator shaft power output    [kW]
                    Pbat = Pmax/eta_b2s                                         # selected for the N-1 case with GT failure
                    P_em = Pmax/(Nem - 1)                                       # selected for the N-1 case with EM failure

                e_motor = axial_flux_motor()
                em_out = e_motor.size_motor(P_em, N, Vsys)

                m_emotor = Nem*em_out[0]

                m_dcdc = Pbat/Sp_dcdc
                m_inverter = Nem*P_em*1.2/Sp_inv                        # assume 20 % power increment for inverter
                m_converter = 1.2*P_gt/Sp_conv                          # assune 20 % power increment for converter
                m_generator = 1.2*P_gt/Sp_gen                           # assune 20 % power increment for generator

                dc_cable = cables()
                dc_cable.cable_characteristics()
                m_cab_dc, A_cab_dc = dc_cable.dc_cable_sizing(Pbat, Vsys)

                ac_cable = cables()
                ac_cable.cable_characteristics()
                m_cab_ac, A_cab_ac = ac_cable.ac_cable_sizing(P_em, Vsys)

                bat_pack = battery_pack()
                bat_pack.cell_dimensions()
                bat_pack.pack_dimensions()
                bat_pack.operating_constraints()
                resAr = bat_pack.size_battery(Pbat, e_bat, Se, Vsys, chrg_r = 1/3, dis_r = 1)
                W_bat = resAr[0]
                Bat_capacity = resAr[1]*resAr[2]*resAr[-3]*bat_pack.cell_V_nom*1e-3

                eps_mass = m_emotor + m_dcdc + m_inverter + m_converter + m_generator

                self.mass_matrix["EPS"] = {}
                self.mass_matrix["EPS"]["Motor"] = m_emotor
                self.mass_matrix["EPS"]["Inverter"] = m_inverter
                self.mass_matrix["EPS"]["DCDC"] = m_dcdc
                self.mass_matrix["EPS"]["Converter"] = m_converter
                self.mass_matrix["EPS"]["Generator"] = m_generator
                self.mass_matrix["EPS"]["DC Cables"] = m_cab_dc
                self.mass_matrix["EPS"]["AC Cables"] = m_cab_ac
                self.mass_matrix["TMS"] = {}
                self.mass_matrix["TMS"]["Cooling System"] = tms_mass

            else:
                P_gt = Pmax*(1 - load_hybridization_factor)
                P_em = Pmax*load_hybridization_factor
                Bat_capacity = 0
                eps_mass = 0
                W_bat = 0
                m_cab_ac = 0
                m_cab_dc = 0
                tms_mass = 0

                self.mass_matrix["EPS"] = {}
                self.mass_matrix["EPS"]["Motor"] = 0
                self.mass_matrix["EPS"]["DCDC"] = 0
                self.mass_matrix["EPS"]["Inverter"] = 0
                self.mass_matrix["EPS"]["Converter"] = 0
                self.mass_matrix["EPS"]["Generator"] = 0
                self.mass_matrix["EPS"]["DC Cables"] = 0
                self.mass_matrix["EPS"]["AC Cables"] = 0
                self.mass_matrix["TMS"] = {}
                self.mass_matrix["TMS"]["Cooling System"] = 0

            el_mode = settings.el_mode
            conv_mode = settings.conv_mode

            if "Series" in settings.configuration:
                p_strategy, recup_en = mission.mission_strategy_series(power_requirement, P_gt, P_em, Nem, resAr[3], el_mode, conv_mode)
            else:
                p_strategy, recup_en = mission.mission_strategy_parallel(power_requirement, load_hybridization_factor, el_mode, conv_mode)

            if "Series" in settings.configuration:
                if propulsion.gt_from_GUI:
                    gas_turb = gas_turbine()
                    gas_turb.gas_generator_characteristics_from_GUI(propulsion.gt_from_GUI)
                else:
                    gas_turb = gas_turbine()
                    gas_turb.gas_generator_characteristics()
            else:
                if propulsion.gt_from_GUI:
                    gas_turb = gas_turbine()
                    gas_turb.update_turboprop_characteristics_from_GUI(propulsion.gt_from_GUI, sfc_reduciton_to_2014)
                else:
                    gas_turb = gas_turbine()
                    gas_turb.turbobprop_characteristics(sfc_red = sfc_reduciton_to_2014)

            m_fuel_segment = {}
            m_fuel = 0
            for key, item in power_requirement.items():
                t = mission.timetable[key]*60
                mf = gas_turb.fuel_requirement(p_strategy[key]['Pgt']/propulsion.propeller.efficiency[key], gas_turb.efficiency[key])
                m_fuel_segment[key] = mf*t
                m_fuel = m_fuel + mf*t

            w_gt = gas_turb.mass

            e_flow, phases2emode, soc_flag = mission.mission_simulation(p_strategy, Bat_capacity, m_fuel, m_fuel_segment, el_mode, settings.allow_charging)

            if "Series" in settings.configuration:
                if soc_flag:
                    P_gt = P_gt + 10

            '''
            ----------------------------------------------------------------------------------------------
                    S   T   A   R   T       S   I   Z   I   N   G       P   R   O   C   E   S   S   
            ----------------------------------------------------------------------------------------------
            '''
            
            aircraft = aircraft_sizing()
            aircraft.mass_matrix["EPS"] = self.mass_matrix["EPS"]
            aircraft.mass_matrix["TMS"] = self.mass_matrix["TMS"]
            aircraft.define_geometry(CLmax, AR, power_requirement['Take-off']*1e3, power_requirement['Cruise']*1e3, propulsion.propeller.efficiency, w_gt, settings)
            aircraft.apply_advanced_settings(settings)
            aircraft.define_mission(mission)
            aircraft.Geometry_Sizing(MTOW)
            old_MTOW = copy.copy(MTOW)

            MTOW, Sref, CD0 = aircraft.design_evaluation(MTOW, eps_mass, tms_mass, m_fuel, W_bat, m_cab_dc, m_cab_ac, PAX, Crew, WPAX, settings)

            err = abs(old_MTOW - MTOW)
            cum_err = cum_err + 1/err
            if cum_err*100 < 99:
                self.loading_dialog.progress_bar.setValue(int(cum_err)*100)
            else:
                self.loading_dialog.progress_bar.setValue(99)
            if err < 0.5:
                converged = True
                self.loading_dialog.progress_bar.setValue(100)
            
            if iteration > 1e5:
                flag = True
                converged = True

            iteration += 1

        aircraft.mass_matrix["Aircraft"] = aircraft.aircraft_mass_breakdown

        self.loading_dialog.accept()
        '''
        ----------------------------------------------------------------------------------------------
                W   R   I   T   E       O   U   T   P   U   T       F   I   L   E   S     
        ----------------------------------------------------------------------------------------------
            '''

        if soc_flag:
            print('Battery initial SOC not sufficient for selected power management strategy')

        self.aircraft_data = {
            'MTOM' : aircraft.aircraft_mass_breakdown['MTOM'],
            'OEW' : aircraft.aircraft_mass_breakdown['Empty'],
            'Fuel' : aircraft.aircraft_mass_breakdown['Fuel'], 
            'Propulsion_mass': aircraft.aircraft_mass_breakdown['Installed_Engines'] + eps_mass,
            'Wing mass' : aircraft.aircraft_mass_breakdown['Main_Wing'],
            'Vertical Tail mass' : aircraft.aircraft_mass_breakdown['Vertical_Tail'],
            'Horizontal Tail mass' : aircraft.aircraft_mass_breakdown['Horizontal_Tail'],
            'Fuselage mass' : aircraft.aircraft_mass_breakdown['Fuselage'],
            'Landing gear mass' : aircraft.aircraft_mass_breakdown['Landing_Gear'],
            'Fuselage length' : aircraft.GEOMETRY['Fuselage']['Length'],
            'Fuselage diameter' : aircraft.GEOMETRY['Fuselage']['Max Diameter'],
            'Wing span' : aircraft.GEOMETRY['Main_Wing']['Span'],
            'Wing reference area' : aircraft.GEOMETRY['Main_Wing']['Sref'],
            'Max power' : power_requirement['Take-off'],
            'Total energy' : total_energy,
            'On-board energy' : aircraft.aircraft_mass_breakdown['Fuel']*gas_turb.fuel_energy_density/gas_turb.fuel_rho + Bat_capacity,
            'Batteries mass' : W_bat,
            'Batteries energy' : Bat_capacity,
            'P_em' : P_em,
            'P_gt' : P_gt,
            'DoH' : load_hybridization_factor,
        }

        self.to_DOC = {
            'Block_Time' : mission.total_mission_time,
            'Fuel_Burn' : aircraft.aircraft_mass_breakdown['Fuel'],
            'Battery_Energy' : Bat_capacity,
            'Payload' : aircraft.aircraft_mass_breakdown['Payload'],
            'MTOW' : aircraft.aircraft_mass_breakdown['MTOM'],
            'Range' : (mission.mission_range + mission.mission_reserves)*1e-3,
            'Empty_Weight' : aircraft.aircraft_mass_breakdown['Empty'],
            'Propulsion_Weight' : aircraft.aircraft_mass_breakdown['Installed_Engines'] + eps_mass,
            'Wing_Span' : aircraft.GEOMETRY['Main_Wing']['Span'],
            'Fuselage_Length' : aircraft.GEOMETRY['Fuselage']['Length'],
            'Vtakeoff' : aircraft.VTO,
            'P_GT_max' : Nem*P_gt,
            'P_EM_max' : Nem*P_em,
        }

        self.to_lca = {
            'maximum range' : (mission.mission_range + mission.mission_reserves)*1e-3/1.852,
            'empty mass' : aircraft.aircraft_mass_breakdown['Empty'],
            'fuel' : aircraft.aircraft_mass_breakdown['Fuel'],
            'batteries' : aircraft.aircraft_mass_breakdown['Batteries'],
            'battery energy' : Bat_capacity,
            'flight time' : mission.total_mission_time/60,
            'flight level' : mission.cruise_alt/0.3048/100,
            'taxi time' : (mission.timetable['Taxi-in'] + mission.timetable['Taxi-out'])/60,
            'main landing gear' : aircraft.aircraft_mass_breakdown['Landing_Gear']*0.85,
            'nose landing gear' : aircraft.aircraft_mass_breakdown['Landing_Gear']*0.15,
            'fuselage' : aircraft.aircraft_mass_breakdown['Fuselage'],
            'main wing' : aircraft.aircraft_mass_breakdown['Main_Wing'],
            'vertical stabilizer' : aircraft.aircraft_mass_breakdown['Vertical_Tail'],
            'horizontal stabilizer' : aircraft.aircraft_mass_breakdown['Horizontal_Tail'],
            'engines' : aircraft.aircraft_mass_breakdown['Installed_Engines'],
            'fuel at cruise' : m_fuel_segment['Cruise'] + m_fuel_segment['DivCruise'],
            'approach time' : mission.timetable['Approach and Landing'] + mission.timetable['Div Approach and Landing'] + mission.timetable['Descent'] + mission.timetable['DivDescent'] + mission.timetable['Hold'],
            'approach fuel' :   (m_fuel_segment['Approach and Landing'] + m_fuel_segment['Div Approach and Landing'] + m_fuel_segment['Descent'] + m_fuel_segment['DivDescent'] + m_fuel_segment['Hold'])/(mission.timetable['Approach and Landing'] + mission.timetable['Div Approach and Landing'] + mission.timetable['Descent'] + mission.timetable['DivDescent'] + mission.timetable['Hold'])/60,
            'idle time' : mission.timetable['Taxi-in'] + mission.timetable['Taxi-out'],
            'idle fuel' : (m_fuel_segment['Taxi-in'] + m_fuel_segment['Taxi-out'])/(mission.timetable['Taxi-in'] + mission.timetable['Taxi-out'])/60,
            'take-off time' : mission.timetable['Overshoot'] + mission.timetable['Take-off'],
            'take-off fuel' : (m_fuel_segment['Take-off'] + m_fuel_segment['Overshoot'])/(mission.timetable['Take-off'] + mission.timetable['Overshoot'])/60,
            'climb time' : mission.timetable['Climb'] + mission.timetable['DivClimb'],
            'climb fuel' : (m_fuel_segment['Climb'] + m_fuel_segment['DivClimb'])/(mission.timetable['Climb'] + mission.timetable['DivClimb'])/60,
            'eps_weight' : eps_mass,
        }

        self.export_results(aircraft, mission, power_requirement, m_fuel_segment)

        self.aircraft = aircraft

    def export_results(self, aircraft, mission, power_requirement, m_fuel_segment):

        mission.export_csv()
        mission.plot_misison_profile()

        with open("./vsp_aircraft_input_file.dat", "w+") as f:
            for key, item in aircraft.GEOMETRY.items():
                f.write("Name={0}\n".format(key))
                for inkey, initem in item.items():
                    f.write("{1}={0}\n".format(initem, inkey))
                    # if isinstance(item, str):
                    #     f.write(inkey + "=%s\n" %initem)
                    # elif isinstance(initem, list):
                    #     f.write(inkey + "=")
                    #     for i in initem:
                    #         f.write(str(i) + ",")
                    #     f.write("\n")
                    # elif isinstance(initem, float):
                    #     f.write(inkey + "=%f\n" % initem)
                    # elif isinstance(initem, int):
                    #     f.write(inkey + "=%f\n" %initem)
                f.write("Fuselage Length={0}\n".format(aircraft.GEOMETRY["Fuselage"]["Length"]))
                f.write("#########################################\n")

        units = ['[m]' for i in range(len(aircraft.cable_len.keys()))]
        i = 0
        with open("./Cable_length_report.dat", "w+") as f:
            for key, item in aircraft.cable_len.items():
                f.write("%s, %f, %s\n" %(key, item, units[i]))
                i += 1
        f.close()

        with open('./lca_inputs.csv', 'w+') as f:
            for key, item in self.to_lca.items():
                f.write('%s, %f\n' %(key, item))
        f.close()

        with open("./doc_inputs.csv", "w+") as f:
            for key, item in self.to_DOC.items():
                f.write('%s, %f\n' %(key, item))
        f.close()

        with open('./power_requirements.csv', 'w+') as f:
            for key in mission.timetable.keys():
                item = power_requirement[key]
                f.write('%s, %f\n' %(key, item))
        f.close()

        with open('./fuel_requirements.csv', 'w+') as f:
            for key in mission.timetable.keys():
                item = m_fuel_segment[key]
                f.write('%s, %f\n' %(key, item))
        f.close()

        with open('./aircraft_comparison_specs.csv', 'w+') as f:
            for key, item in self.aircraft_data.items():
                f.write('%s, %f \n' %(key, item))
            f.close()

        with open('./Design_Report.csv', 'w+') as f:
            f.write('#####Geometrical Characteristics#####\n')
            for key, item in aircraft.GEOMETRY.items():
                f.write('\n### %s ###\n\n' %key)
                for inkey, initem in item.items():
                    f.write('%s, %s \n' %(inkey, initem))
            f.write('\n######Aircraft mass breakdown#####\n\n')
            for key, item in aircraft.aircraft_mass_breakdown.items():
                f.write('\n%s, %s \n' %(key, item))
        f.close()

        with open("aircraft_weight_report.dat", "w+") as myfile:
            for key, item in aircraft.mass_matrix.items():
                for inkey, initem in item.items():
                    myfile.write("{0}, {1}\n".format(inkey, initem))
        myfile.close()