import openvsp as vsp
import numpy as np
import os
import json

def export2CAD(file_name, option = "STEP"):

    if "IGES" in option:
        file_type = vsp.EXPORT_IGES
        ft = ".igs"
    elif "STEP" in option:
        file_type = vsp.EXPORT_STEP
        ft = ".stp"
    else:
        file_type = None

    vsp.ReadVSPFile(file_name)
    
    vehicle_id = vsp.FindContainersWithName("Vehicle")[0]
    parm_id = vsp.FindParm(vehicle_id, "LenUnit", "STEPSettings")
    vsp.SetParmVal(parm_id, vsp.LEN_M)
    parm_id = vsp.FindParm(vehicle_id, "SplitSurfs", "STEPSettings")
    vsp.SetParmVal(parm_id, True)

    vsp.ExportFile(file_name.replace(".vsp3", ft), vsp.SET_ALL, file_type)
    vsp.ClearVSPModel()

def WriteFile(filename):
    
    vsp.WriteVSPFile(str(filename) + ".vsp3")
    vsp.ClearVSPModel()

def Mass_properties(folder_path, filename, read_from):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    vsp.InsertVSPFile(read_from + str(filename) + ".vsp3","")
    analysis = vsp.ComputeMassProps( vsp.SET_ALL, 50)
    result_type = vsp.GetAllResultsNames()
    find_results_id = vsp.FindResultsID(result_type[0],0)

    check_for_errors()
    vsp.WriteResultsCSVFile(find_results_id, folder_path + str(filename) + ".csv")
    vsp.DeleteAllResults()
    vsp.ClearVSPModel()

def Area_Properties(folder_path, file_name, name):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    vsp.ReadVSPFile(file_name)

    analysis = vsp.ComputeCompGeom(vsp.SET_SHOWN, False, vsp.COMP_GEOM_CSV_TYPE)
    results_type = vsp.GetAllResultsNames()
    find_results_id = vsp.FindResultsID(results_type[0], 0)
    vsp.WriteResultsCSVFile(find_results_id, folder_path + name + ".csv")

    print("Data extracted to folder path : %s  " % folder_path)

    check_for_errors()

    vsp.DeleteAllResults()
    vsp.ClearVSPModel()

def check_for_errors():
    errorMgr = vsp.ErrorMgrSingleton_getInstance()

    num_err = errorMgr.GetNumTotalErrors()
    for i in range(num_err):
        err = errorMgr.PopLastError()
        print("error = ", err.m_ErrorString)


def Read_Input_File(datafile):

    f = open(datafile, "r")

    MASTER = { }

    INPUTS = { }

    for item in f:
        if item[0] != "#" and item[0] != "\n" and item[0] != "%":
            partition = item.split("=")
            try:
                INPUTS.update( { partition[0] : float(partition[1]) } )
            except ValueError:
                try:
                    temp = partition[1].split(",")
                    List = []
                    for t in temp:
                        if t != "\n" and t!= " \n":
                            List.append(float(t))
                    INPUTS.update( { partition[0] : List } )
                except ValueError:
                    INPUTS.update( { partition[0] : partition[1].translate( {ord("\n"): None} ) } )
        else:
            MASTER.update( { INPUTS["Name"] : INPUTS.copy() } )
            INPUTS.clear()

    return MASTER

