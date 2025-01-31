EPIC,UNCC
SIMPLE-EXAMPLE
Co-Simulation example using : helics, gridlabd d , and GRIDPACK. 

- basic gridlabd module to reprsent source , switch and load.
- Basic GRIDPACK module to represent a 2-bus transmission grid with a source, and a load,
- the switch status is fetched by the switch_controller.py file using https request. The status is published to helics file.
- gridlab-d subscribes to this switch status and updates the switch accordingly.
- the load current measured using the recorder confirms for the switch closing and opening.

- the 2nd python file st_control.py is used to update the IOT switch status every 5 mins. This folder is used so that the time sync happens between all the federates as expected.
For the first time running the example, you need to compile the gridpack model with this command:(According to your directory)

g++ -o gridpack_federate gridpack_federate.cpp -I/usr/local/include/helics -L/usr/local/lib -lhelics -lstdc++

and after that, you need to run HELICS command to run the master json file:

 helics run --path=switch_cosim_runner.json
