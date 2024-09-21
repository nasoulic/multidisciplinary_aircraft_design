import subprocess
import os, shutil

class XFOIL_wrapper():

    def __init__(self):
        pass

    def defineCase(self, nacaprofile, Re, niter = 250, min_a = -8, max_a = 18, step_a = 1):
        
        self.NACAprofile = nacaprofile
        self.Re = Re
        self.Niter = niter
        self.min_a = min_a
        self.max_a = max_a
        self.step_a = step_a

    def createInputFile(self, filename):

        with open(filename, "w+") as myfile:
            myfile.write("NACA {0}\n".format(self.NACAprofile))
            myfile.write("oper\n")
            myfile.write("iter {0}\n".format(self.Niter))
            myfile.write("visc {0}\n".format(self.Re))
            myfile.write("seqp\n")
            myfile.write("pacc\n")
            myfile.write("NACA_{0}_PolarSave_Re{1}.p\n".format(self.NACAprofile, int(self.Re)))
            myfile.write("NACA_{0}_PolarDump.p\n".format(self.NACAprofile))
            myfile.write("aseq {0} {1} {2}\n".format(self.min_a, self.max_a, self.step_a))
        myfile.close()

    # def runXFOIL(self, filename):
    #     cmd_line = "{0} < {1}".format(os.path.join(self.home_dir, "xfoil.exe"), filename)
    #     subprocess.run(cmd_line, shell = True)
    #     return -1

    def runXFOIL(self, cmd_line, filename):
        with open(filename, 'r') as input_file:
            subprocess.run(cmd_line, stdin=input_file, shell=True, startupinfo=subprocess.STARTUPINFO(), creationflags=subprocess.CREATE_NO_WINDOW)
        return -1
    
    def copyFiles2Path(self, path, files):

        if not os.path.exists(os.path.join(os.getcwd(), path)):
            os.mkdir(os.path.join(os.getcwd(), path))
        
        for file in files:
            if not "Dump.p" in file and not ".dat" in file:
                shutil.copy(os.path.join(os.getcwd(), file), os.path.join(os.getcwd(), path, file))

        for file in files:
            os.remove(os.path.join(os.getcwd(), file))

def callXFOILWrapper(nacaseries, Re, home_dir, output_dir):
    xfoil_path = os.path.join(home_dir, "XFOIL/xfoil.exe")           
    if not os.path.exists(os.path.join(output_dir, "NACA{0}_Re{1}".format(nacaseries, int(Re)))):
        os.mkdir(os.path.join(output_dir, "NACA{0}_Re{1}".format(nacaseries, int(Re))))
        testfile = "naca{0}config.dat".format(nacaseries)
        testfile_path = os.path.join(os.path.join(output_dir, testfile))
        runXFOIL = XFOIL_wrapper()
        runXFOIL.defineCase(nacaseries, Re)
        runXFOIL.createInputFile(testfile)
        runXFOIL.runXFOIL(xfoil_path, testfile_path)
        runXFOIL.copyFiles2Path("NACA{0}_Re{1}".format(nacaseries, int(Re)), [testfile, "NACA_{0}_PolarSave_Re{1}.p".format(nacaseries, int(Re)), "NACA_{0}_PolarDump.p".format(nacaseries)])
    

if __name__ == "__main__":
    anaca = "4415"
    Re = 3e6
    callXFOILWrapper(anaca, Re)

    from readPolar import airfoil_polar

    af = airfoil_polar(anaca, Re)
    print(af.zero_angle_moment_coefficient())
    print(af.zero_lift_angle())
    af.plot_polar()