class Duct():

    def __init__(self, INPUTS):

        self.name = INPUTS['Name']
        self.px = INPUTS['Relative Position X']
        self.pz = INPUTS['Relative Position Z']
        self.Lf = INPUTS["Fuselage Length"]
        self.diam = INPUTS["Diameter"]
        self.chord = INPUTS["Chord"]
        self.thickness = INPUTS["Thickness"]
        self.camber = INPUTS["Camber"]
        self.camber_pos = INPUTS["Camber_pos"]

    def draw(self):

        fid = vsp.AddGeom("BODYOFREVOLUTION", "")
        vsp.SetGeomName( fid, self.name )

        vsp.SetParmVal( fid, "X_Rel_Location", "XForm", self.px*self.Lf)
        vsp.SetParmVal( fid, "Z_Rel_Location", "XForm", self.pz*self.Lf)

        vsp.SetParmVal( fid, 'Diameter', 'Design', self.diam)

        vsp.SetParmVal( vsp.GetParm( fid, "Mode", "Design"), vsp.BOR_FLOWTHROUGH)

        vsp.ChangeBORXSecShape(fid, vsp.XS_FOUR_SERIES)

        vsp.SetParmVal( fid, 'Chord', 'XSecCurve', self.chord)
        vsp.SetParmVal( fid, 'ThickChord', 'XSecCurve', self.thickness)
        vsp.SetParmVal( fid, 'Camber', 'XSecCurve', self.camber)
        vsp.SetParmVal( fid, 'CamberLoc', 'XSecCurve', self.camber_pos)


    def Get_Name(self):
        return self.name


class Box():

    def __init__(self,INPUTS):

        self.name = INPUTS["Name"]
        self.px = INPUTS["Relative Position X"]
        self.pz = INPUTS["Relative Position Z"]
        self.Lf = INPUTS["Fuselage Length"]
        self.height = INPUTS["Box Height"]
        self.width = INPUTS["Box Width"]
        self.length = INPUTS["Box Length"]
        

    def draw(self):

        fid = vsp.AddGeom( "Box", "")
        vsp.SetGeomName( fid, self.name )

        vsp.SetParmVal( fid, "X_Rel_Location", "XForm", self.px*self.Lf)
        vsp.SetParmVal( fid, "Z_Rel_Location", "XForm", self.pz*self.Lf)

        vsp.SetParmVal( fid, "Length", "Design", self.length)
        vsp.SetParmVal( fid, "Width", "Design", self.width)
        vsp.SetParmVal( fid, "Height", "Design",self.height)

    def Get_Name(self):
        return self.name



