Multidisciplinary Novel Aircraft Design Application
Welcome to the Multidisciplinary Novel Aircraft Design application.
This application provides a user-friendly interface to assist in various stages of aircraft design, configuration, and evaluation.
        
Features:
- Configure different components of the aircraft.
- Perform sizing calculations for the aircraft.
- Evaluate Life Cycle Assessment (LCA) and Direct Operating Costs (DOC).
- View the aircraft design and export designs in different formats.
- Configure the Thermal Management System (TMS).
        
Explore the different menus and buttons to make the most of this application.
For more detailed information, consult the user manual or help documentation.

Installation Guidelines:

1) Download OpenVSP-3.38.0-win64 from the following website: https://openvsp.org/download.php

	NOTE: If you don't want to use the latest version of OpenVSP you can skip this step. A working version of OpenVSP is 
	located in the ./aircraft_visualisation/OpenVSP-3.38.0-win64 path.

2) Follow the instructions found on the OpenVSP-3.38.0-win64/python/README.md file to create the conda environment supporting the OpenVSP python API (Summarised below).
	2.1) Open a command prompt window and navigate to relative path: ./OpenVSP-3.38.0-win64/python/
	2.2) run <conda env create -f .\environment.yml>
	2.3) run <conda activate mdhead_vsp>
	2.4) run <pip install -r requirements-dev.txt>

3) Install openmdao and PyQt5 in the new vsp conda environment:
	3.1) Acivate the conda environment
	3.2) run <pip install openmdao>
	3.3) run <pip install PyQt5>
	3.4) run <pip install pyDOE2>

4) Copy the OpenVSP-3.38.0-win64/CustomScripts fodler to your Users file directory (e.g. C:\Users\<myusername>\CustomScripts)

5) Done.

NOTE: This project has been built using Python 3.11. Variations in the Python version may require additional actions to install the project.

Copyright © 2023
Laboratory of Fluid Mechanics and Turbomachinery
Aristotle University of Thessaloniki
All rights reserved.

Developer: Christos P. Nasoulis
Contact e-mail: nasoulic@meng.auth.gr

The author(s) disclaims all warranties with regard to this software,
including all implied warranties of merchantability and fitness.
In no event the author(s) shall be held liable for any special, indirect
or consequential damages or any damages whatsoever resulting from
loss of use, data or profits, either in an action of contract,
negligence or other tortious action, arising out of or in connection
with the use or performance of this software.

This software has been developed as a partial fulfilment of the Developer's PhD.

Data produced with this software may not be published or disclosed to
any third party without the written authorisation of the author(s). 