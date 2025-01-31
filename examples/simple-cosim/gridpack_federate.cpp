#include <helics/cpp98/Federate.hpp>
#include <helics/cpp98/ValueFederate.hpp>
#include <helics/cpp98/Publication.hpp>
#include <helics/cpp98/Input.hpp>
#include <helics/cpp98/helicsExceptions.hpp>
#include <iostream>
#include <complex>

int main(int argc, char *argv[]) {
    try {
        // Create FederateInfo object for initializing the federate
        helicscpp::FederateInfo fi;
        fi.setCoreInit("--federates=1");  // Set initialization string
        fi.setCoreType(HELICS_CORE_TYPE_ZMQ);  // Set core type (ZMQ)

        // Create a ValueFederate instance
        helicscpp::ValueFederate fed("gridpack", fi);

        // Register publications (voltages)
        std::cout << "Registering publications..." << std::endl;
        helicscpp::Publication voltage_pub_A = fed.registerGlobalPublication("gridpack/voltage_A", "complex", "");
        helicscpp::Publication voltage_pub_B = fed.registerGlobalPublication("gridpack/voltage_B", "complex", "");
        helicscpp::Publication voltage_pub_C = fed.registerGlobalPublication("gridpack/voltage_C", "complex", "");
        std::cout << "Publications registered successfully." << std::endl;

        // Register subscription (load current)
        std::cout << "Registering subscription..." << std::endl;
        helicscpp::Input load_current_sub = fed.registerSubscription("load_meter/current");
        std::cout << "Subscription registered successfully." << std::endl;

        // Enter the execution state
        fed.enterExecutingMode();
        std::cout << "Federate entered execution mode." << std::endl;

        // Simulation loop for 10 time steps
        for (int t = 0; t < 10; ++t) {
            // Request time advancement
            std::cout << "Requesting time advancement to: " << t + 1 << std::endl;
            fed.requestTime(t + 1.0);

            // Retrieve load current from subscription
            std::complex<double> load_current = load_current_sub.getComplex();
            std::cout << "Received load current: " << load_current << " at time step " << t << std::endl;

            // For demonstration purposes, we assume a simple computation here
            std::complex<double> voltage_A = std::complex<double>(load_current.real() * 1.1, load_current.imag() * 1.1);
            std::complex<double> voltage_B = std::complex<double>(load_current.real() * 1.2, load_current.imag() * 1.2);
            std::complex<double> voltage_C = std::complex<double>(load_current.real() * 1.3, load_current.imag() * 1.3);

            // Publish voltages
            voltage_pub_A.publish(voltage_A);
            voltage_pub_B.publish(voltage_B);
            voltage_pub_C.publish(voltage_C);
            std::cout << "Published voltages at time step " << t << std::endl;
        }

        // Finalize the federate
        fed.finalize();
        std::cout << "Federate finalized successfully." << std::endl;
    } catch (const helicscpp::HelicsException& e) {
        std::cerr << "HELICS Error: " << e.what() << std::endl;
        return -1;
    }

    return 0;
}