class Cabin():

    def __init__(self,INPUTS):

        self.name = INPUTS["Name"]
        self.check = INPUTS["Draw PAX"]
        self.name1 = INPUTS["Name1"]
        self.PAX = INPUTS["PAX"]
        self.seat_pitch = INPUTS["Seat Pitch"]
        self.seat_gap = INPUTS["Seat Gap"]
        self.aisle_width = INPUTS["Aisle Width"]
        self.seat_length = INPUTS["Seat Length"]
        self.seat_height = INPUTS["Seat Height"]
        self.seat_angle = INPUTS["Seat Angle"]
        self.seat_width = INPUTS["Seat Width"]
        self.rotate = INPUTS["Rotate Seats"]
        self.cabin_pos_x = INPUTS["Relative Position X"]
        self.L_seats = INPUTS["Seats on Left Side"]
        self.M_seats = INPUTS["Seats on Mid Side"]
        self.R_seats = INPUTS["Seats on Right Side"]
        self.Lf = INPUTS["Fuselage Length"]


    def draw(self):
        self.draw_Cabin()
        if self.check == "True":
            self.draw_PAX()

    def draw_Cabin(self):
        
        fid = vsp.AddGeom( "SeatGroup", "")
        vsp.SetGeomName( fid, self.name)
        self.fid = fid

        no_rows = int(self.PAX/(self.L_seats + self.R_seats + self.M_seats))
        if no_rows < 1:
            no_rows = 1

        vsp.SetParmVal( fid, "Y_Rel_Rotation", "XForm", self.rotate)
        vsp.SetParmVal( fid, "X_Rel_Location", "XForm", self.cabin_pos_x*self.Lf)
        vsp.SetParmVal( fid, "Y_Rel_Location", "XForm", -0.5*(self.seat_width + self.aisle_width))

        vsp.SetParmVal( fid, "SeatPitch", "Layout", self.seat_pitch)
        vsp.SetParmVal( fid, "SeatGap", "Layout", self.seat_gap)
        vsp.SetParmVal( fid, "AisleWidth", "Layout", self.aisle_width)

        vsp.SetParmVal( fid, "Width", "Design", self.seat_width)
        vsp.SetParmVal( fid, "SeatHeight", "Design", self.seat_height)
        vsp.SetParmVal( fid, "SeatLength", "Design", self.seat_length)
        vsp.SetParmVal( fid, "BackAngle", "Design", self.seat_angle)

        vsp.SetParmVal( fid, "NumLeft", "Layout", self.L_seats)
        vsp.SetParmVal( fid, "NumMiddle", "Layout", self.M_seats)
        vsp.SetParmVal( fid, "NumRight", "Layout", self.R_seats)

        vsp.SetParmVal( fid, "NumRow", "Layout", no_rows)

        if no_rows > 1:
            sid = vsp.AddGeom( "SeatGroup", fid)
            vsp.SetGeomName( sid, self.name)

            vsp.SetParmVal( sid, "Y_Rel_Rotation", "XForm", self.rotate)
            vsp.SetParmVal( sid, "X_Rel_Location", "XForm", self.cabin_pos_x*self.Lf + self.seat_pitch*(no_rows - 1))
            vsp.SetParmVal( fid, "Y_Rel_Location", "XForm", -0.5*(self.seat_width + self.aisle_width))

            vsp.SetParmVal( sid, "Width", "Design", self.seat_width)
            vsp.SetParmVal( sid, "SeatHeight", "Design", self.seat_height)
            vsp.SetParmVal( sid, "SeatLength", "Design", self.seat_length)
            vsp.SetParmVal( sid, "BackAngle", "Design", self.seat_angle)
            
            vsp.SetParmVal( sid, "NumLeft", "Layout", 0)
            vsp.SetParmVal( sid, "NumMiddle", "Layout", self.M_seats)
            vsp.SetParmVal( sid, "NumRight", "Layout", 0)

            vsp.SetParmVal( sid, "NumRow", "Layout", 1)


    def draw_PAX(self):

        hid = vsp.AddGeom( "HUMAN", self.fid)
        vsp.SetGeomName ( hid, self.name1 )

        vsp.SetParmVal( hid, "LenUnit", "Anthropometric", vsp.LEN_M )
        vsp.SetParmVal( hid, "MassUnit", "Anthropometric", vsp.MASS_UNIT_KG )
        vsp.SetParmVal( hid, "Mass", "Anthropometric", 87)

        vsp.SetParmVal( hid, "ElbowRt", "Pose", 80 )
        vsp.SetParmVal( hid, "ShoulderIERt", "Pose", 45 )

        vsp.SetParmVal( hid, "HipFERt", "Pose", 80 )
        vsp.SetParmVal( hid, "KneeRt", "Pose", 80 )
        vsp.SetParmVal( hid, "ShoulderABADRt", "Pose", -15)

        offset = 0.05
        vsp.SetParmVal( hid, "X_Rel_Location", "XForm", offset)
        vsp.SetParmVal( hid, "Z_Rel_Location", "XForm", 0.6 )
        vsp.SetParmVal( hid, "Y_Rel_Rotation", "XForm", 5 )


        vsp.CopyGeomToClipboard( hid )

        for i in range(int(self.PAX)-1):
            vsp.PasteGeomClipboard(hid)


        geom_ids = vsp.FindGeoms()
        Xloc = np.zeros([int(self.PAX)],dtype=float)
        Yloc = Xloc.copy()

        for i in range(int(self.PAX)):
            if i<9:
                Xloc[i] = -1*self.seat_pitch*(i) + self.cabin_pos_x*self.Lf + offset
                Yloc[i] = 0.5*(self.seat_width + self.aisle_width)
            else:
                Xloc[i] = -1*(i-9)*self.seat_pitch + self.cabin_pos_x*self.Lf + offset
                Yloc[i] = -0.5*(self.seat_width + self.aisle_width)

                if i == 18:
                    Yloc[i] = 0.0
                    Xloc[i] = offset + self.cabin_pos_x*self.Lf

        c = 0
        for i in range(len(geom_ids)):
            geom_type_name = vsp.GetGeomTypeName(geom_ids[i])
            if geom_type_name == "Human":
                vsp.SetParmVal( geom_ids[i], "X_Rel_Location", "XForm", Xloc[c])
                vsp.SetParmVal( geom_ids[i], "Y_Rel_Location", "XForm", Yloc[c])
                c += 1

    def Get_Name(self):
        return self.name


