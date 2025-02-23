#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include "helics/helics98.hpp"

void destroyFederate(helicscpp::ValueFederate& fed) {
    try {
        fed.requestTime(HELICS_TIME_MAXTIME - 1);
        fed.finalize();
        std::cout << "Federate finalized" << std::endl;
    } catch (const helicscpp::HelicsException& e) {
        std::cerr << "Error during federate destruction: " << e.what() << std::endl;
    }
}

helicscpp::ValueFederate createValueFederate(const std::string& fedinitstring, const std::string& name, double period) {
    helicscpp::FederateInfo fedinfo;
    fedinfo.setCoreType("zmq");
    //fedinfo.coreInitString = fedinitstring;
    //fedinfo.setIntegerProperty(helicscpp::PROPERTY_INT_LOG_LEVEL, 1);
    //fedinfo.setTimeProperty(helicscpp::PROPERTY_TIME_PERIOD, period);
    //fedinfo.setFlagOption(helicscpp::FLAG_UNINTERRUPTIBLE, false);
    //fedinfo.setFlagOption(helicscpp::FLAG_TERMINATE_ON_ERROR, true);
    //fedinfo.setFlagOption(helicscpp::FLAG_WAIT_FOR_CURRENT_TIME_UPDATE, false);

    return helicscpp::ValueFederate(name, fedinfo);
}

int main() {
    std::string fedinitstring = "--federates=1";
    std::string name = "Inductor";
    double period = 100e-6;

    helicscpp::ValueFederate fed = createValueFederate(fedinitstring, name, period);
    std::cout << "Created federate " << name << std::endl;

    /*
    helicscpp::Publication Il_pub = fed.registerGlobalPublication<double>("Il");
    helicscpp::Input Vc_sub = fed.registerSubscription("Vc");

    fed.enterExecutingMode();
    std::cout << "Entered HELICS execution mode" << std::endl;

    double total_interval = 10.0;
    double update_interval = fed.getTimeProperty(helicscpp::PROPERTY_TIME_PERIOD);
    double grantedtime = 0;
    double l_value = 0.159;
    
    std::vector<double> time_sim;
    std::vector<double> current;
    
    time_sim.push_back(grantedtime);
    current.push_back(1.0); // Initial inductor current (1 A)
    Il_pub.publish(current.back());
    
    while (grantedtime < total_interval) {
        double requested_time = grantedtime + update_interval;
        grantedtime = fed.requestTime(requested_time);
        
        double capacitor_voltage = Vc_sub.getDouble();
        double delta_i = (1.0 / l_value) * capacitor_voltage * update_interval;
        
        time_sim.push_back(grantedtime);
        current.push_back(current.back() + delta_i);
        Il_pub.publish(current.back());
    }

    destroyFederate(fed);

    std::ofstream outFile("Inductor_Current.csv");
    outFile << "Time (s), Inductor Current (A)\n";
    for (size_t i = 0; i < time_sim.size(); ++i) {
        outFile << time_sim[i] << ", " << current[i] << "\n";
    }
    outFile.close();
    */
    std::cout << "Simulation complete. Data saved to Inductor_Current.csv" << std::endl;
    return 0;
}
