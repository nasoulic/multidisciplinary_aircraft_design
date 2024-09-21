
class energy_requirements(object):

    def __init__(self) -> None:        
        pass

    def energy_calculation(self, mission, power_requirements):

        energy = {}
        
        for key, item in mission.timetable.items():
            energy[key] = item/60*power_requirements[key]
        
        total_energy = 0
        for key, item in energy.items():
            total_energy = total_energy + item

        return energy, total_energy