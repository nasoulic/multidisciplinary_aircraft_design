# from aircraft_visualization.create_aircraft import build_aircraft
import subprocess, os

def launch_openvsp(input_file):

    home_dir = os.getcwd()

    vsp_dir = "./aircraft_visualization/OpenVSP-3.38.0-win64/"
    vsp_exe = os.path.join(vsp_dir, "vsp.exe")

    command = f'"{vsp_exe}" "{input_file}"'

    result = subprocess.run(command, shell = True, cwd = home_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    

if __name__ == "__main__":
    launch_openvsp("dummy.dat")