class Engine():

    def __init__(self,INPUTS):

        self.name = INPUTS["Name"]
        self.name1 = INPUTS["Name1"]
        self.Lengine = INPUTS["Engine Length"]
        self.px = INPUTS["Relative Position X Eng"]
        self.py = INPUTS["Relative Position Y Eng"]
        self.pz = INPUTS["Relative Position Z Eng"]
        self.NoBlades = INPUTS["Number of Blades"]
        self.prop_diameter = INPUTS["Propeller Diameter"]
        self.prx = INPUTS["Relative Position X Prop"]
        self.pry = INPUTS["Relative Position Y Prop"]
        self.prz = INPUTS["Relative Position Z Prop"]
        self.H = json.loads(INPUTS["XS_Height"])
        self.W = json.loads(INPUTS["XS_Width"])
        self.XL = json.loads(INPUTS["XS_Xpos_rel"])
        self.ZL = json.loads(INPUTS["XS_Zpos_rel"])
        self.Lf = INPUTS["Fuselage Length"]
        

    def draw(self):
        self.draw_Pod()
        self.draw_Propeller()

    def draw_Pod(self):
        
        fid = vsp.AddGeom( "FUSELAGE", "")
        vsp.SetGeomName( fid, self.name)

        vsp.SetParmVal( fid, "Tess_W", "Shape", 50)
        vsp.SetParmVal( fid, "Length", "Design", self.Lengine )

        vsp.InsertXSec( fid, 1, vsp.XS_ELLIPSE )                   # Insert A Cross-Section 
        vsp.SetParmVal( fid, "Ellipse_Height", "XSecCurve_2", 1 )  # Change Height
        vsp.SetParmVal( fid, "Ellipse_Width", "XSecCurve_2", 1 )   # Change Width

        vsp.CopyXSec( fid, 2 )
        vsp.PasteXSec( fid, 1)
        vsp.PasteXSec( fid, 3 )
        vsp.PasteXSec( fid, 4 )
        vsp.CutXSec( fid, 2)

        xsec_surf = vsp.GetXSecSurf( fid, 0 )                                      # Get First (and Only) XSec Surf

        num_xsecs = vsp.GetNumXSec( xsec_surf )

        for i in range(1,num_xsecs-1):

            vsp.SetParmVal( fid, "Ellipse_Height", "XSecCurve_" + str(i), self.H[i])          # Change Height
            vsp.SetParmVal( fid, "Ellipse_Width", "XSecCurve_" + str(i), self.W[i] )          # Change Width
        
        for i in range(num_xsecs):
            vsp.SetParmVal( fid, "XLocPercent", "XSec_" + str(i), self.XL[i])                 # X location
            vsp.SetParmVal( fid, "ZLocPercent", "XSec_" + str(i), self.ZL[i])                 # Z location


        vsp.SetParmVal( fid, "X_Rel_Location", "XForm", self.px*self.Lf )
        vsp.SetParmVal( fid, "Y_Rel_Location", "XForm", self.py*self.Lf )
        vsp.SetParmVal( fid, "Z_Rel_Location", "XForm", self.pz*self.Lf )


    def draw_Propeller(self):
        
        fid = vsp.AddGeom( "PROP", "")
        vsp.SetGeomName( fid, self.name1)

        vsp.SetParmVal( fid, "X_Rel_Location", "XForm", self.prx*self.Lf )
        vsp.SetParmVal( fid, "Y_Rel_Location", "XForm", self.pry*self.Lf )
        vsp.SetParmVal( fid, "Z_Rel_Location", "XForm", self.prz*self.Lf )

        vsp.SetParmVal( fid, "Diameter", "Design", self.prop_diameter)
        vsp.SetParmVal( fid, "NumBlade", "Design", self.NoBlades)

    def Get_Name(self):
        return self.name


