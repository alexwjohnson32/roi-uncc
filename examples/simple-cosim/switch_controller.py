# -*- coding: utf-8 -*-
"""
Updated switch_controller.py for integration with GridPACK federate
"""
import requests
import json
import time
import helics as h
import logging
import argparse

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# URLs for getting device status and controlling the device
url_status = "https://api.smartthings.com/v1/devices/a1a25a20-24a2-41a6-abe5-c7200337552b/status"
url_control = "https://api.smartthings.com/v1/devices/a1a25a20-24a2-41a6-abe5-c7200337552b/commands"

headers = {
    'Authorization': 'Bearer 0dc70a10-bda8-4d39-a1ee-67dc45e91595',
    'Content-Type': 'application/json'
}

def get_device_status():
    try:
        response = requests.get(url_status, headers=headers)
        logger.info(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                status = data['components']['main']['switch']['switch']['value']

                if status == "on":
                    switch_status = "CLOSED"
                elif status == "off":
                    switch_status = "OPEN"
                else:
                    switch_status = "UNKNOWN"

                return switch_status

            except json.JSONDecodeError as e:
                logger.error("Error decoding JSON response: {}".format(str(e)))
                return None
        else:
            logger.error("Failed to get a valid response from the server. Status Code: {}".format(response.status_code))
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching device status: {str(e)}")
        return None

def destroy_federate(fed):
    grantedtime = h.helicsFederateRequestTime(fed, h.HELICS_TIME_MAXTIME)
    h.helicsFederateDisconnect(fed)
    h.helicsFederateDestroy(fed)
    logger.info("Federate finalized")

# Define the default hours value outside the main block to make it accessible for import
hours = 1  # Default value if not provided

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--case_num', help='Case number, must be either "1b" or "1c"', nargs=1)
    args = parser.parse_args()
    
    # Set the hours value based on the input argument
    if args.case_num and args.case_num[0] == "1b":
        hours = 1
    elif args.case_num and args.case_num[0] == "1c":
        hours = 2

    # Registering federate from json
    fed = h.helicsCreateValueFederateFromConfig("switch_controller.json")
    federate_name = h.helicsFederateGetName(fed)
    logger.info("HELICS Version: {}".format(h.helicsGetVersion()))
    logger.info("{}: Federate {} has been registered".format(federate_name, federate_name))

    pubkeys_count = h.helicsFederateGetPublicationCount(fed)
    subkeys_count = h.helicsFederateGetInputCount(fed)

    # Reference to Publications and Subscription form index
    pubid = {}
    subid = {}
    for i in range(pubkeys_count):
        pubid["m{}".format(i)] = h.helicsFederateGetPublicationByIndex(fed, i)
        pubname = h.helicsPublicationGetName(pubid["m{}".format(i)])
        logger.info("{}: Registered Publication ---> {}".format(federate_name, pubname))

    for i in range(subkeys_count):
        subid["m{}".format(i)] = h.helicsFederateGetInputByIndex(fed, i)
        h.helicsInputSetDefaultComplex(subid["m{}".format(i)], 0, 0)
        sub_key = h.helicsSubscriptionGetTarget(subid["m{}".format(i)])
        logger.info("{}: Registered Subscription ---> {}".format(federate_name, sub_key))

    # Entering Execution Mode
    h.helicsFederateEnterInitializingMode(fed)
    status = h.helicsFederateEnterExecutingMode(fed)

    total_interval = int(60 * 60 * hours)
    grantedtime = -1
    update_interval = 30
    switch_state = "CLOSED"

    # Starting Co-simulation
    for t in range(0, total_interval, update_interval):
        if (grantedtime % 30 == 2):
            switch_state = get_device_status()
            if switch_state:
                logger.info("{}: Switch state value = {} ".format(federate_name, switch_state))
                for i in range(pubkeys_count):
                    pub = pubid["m{}".format(i)]
                    if i == 0:
                        h.helicsPublicationPublishString(pub, switch_state)
                    else:
                        test_val = 0.0  # Placeholder test value
                        h.helicsPublicationPublishString(pub, str(test_val))
                        logger.info("Published test value: {}".format(test_val))
                        test_val += 2.505

                logger.info("Switch state => {}".format(switch_state))

        logger.info("{} - {}".format(grantedtime, t))
        while grantedtime < t:
            grantedtime = h.helicsFederateRequestTime(fed, t + 2)

        # Subscribing to Load current from GridLAB-D
        for i in range(subkeys_count):
            sub = subid["m{}".format(i)]
            if h.helicsSubscriptionGetTarget(sub) == "transmission_voltage":  # Assuming new subscription from GridPACK
                transmission_voltage = h.helicsInputGetComplex(sub).real
                logger.info(f"Received transmission voltage: {transmission_voltage}")

            demand = h.helicsInputGetComplex(sub)
            rload = demand.real * 1000
            iload = demand.imag * 1000
            logger.info("{}: Federate Granted Time = {}".format(federate_name, grantedtime))
            logger.info("{}: Load current consumption = {} Amps".format(federate_name, complex(round(rload, 2), round(iload, 2)) / 1000))

    # Terminating Federate
    t = 60 * 60 * hours
    while grantedtime < t:
        grantedtime = h.helicsFederateRequestTime(fed, t + 2)
    logger.info("{}: Destroying federate".format(federate_name))
    destroy_federate(fed)
    logger.info("{}: Done!".format(federate_name))
