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
  fi.setFlagOption(HELICS_FLAG_WAIT_FOR_CURRENT_TIME_UPDATE,false);

  // Create Value Federate
  helics::ValueFederate Inductor("Inductor",fi);
  std::cout << "HELICS Inductor Federate created successfully." << std::endl;

  // Registering Publications and subscriptions
  auto Il_id = Inductor.registerPublication("Il", "double", "A");
  auto Vc_id = Inductor.registerSubscription("Capacitor/Vc", "V");

  // Enter execution mode (this transitions the federate from initialization to execution)
  Inductor.enterExecutingMode();
  std::cout << "Federate has entered execution mode." << std::endl;
  // Simulation Initialization
  double total_interval = 10.0;
  double grantedtime = 0.0;
  double l_value = 0.159;
  double capacitor_voltage = 0.0;
  double delta_i = 0.0;

  // Data collection vectors
  std::vector<double> time_sim;
  std::vector<double> current;

  time_sim.push_back(grantedtime);
  current.push_back(1.0);

  // Publish Initial current
  Il_id.publish(current.back());

  // Entering simulation loop
  while (grantedtime < total_interval) {
    // Request time
    grantedtime = Inductor.requestTime(grantedtime+period);

    // Get Capacitor Voltage charging the inductor, calculate delta_i
    capacitor_voltage = Vc_id.getDouble();
    delta_i = (1.0 / l_value) * capacitor_voltage * period;

    // Store updates
    time_sim.push_back(grantedtime);
    current.push_back(current.back() + delta_i);

    // Publish new inductor current
    Il_id.publish(current.back());
  }

  // Write results into CSV file
  std::ofstream outFile("../outputs/Inductor_Current.csv");
  outFile << "Time (s), Inductor Current (A)\n";
  for (size_t i = 0; i < time_sim.size(); ++i) {
    outFile << time_sim[i] << ", " << current[i] << "\n";
  }
  outFile.close();

  
  // Finalize the federate to clean up and disconnect from the HELICS core
  Inductor.finalize();
  std::cout << "Federate finalized." << std::endl;

  return 0;
}