class Fuselage():

    def __init__(self,INPUTS):

        self.fusetype = INPUTS["Fuselage XSection"]

        self.name = INPUTS["Name"]
        self.Lf = INPUTS["Fuselage Length"]
        self.Dmax = INPUTS["Max Diameter"]
        self.pz = INPUTS["Relative Position Z"]

        if self.fusetype == "Ellipse":
            self.H = [0, 5.107/74.146*INPUTS["Fuselage Length"], INPUTS["Max Diameter"], INPUTS["Max Diameter"], 1.777/74.146*INPUTS["Fuselage Length"], 0]
            self.W = [0, 6.547/74.416*INPUTS["Fuselage Length"], INPUTS["Max Diameter"], INPUTS["Max Diameter"], 1.19/74.146*INPUTS["Fuselage Length"], 0]
            self.XL = [0, 0.05494,  0.13546, 0.66117, 0.985, 1]
            self.YL = [0, 0, 0, 0, 0, 0]
            self.ZL = [0, 0.00255, 0.01864, 0.02007, 0.04316, 0.04545]
            self.T_a = [ 90, 30, 0, 0, -1.73, -90]
            self.B_a = [ 90, 10, 0, 0, -12.12, -90]
            self.R_a = [ 90, 20.77, 0, 0, -5.5, -90]
            self.T_s = [ 0.75, 0.75, 1.97, 0.75, 0.75, 1.2]
            self.R_s = [ 0.75, 0.75, 0.75, 0.75, 1.13, 1.03]
            self.B_s = [ 0.75, 0.75, 0.75, 0.75, 0.75, 1.2]
        elif self.fusetype == "Rectangular":
            scf = INPUTS["Fuselage Length"]/16.56
            self.H = [0, 1.2*scf, 1.95*scf, 1.95*scf, 0.79*scf, 0]
            self.W = [0, 1.5*scf, 1.5*scf, 1.5*scf, 0.59*scf, 0]
            self.XL = [0, 0.11697,  0.2215, 0.6875, 0.94263285, 1]
            self.YL = [0, 0, 0, 0, 0, 0]
            self.ZL = [0.005, 0.018, 0.04, 0.04, 0.05, 0.0603864]
            self.T_a = [ 45, 0, 0, 0, 0, -45]
            self.B_a = [ 45, 0, 0, 0, 0, -45]
            self.R_a = [ 45, 0, 0, 0, 0, -45]
            self.T_s = [ 0.75, 1, 1, 1, 1, 0.75]
            self.R_s = [ 0.75, 1, 1, 1, 1, 0.75]
            self.B_s = [ 0.75, 1, 1, 1, 1, 0.75]
        else:
            print("Error: Non-recognized fuselage X-Section")


    def draw(self):

        fid = vsp.AddGeom("FUSELAGE", "")
        self.hierarchy = fid
        vsp.SetGeomName( fid, self.name)

        vsp.SetParmVal( fid, "Tess_W", "Shape", 50)
        vsp.SetParmVal( fid, "Length", "Design",  self.Lf)

        if self.fusetype == "Ellipse":

            XSEC = vsp.XS_ELLIPSE
            height = "Ellipse_Height"
            width = "Ellipse_Width"

        elif self.fusetype == "Rectangular":

            XSEC = vsp.XS_ROUNDED_RECTANGLE
            height = "RoundedRect_Height"
            width = "RoundedRect_Width"

        else:
            print("Wrong Fuselage Type")

        vsp.InsertXSec( fid, 1, XSEC)                          # Insert A Cross-Section
        vsp.SetParmVal( fid, height, "XSecCurve_2", 2)         # Change Height
        vsp.SetParmVal( fid, width, "XSecCurve_2", 2)          # Change Width

        vsp.CopyXSec( fid, 2)                  
        vsp.PasteXSec( fid, 1)                 
        vsp.PasteXSec( fid, 3)
        vsp.PasteXSec( fid, 4)
        
        xsec_surf = vsp.GetXSecSurf( fid, 0 )                                                        # Get First (and Only) XSec Surf

        num_xsecs = vsp.GetNumXSec( xsec_surf )
                
        for i in range(num_xsecs):
            vsp.SetParmVal( fid, "XLocPercent", "XSec_" + str(i), self.XL[i])
            vsp.SetParmVal( fid, "YLocPercent", "XSec_" + str(i), self.YL[i])
            vsp.SetParmVal( fid, "ZLocPercent", "XSec_" + str(i), self.ZL[i])
        
        for i in range(num_xsecs):  #( int i = 0 ; i < num_xsecs ; i++ )
            xsec = vsp.GetXSec( xsec_surf, i )
            vsp.SetXSecWidthHeight( xsec, self.W[i], self.H[i])
            vsp.SetXSecContinuity( xsec, 0 )                                                                         # Set Continuity At Cross Section
            vsp.SetXSecTanStrengths( xsec, vsp.XSEC_LEFT_SIDE, self.T_s[i], self.R_s[i], self.B_s[i], self.R_s[i] )  # Set Tangent Strengths At Cross Section
            vsp.SetXSecTanAngles( xsec,vsp.XSEC_LEFT_SIDE, self.T_a[i], self.R_a[i], self.B_a[i], self.R_a[i])       # Set Tangent Angles At Cross Sectionv
            
        vsp.SetParmVal( fid, "XLocPercent", "XSec_2", self.XL[2]) # X location
        vsp.SetParmVal( fid, "Z_Rel_Location", "XForm", self.pz)
    
    def Add_Conformal(self):

        fid = vsp.AddGeom( "CONFORMAL", self.hierarchy )
        vsp.SetGeomName( fid, "Front Cargo Box" )
        parm = vsp.GetParm( fid, "UTrimFlag", "Design" )
        vsp.SetParmVal( parm, vsp.TRIM_X )
        vsp.SetParmVal( fid, "Offset", "Design", 0.1 )
        vsp.SetParmVal( fid, "UTrimMin", "Design", 0.08 )
        vsp.SetParmVal( fid, "UTrimMax", "Design", 0.25 )

    def Get_Name(self):
        return self.name


