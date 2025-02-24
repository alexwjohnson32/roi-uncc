#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <helics/application_api/ValueFederate.hpp>

int main() {
  // Create a FederateInfo object
  helics::FederateInfo fi;

  // Select the core type, set one core per federate
  fi.coreType = helics::CoreType::ZMQ;
  fi.coreInitString = "--federates=1";

  // Logging in debug mode
  fi.setProperty(HELICS_PROPERTY_INT_LOG_LEVEL,HELICS_LOG_LEVEL_DEBUG);

  // Set Simulator resolution
  double period = 100e-6;
  fi.setProperty(HELICS_PROPERTY_TIME_PERIOD,period);

  // Set some flags
  fi.setFlagOption(HELICS_FLAG_UNINTERRUPTIBLE, false);
  fi.setFlagOption(HELICS_FLAG_TERMINATE_ON_ERROR, true);
  fi.setFlagOption(HELICS_FLAG_WAIT_FOR_CURRENT_TIME_UPDATE,true);

  // Create Value Federate
  helics::ValueFederate Capacitor("Capacitor",fi);
  std::cout << "HELICS Capacitor Federate created successfully." << std::endl;

  // Registering Publications and subscriptions
  auto Vc_id = Capacitor.registerPublication("Vc", "double", "V");
  auto Il_id = Capacitor.registerSubscription("Inductor/Il", "A");

  // Enter execution mode (this transitions the federate from initialization to execution)
  Capacitor.enterExecutingMode();
  std::cout << "Federate has entered execution mode." << std::endl;

  // Simulation Initialization
  double total_interval = 10.0;
  double grantedtime = 0.0;
  double c_value = 0.159;
  double inductor_current = 0.0;
  double delta_v = 0.0;

  // Data collection vectors
  std::vector<double> time_sim;
  std::vector<double> voltage;

  time_sim.push_back(grantedtime);
  voltage.push_back(0.0);

  // Publish Initial voltage
  Vc_id.publish(voltage.back());

  // Entering simulation loop
  while (grantedtime < total_interval) {
    // Request time
    grantedtime = Capacitor.requestTime(grantedtime+period);

    // Get Inductor current, calculate delta_v
    inductor_current = Il_id.getDouble();
    delta_v = (-1.0 / c_value) * inductor_current * period;

    // Store updates
    time_sim.push_back(grantedtime);
    voltage.push_back(voltage.back() + delta_v);

    // Publish new Capacitor voltage
    Vc_id.publish(voltage.back());
  }

  // Write results into CSV file
  std::ofstream outFile("Capacitor_Voltage.csv");
  outFile << "Time (s), Capacitor Voltage (V)\n";
  for (size_t i = 0; i < time_sim.size(); ++i) {
    outFile << time_sim[i] << ", " << voltage[i] << "\n";
  }
  outFile.close();

  
  // Finalize the federate to clean up and disconnect from the HELICS core
  Capacitor.finalize();
  std::cout << "Federate finalized." << std::endl;

  return 0;
}
