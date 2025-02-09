# -*- coding: utf-8 -*-
"""
Created on 2/7/2025

This is a simple capacitor model as a federate

This model creates federate and registers it with the HELICS API.

@author: Ehab Shoubaki
eshoubak@uncc.edu
"""

import matplotlib.pyplot as plt
import helics as h
import logging
import numpy as np
import os

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def destroy_federate(fed):
    '''
    As part of ending a HELICS co-simulation it is good housekeeping to
    formally destroy a federate. Doing so informs the rest of the
    federation that it is no longer a part of the co-simulation and they
    should proceed without it (if applicable). Generally this is done
    when the co-simulation is complete and all federates end execution
    at more or less the same wall-clock time.

    :param fed: Federate to be destroyed
    :return: (none)
    '''

    # Adding extra time request to clear out any pending messages to avoid
    #   annoying errors in the broker log. Any message are tacitly disregarded.
    grantedtime = h.helicsFederateRequestTime(fed, h.HELICS_TIME_MAXTIME -1)
    status = h.helicsFederateDisconnect(fed)
    h.helicsFederateDestroy(fed)
    logger.info('Federate finalized')

def create_value_federate(fedinitstring,name,period):
    fedinfo = h.helicsCreateFederateInfo()
    # "coreType": "zmq",
    h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
    h.helicsFederateInfoSetCoreInitString(fedinfo, fedinitstring)
    # "loglevel": 1,
    h.helicsFederateInfoSetIntegerProperty(fedinfo, h.helics_property_int_log_level, 1)
    h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_period, period)
    # "uninterruptible": false,
    h.helicsFederateInfoSetFlagOption(fedinfo, h.helics_flag_uninterruptible, False)
    # "terminate_on_error": true,
    h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_TERMINATE_ON_ERROR, True)
    # "wait_for_current_time_update": true,
    h.helicsFederateInfoSetFlagOption(fedinfo, h.helics_flag_wait_for_current_time_update, True)
    fed = h.helicsCreateValueFederate(name, fedinfo)
    return fed

if __name__ == "__main__":
    
    ##########  Registering  federate and configuring with API################
    fedinitstring = " --federates=1"
    name = "Capacitor"
    period = 100e-6
    fed = create_value_federate(fedinitstring,name,period)
    logger.info(f'Created federate {name}')
    print(f'Created federate {name}')

    Vc_id = h.helicsFederateRegisterGlobalTypePublication(fed, 'Vc', 'double', 'V')
    logger.debug(f'\tRegistered publication---> Vc')

    Il_id = h.helicsFederateRegisterSubscription(fed,'Il', 'A')
    logger.debug(f'\tRegistered subscription---> Il')

    ##############  Entering Execution Mode  ##################################
    h.helicsFederateEnterExecutingMode(fed)
    logger.info('Entered HELICS execution mode')

    total_interval = 10.0
    update_interval = h.helicsFederateGetTimeProperty(
                                fed,
                                h.HELICS_PROPERTY_TIME_PERIOD)
    grantedtime = 0

    # Define capacitor value
    c_value = 0.159
    
    # Data collection lists
    time_sim = [grantedtime]
    voltage = [0.0]        # initial capacitor voltage (set to zero)

    # Publish initial voltage
    h.helicsPublicationPublishDouble(Vc_id, voltage[0])
    
    # As long as granted time is in the time range to be simulated...
    while grantedtime < total_interval:
        
        # Time request for the next physical interval to be simulated
        requested_time = (grantedtime+update_interval)
        logger.debug(f'Requesting time {requested_time}')

        grantedtime = h.helicsFederateRequestTime (fed, requested_time)
        logger.debug(f'Granted time {grantedtime}')

        # Get the inductor current discharging the capacitor
        inductor_current = h.helicsInputGetDouble(Il_id)
        logger.debug(f'\tReceived Inductor Current {inductor_current:.2f} A')

        # Calculate capacitor delta_v
        delta_v = -1/c_value*inductor_current*update_interval

        # Data collection vectors
        time_sim.append(grantedtime)
        voltage.append(voltage[-1]+delta_v)

        # Publish out new voltage
        h.helicsPublicationPublishDouble(Vc_id, voltage[-1])
        logger.debug(f'\tPublished Vc with value {voltage[-1]}')
        
    # Cleaning up HELICS stuff once we've finished the co-simulation.
    destroy_federate(fed)

    # Printing out final results graphs for comparison/diagnostic purposes.
    plt.plot(time_sim, voltage, color='tab:blue', linestyle='-')

    # Labels and title
    plt.xlabel("Time (seconds)")
    plt.ylabel("Capacitor Voltage (V)")
    plt.title("Capacitor")

    plt.savefig('Capacitor_Voltage.png', format='png')

    plt.show()