class Reinforcements():

    def __init__(self,INPUTS):

        self.podtype = INPUTS["Pod XS Type"]
        self.pod_length = INPUTS["Pod Length"]
        self.px = INPUTS["Relative Position X"]
        self.pz = INPUTS["Relative Position Z"]
        self.Lf = INPUTS["Fuselage Length"]
        self.scf = self.Lf/16.56
        self.name = INPUTS["Name"]

        self.T_a = json.loads(INPUTS["Top Side Angles"])
        self.R_a = json.loads(INPUTS["Right Side Angles"])
        self.T_s = json.loads(INPUTS["Top Side Strengths"])
        self.R_s = self.T_s.copy()

        self.W = json.loads(INPUTS["XS_Width"])
        self.H = json.loads(INPUTS["XS_Height"])


    def draw(self):

        fid = vsp.AddGeom( "FUSELAGE", "")
        vsp.SetGeomName( fid, self.name)

        vsp.SetParmVal( fid, "Tess_W", "Shape", 50)
        vsp.SetParmVal( fid, "Length", "Design", self.pod_length )

        if self.podtype == "Ellipse":

            XSEC = vsp.XS_ELLIPSE
            height = "Ellipse_Height"
            width = "Ellipse_Width"

        elif self.podtype == "Rectangular":
            
            XSEC = vsp.XS_ROUNDED_RECTANGLE
            height = "RoundedRect_Height"
            width = "RoundedRect_Width"

        else:
            print("Wrong Fuselage Type")

        vsp.InsertXSec( fid, 1, XSEC )                   # Insert A Cross-Section 
        vsp.SetParmVal( fid, height, "XSecCurve_2", 1 )  # Change Height
        vsp.SetParmVal( fid, width, "XSecCurve_2", 1 )   # Change Width

        vsp.CopyXSec( fid, 2 )
        vsp.PasteXSec( fid, 1)
        vsp.PasteXSec( fid, 3 )
        vsp.PasteXSec( fid, 4 )
        vsp.CutXSec( fid, 2)

        xsec_surf = vsp.GetXSecSurf( fid, 0 )                                      # Get First (and Only) XSec Surf

        num_xsecs = vsp.GetNumXSec( xsec_surf )

        for i in range(num_xsecs):  #( int i = 0 ; i < num_xsecs ; i++ )
            xsec = vsp.GetXSec( xsec_surf, i )
            vsp.SetXSecContinuity( xsec, 0 )                                                                         # Set Continuity At Cross Section
            vsp.SetXSecTanStrengths( xsec, vsp.XSEC_LEFT_SIDE, self.T_s[i], self.R_s[i], self.T_s[i], self.R_s[i] )  # Set Tangent Strengths At Cross Section
            vsp.SetXSecTanAngles( xsec,vsp.XSEC_LEFT_SIDE, self.T_a[i], self.R_a[i], self.T_a[i], self.R_a[i])       # Set Tangent Angles At Cross Sectionv

        for i in range(1,num_xsecs-1):
            vsp.SetParmVal( fid, height, "XSecCurve_" + str(i), self.scf*self.H[i])          # Change Height
            vsp.SetParmVal( fid, width, "XSecCurve_" + str(i), self.scf*self.W[i] )          # Change Width

        vsp.SetParmVal( fid, "X_Rel_Location", "XForm", self.px*self.Lf )
        vsp.SetParmVal( fid, "Z_Rel_Location", "XForm", self.pz*self.Lf )

    def Get_Name(self):
        return self.name


