# -*- coding: utf-8 -*-
"""
Created on 2/18/2025

This federate performs the power flow for the full test oneline network.

This model creates federate and registers it with the HELICS API.

@author: Ehab Shoubaki
eshoubak@uncc.edu
"""
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

def create_value_federate(fedinitstring,name,period):
    fedinfo = h.helicsCreateFederateInfo()
    h.helicsFederateInfoSetCoreTypeFromString(fedinfo, "zmq")
    h.helicsFederateInfoSetCoreInitString(fedinfo, fedinitstring)
    h.helicsFederateInfoSetIntegerProperty(fedinfo, h.helics_property_int_log_level, 1)
    h.helicsFederateInfoSetTimeProperty(fedinfo, h.helics_property_time_period, period)
    h.helicsFederateInfoSetFlagOption(fedinfo, h.helics_flag_uninterruptible, False)
    h.helicsFederateInfoSetFlagOption(fedinfo, h.HELICS_FLAG_TERMINATE_ON_ERROR, True)
    h.helicsFederateInfoSetFlagOption(fedinfo, h.helics_flag_wait_for_current_time_update, False)
    fed = h.helicsCreateValueFederate(name, fedinfo)
    return fed

if __name__ == "__main__":
    
    ##########  Registering  federate and configuring with API################
    fedinitstring = " --federates=1"
    name = "Full PowerFlow"
    period = 1.0
    fed = create_value_federate(fedinitstring,name,period)
    logger.info(f'Created federate {name}')
    print(f'Created federate {name}')

    Vc_mag_id = h.helicsFederateRegisterGlobalTypePublication(fed, 'Vc_mag_full', 'double', 'V')
    logger.debug(f'\tRegistered publication---> Vc_mag_full')

    Vc_ph_id = h.helicsFederateRegisterGlobalTypePublication(fed, 'Vc_ph_full', 'double', 'deg')
    logger.debug(f'\tRegistered publication---> Vc_ph_full')

    Pc_id = h.helicsFederateRegisterGlobalTypePublication(fed,'Pc_full', 'MW')
    logger.debug(f'\tRegistered subscription---> Pc_full')

    Qc_id = h.helicsFederateRegisterGlobalTypePublication(fed,'Qc_full', 'MVAR')
    logger.debug(f'\tRegistered subscription---> Qc_full')

    ##############  Entering Execution Mode  ##################################
    h.helicsFederateEnterExecutingMode(fed)
    logger.info('Entered HELICS execution mode')

    total_interval = 10.0
    update_interval = h.helicsFederateGetTimeProperty(
                                fed,
                                h.HELICS_PROPERTY_TIME_PERIOD)
    grantedtime = 0

    r = 0.2
    x = 0.8
    ratio = 0.3
    
    # As long as granted time is in the time range to be simulated...
    while grantedtime < total_interval:
        
        # Time request for the next physical interval to be simulated
        requested_time = (grantedtime+update_interval)
        logger.debug(f'Requesting time {requested_time}')

        grantedtime = h.helicsFederateRequestTime (fed, requested_time)
        logger.debug(f'Granted time {grantedtime}')

        # Calculate Full Power Flow
        [Vc_mag,Vc_ph,Pc,Qc]=pf.full_powerflow(r,x,ratio)

        # Publish Power Flow results for center bus
        h.helicsPublicationPublishDouble(Vc_mag_id, Vc_mag)
        logger.debug(f'\tPublished Vc_mag_full with value {Vc_mag}')
        
        h.helicsPublicationPublishDouble(Vc_ph_id,Vc_ph)
        logger.debug(f'\tPublished V_ph_full with value {Vc_ph}')
        
        h.helicsPublicationPublishDouble(Pc_id, Pc)
        logger.debug(f'\tPublished Pc_full with value {Pc}')

        h.helicsPublicationPublishDouble(Qc_id, Qc)
        logger.debug(f'\tPublished Qc_full  with value {Qc}')

    # Cleaning up HELICS stuff once we've finished the co-simulation.
    destroy_federate(fed)
