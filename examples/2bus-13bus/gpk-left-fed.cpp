#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <helics/application_api/ValueFederate.hpp>

// GridPACK inludes
#include "mpi.h"
#include <ga.h>
#include <macdecls.h>
#include "gridpack/include/gridpack.hpp"
#include "pf_app.hpp" 

int main(int argc, char **argv) {
  // Create a FederateInfo object
  helics::FederateInfo fi;

  // Select the core type, set one core per federate
  fi.coreType = helics::CoreType::ZMQ;
  fi.coreInitString = "--federates=1";

  // Logging in debug mode
  fi.setProperty(HELICS_PROPERTY_INT_LOG_LEVEL,HELICS_LOG_LEVEL_DEBUG);

  // Set Simulator resolution
  double period = 1.0;
  fi.setProperty(HELICS_PROPERTY_TIME_PERIOD,period);

  // Set some flags
  fi.setFlagOption(HELICS_FLAG_UNINTERRUPTIBLE, false);
  fi.setFlagOption(HELICS_FLAG_TERMINATE_ON_ERROR, true);
  fi.setFlagOption(HELICS_FLAG_WAIT_FOR_CURRENT_TIME_UPDATE,true);

  // Create Value Federate
  helics::ValueFederate gpk_left("gridpack",fi);
  std::cout << "HELICS GridPAKC Federate created successfully." << std::endl;

  // Registering Publications and subscriptions
  auto Va_id = gpk_left.registerPublication("Va", "complex", "V");
  auto Vb_id = gpk_left.registerPublication("Vb", "complex", "V");
  auto Vc_id = gpk_left.registerPublication("Vc", "complex", "V");


  auto Sa_id = gpk_left.registerSubscription("gld_hlc_conn/Sa", "VA");
  auto Sb_id = gpk_left.registerSubscription("gld_hlc_conn/Sb", "VA");
  auto Sc_id = gpk_left.registerSubscription("gld_hlc_conn/Sc", "VA");

  // File to store simulatio signals
  std::ofstream outFile("gpk.csv");

  // Prepare GridPACK Environement
  gridpack::Environment env(argc,argv);
  gridpack::math::Initialize(&argc,&argv);

  gridpack::powerflow::PFApp app_A;
  gridpack::powerflow::PFApp app_B;
  gridpack::powerflow::PFApp app_C;
  
  // Enter execution mode (this transitions the federate from initialization to execution)
  gpk_left.enterExecutingMode();
  std::cout << "GridPACK Federate has entered execution mode." << std::endl;
  // Simulation Initialization
  double total_interval = 10.0;
  double grantedtime = 0.0;

  auto Sa = std::complex<double>(0.0,0.0);
  auto Sb = std::complex<double>(0.0,0.0);
  auto Sc = std::complex<double>(0.0,0.0);
  
  auto Va = std::complex<double>(1.0,0.0);
  auto Vb = std::complex<double>(-0.5,-0.866025);
  auto Vc = std::complex<double>(-0.5,0.866025);

  // Publish Initial center voltage
  Va_id.publish(Va*2400.0);
  Vb_id.publish(Vb*2400.0);
  Vc_id.publish(Vc*2400.0);

  // Setting up the GridPACK Environement

  // Entering simulation loop
  while (grantedtime < total_interval) {
    // Request time
    grantedtime = gpk_left.requestTime(grantedtime+period);

    // Get Sa from gridlab-d
    Sa = Sa_id.getValue<std::complex<double>>()/100000000.0;
    Sb = Sb_id.getValue<std::complex<double>>()/100000000.0;
    Sc = Sc_id.getValue<std::complex<double>>()/100000000.0;

    // pass S's to GridPACK and get back V's
    app_A.execute(argc, argv, Va, Sa);
    app_B.execute(argc, argv, Vb, Sb);
    app_C.execute(argc, argv, Vc, Sc);

    // Log boundary signals
    outFile << "Time (s): "<< grantedtime << "\n";
    outFile << "S received from Gridlab-D, Sa: " << Sa << " Sb: " << Sb << " Sc: " << Sc <<"\n";
    outFile << "Updated Vv by GridPACK, Va: " << Va << " Vb: " << Vb << " Vc: " << Vc << "\n\n"; 
    
    // Publish new Center Bus Voltage
    Va_id.publish(Va*2400.0);
    Vb_id.publish(Vb*2400.0);
    Vc_id.publish(Vc*2400.0);
  }

  outFile << "End of Cosimulation.";
  outFile.close();

  // Terminate GridPACK Math Libraries
  gridpack::math::Finalize();

  // Finalize the federate to clean up and disconnect from the HELICS core
  gpk_left.finalize();
  std::cout << "Federate finalized." << std::endl;

  return 0;
}