class Wing():

    def __init__(self,INPUTS):

        self.name = INPUTS["Name"]
        self.profile = INPUTS["Profile"]
        self.wpx = INPUTS["Relative Position X"]
        self.wpz = INPUTS["Relative Position Z"]
        self.Sweep = INPUTS["Sweep"]
        self.Span = INPUTS["Span"]
        self.Croot = INPUTS["Croot"]
        self.Ctip = INPUTS["Ctip"]
        self.incidence = INPUTS["Incidence"]
        self.twist = INPUTS["Twist"]
        self.dihedral = INPUTS["Dihedral"]
        self.t_c_w = INPUTS["Thickness"]
        self.Lf = INPUTS["Fuselage Length"]
        self.MovingParts = INPUTS["Moving Parts"]
        self.c_C = json.loads(INPUTS["ChordRatio"])
        self.b_B = json.loads(INPUTS["SpanRatio"])


    def draw(self):
        
        wid = vsp.AddGeom("WING", "")
        self.wid = wid
        vsp.SetGeomName( wid, self.name)
        if self.name == "Vertical_Tail":
            vsp.SetParmVal( vsp.GetParm( wid, "Sym_Planar_Flag", "Sym"), vsp.SYM_NONE)
            vsp.SetParmVal( wid, "X_Rel_Rotation", "XForm", 90)
        else:
            vsp.SetParmVal( vsp.GetParm( wid, "Sym_Planar_Flag", "Sym"), vsp.SYM_XZ)
            vsp.SetParmVal( wid, "X_Rel_Rotation", "XForm", 0)
        
        vsp.SetParmVal( wid, "X_Rel_Location", "XForm", self.wpx*self.Lf )
        vsp.SetParmVal( wid, "Z_Rel_Location", "XForm", self.wpz*self.Lf )
        vsp.SetParmVal( wid, "TotalSpan", "WingGeom", self.Span )
        vsp.SetParmVal( wid, "Sweep", "XSec_1", self.Sweep )
        vsp.SetParmVal( wid, "Root_Chord", "XSec_1", self.Croot )
        vsp.SetParmVal( wid, "Tip_Chord", "XSec_1", self.Ctip )
        vsp.SetParmVal( wid, "Twist", "XSec_1", self.twist )
        vsp.SetParmVal( wid, "Twist", "XSec_0", self.incidence )
        vsp.SetParmVal( wid, "Dihedral", "XSec_1", self.dihedral)
        vsp.SetParmVal( wid, "CapUMaxOption", "EndCap", 2)

        #vsp.InsertXSec( wid, 1, vsp.XS_SIX_SERIES)
        
        # Set tesselation values
        vsp.SetParmVal( wid, "SectTess_U", "XSec_1", 20)
        vsp.SetParmVal( wid, "Tess_W", "Shape", 20)

        xsec_surf = vsp.GetXSecSurf( wid, 0 )
        num_xsecs = vsp.GetNumXSec( xsec_surf )

        for i in range(num_xsecs):

            vsp.SetParmVal( wid, "ThickChord", "XSecCurve_" + str(i), self.t_c_w)
        
        self.insert_airfoil()

    
    def insert_airfoil(self):

        airfoil_path = self.profile + ".dat"
        xsec_surf = vsp.GetXSecSurf( self.wid, 0)
        num_xsec = vsp.GetNumXSec(xsec_surf)
        
        for i in range(num_xsec):
            xsec0 = vsp.GetXSec( xsec_surf, i )
            vsp.ChangeXSecShape( xsec_surf, i, vsp.XS_FILE_AIRFOIL )
            xsec0 = vsp.GetXSec( xsec_surf, i )

            vsp.ReadFileAirfoil( xsec0, airfoil_path )
    
    def insert_control_surfaces(self):

        offset = 0.1
        for ii in range(int(self.MovingParts)):
            Ustart, Uend = self.Get_U_W_coords(self.b_B[ii], offset, self.wid)

            vsp.AddSubSurf( self.wid, vsp.SS_CONTROL, 0)
            vsp.SetParmVal( self.wid, "UStart", "SS_Control_" + str(ii + 1), Ustart)
            vsp.SetParmVal( self.wid, "UEnd", "SS_Control_" + str(ii + 1), Uend)
            vsp.SetParmVal( self.wid, "Length_C_Start", "SS_Control_" + str(ii + 1), self.c_C[ii])
            offset = offset + Uend

    def Get_U_W_coords(self, value, offset_val, id):
        '''
        U and W coordinates are the surface parametric coordinates.
        
        In the W direction (cord direction) is needed i.e. c_i/C = 0.25 is the 25% of the chord.

        In the U direction (span direction) both end caps are included in the coordinate system i.e. calibration is needed.

        To add a control surface after the first cap, Ustart = 1/(num_xsec + 1)*initial_offset and Uend = 1/(num_xsec + 1)*End_value + 1/(num_xsec + 1)

        e.g.

        A flap with flap2wing chord ratio of 0.25 and a flap2wing span ratio of 0.5, with a 10% of the total wing span offset from root,
        has a Ustart = 1/(num_xsec + 1)*0.1 and a Uend = 1/(num_xsec + 1)*0.5 + 1/(num_xsec + 1). No changes for the chord ratio are required.

        NOTE!!!! if multi-xsecs are added with different span per section, the above values must be weighed acoording to the span ratio of each section!  
        '''

        xsec_surf = vsp.GetXSecSurf(id, 0)
        num_xsec = vsp.GetNumXSec(xsec_surf)
        offset = 1/(num_xsec + 1)*offset_val
        Ustart = 1/(num_xsec + 1) + offset
        Uend = 1/(num_xsec + 1)*value + 1/(num_xsec + 1) + offset

        return Ustart, Uend

    def Get_Name(self):
        return self.name
