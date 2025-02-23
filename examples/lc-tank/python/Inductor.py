# -*- coding: utf-8 -*-
"""
Created on 2/7/2025

This is a simple indoctor model as a federate

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
    # "period": 1e-6,
    h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_period, period)
    # "uninterruptible": false,
    h.helicsFederateInfoSetFlagOption(fedinfo, h.helics_flag_uninterruptible, False)
    # "terminate_on_error": true,
    h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_TERMINATE_ON_ERROR, True)
    # "wait_for_current_time_update": false,
    h.helicsFederateInfoSetFlagOption(fedinfo, h.helics_flag_wait_for_current_time_update, False)
    # "name": "Battery",
    fed = h.helicsCreateValueFederate(name, fedinfo)
    return fed

if __name__ == "__main__":
    
    ##########  Registering  federate and configuring with API################
    fedinitstring = " --federates=1"
    name = "Inductor"
    period = 100e-6
    fed = create_value_federate(fedinitstring,name,period)
    logger.info(f'Created federate {name}')
    print(f'Created federate {name}')

    Il_id = h.helicsFederateRegisterGlobalTypePublication(fed, 'Il', 'double', 'A')
    logger.debug(f'\tRegistered publication---> Vc')

    Vc_id = h.helicsFederateRegisterSubscription(fed,'Vc', 'V')
    logger.debug(f'\tRegistered subscription---> Il')

    sub_count = h.helicsFederateGetInputCount(fed)
    logger.debug(f'\tNumber of subscriptions: {sub_count}')

    pub_count = h.helicsFederateGetPublicationCount(fed)
    logger.debug(f'\tNumber of publications: {pub_count}')

    ##############  Entering Execution Mode  ##################################
    h.helicsFederateEnterExecutingMode(fed)
    logger.info('Entered HELICS execution mode')

    total_interval = 10.0
    update_interval = h.helicsFederateGetTimeProperty(
                                fed,
                                h.HELICS_PROPERTY_TIME_PERIOD)
    grantedtime = 0

    # Define capacitor value
    l_value = 0.159
    
    # Data collection lists
    time_sim = [grantedtime]
    current = [1.0]        # initial inductor current (set to 1 A)

    # Publish initial current
    h.helicsPublicationPublishDouble(Il_id, current[0])

    # As long as granted time is in the time range to be simulated...
    while grantedtime < total_interval:
        
        # Time request for the next physical interval to be simulated
        requested_time = (grantedtime+update_interval)
        logger.debug(f'Requesting time {requested_time}')

        grantedtime = h.helicsFederateRequestTime (fed, requested_time)
        logger.debug(f'Granted time {grantedtime}')

        # Get the capacitor voltage charging the inductor
        capacitor_voltage = h.helicsInputGetDouble(Vc_id)
        logger.debug(f'\tReceived Capacitor Voltage {capacitor_voltage:.2f} V')

        # Calculate inductor delta_i
        delta_i = 1/l_value*capacitor_voltage*update_interval

        # Data collection vectors
        time_sim.append(grantedtime)
        current.append(current[-1]+delta_i)

        # Publish out new voltage
        h.helicsPublicationPublishDouble(Il_id, current[-1])
        logger.debug(f'\tPublished Il with value {current[-1]:.2f}')
        
    # Cleaning up HELICS stuff once we've finished the co-simulation.
    destroy_federate(fed)

    # Printing out final results graphs for comparison/diagnostic purposes.
    plt.plot(time_sim, current, color='tab:blue', linestyle='-')

    # Labels and title
    plt.xlabel("Time (seconds)")
    plt.ylabel("Inductor Current (A)")
    plt.title("Inductor")

    plt.savefig('Indoctor_Current.png', format='png')

    plt.show()
