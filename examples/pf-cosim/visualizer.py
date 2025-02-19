# -*- coding: utf-8 -*-
"""
Created on 2/18/2025

Visualization Federate for the Power Flow example federation.

This model creates federate and registers it with the HELICS API.

@author: Ehab Shoubaki
eshoubak@uncc.edu
"""

import matplotlib.pyplot as plt
import helics as h
import pf
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

def create_value_federate(fedinitstring,name,period,offset):
    fedinfo = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
    h.helicsFederateInfoSetCoreInitString(fedinfo, fedinitstring)
    h.helicsFederateInfoSetIntegerProperty(fedinfo, h.helics_property_int_log_level, 1)
    h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_period, period)
    h.helicsFederateInfoSetTimeProperty(fedinfo,  h.helics_property_time_offset, offset)
    h.helicsFederateInfoSetFlagOption(fedinfo, h.helics_flag_uninterruptible, True)
    h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_TERMINATE_ON_ERROR, True)
    h.helicsFederateInfoSetFlagOption(fedinfo, h.helics_flag_wait_for_current_time_update, False)
    fed = h.helicsCreateValueFederate(name, fedinfo)
    return fed

if __name__ == "__main__":
    
    ##########  Registering  federate and configuring with API################
    fedinitstring = " --federates=1"
    name = "Visualizer"
    period = 1.0
    offset = 0.1
    fed = create_value_federate(fedinitstring,name,period,offset)
    logger.info(f'Created federate {name}')
    print(f'Created federate {name}')

    # Subscriptions
    Vc_mag_full_id = h.helicsFederateRegisterSubscription(fed,'Vc_mag_full', 'V')
    logger.debug(f'\tRegistered subscription---> Vc_mag_full')

    Vc_mag_id = h.helicsFederateRegisterSubscription(fed,'Vc_mag', 'V')
    logger.debug(f'\tRegistered subscription---> Vc_mag')
    

    ##############  Entering Execution Mode  ##################################
    h.helicsFederateEnterExecutingMode(fed)
    logger.info('Entered HELICS execution mode')

    total_interval = 10.0
    update_interval = h.helicsFederateGetTimeProperty(
                                fed,
                                h.HELICS_PROPERTY_TIME_PERIOD)
    grantedtime = 0

    # Data collection lists
    time_sim = []
    Vc_mag_full = []
    Vc_mag= []

    # Prepare Plot
    plt.ion()
    fig, ax = plt.subplots()
    line1, = ax.plot([], [], 'bo-', label="Vc_mag_Full")   
    line2, = ax.plot([], [], 'ro-', label="Vc_mag_PYPY") 

    ax.relim()  # Recalculate limits based on new data
    ax.autoscale_view()  # Autoscale axes

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Voltage Magnitude (pu)")
    ax.legend()
    
    # As long as granted time is in the time range to be simulated...
    while grantedtime < total_interval:
        
        # Time request for the next physical interval to be simulated
        requested_time = (grantedtime+update_interval)
        logger.debug(f'Requesting time {requested_time}')

        grantedtime = h.helicsFederateRequestTime (fed, requested_time)
        logger.debug(f'Granted time {grantedtime}')

        # Get signals to plot
        time_sim.append(grantedtime)
        Vc_mag_full.append(h.helicsInputGetDouble(Vc_mag_full_id))
        Vc_mag.append(h.helicsInputGetDouble(Vc_mag_id))

        # Plot Signals
        line1.set_xdata(time_sim)
        line1.set_ydata(Vc_mag_full)
        line2.set_xdata(time_sim)
        line2.set_ydata(Vc_mag)

        ax.relim()  # Recalculate limits based on new data
        ax.autoscale_view()  # Autoscale axes

        plt.draw()  # Update the plot


    # Cleaning up HELICS stuff once we've finished the co-simulation.
    plt.ioff()
    plt.show()
    destroy_federate(fed)
