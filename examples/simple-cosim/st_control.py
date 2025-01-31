import requests
import json
import time
import helics as h
import logging
from switch_controller import destroy_federate, get_device_status, url_control, headers, hours


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


running = True

def print_status_every_second():
    while running:
        status = get_device_status()
        logger.info(f"Device status: {status}")
        time.sleep(1)  # Wait for 1 second before checking the status again

def send_command(command):
    payload = {
        "commands": [
            {
                "component": "main",
                "capability": "switch",
                "command": command
            }
        ]
    }
    response = requests.post(url_control, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        logger.info(f"Command '{command}' sent successfully.")
    else:
        logger.info(f"Failed to send command '{command}'. Status code: {response.status_code}, Response: {response.text}")

def check_and_update_status(time):
        status = get_device_status()
        if (status == "CLOSED") and (time % 600 == 1):
            logger.info(f"Switch is currently {status}. Will open after 5 minutes.")
            send_command("off")
        elif (time % 600 == 301):
            logger.info(f"Switch is currently {status}. Will close after 5 minutes.")
            send_command("on")
        #else :
            #logger.info(f"~{time}")


#################################


def destroy_federate(fed):
    grantedtime = h.helicsFederateRequestTime(fed, h.HELICS_TIME_MAXTIME)
    status = h.helicsFederateDisconnect(fed)
    h.helicsFederateDestroy(fed)
    logger.info("Federate finalized")


if __name__ == "__main__":

    total_inteval = int(60 * 60 * hours)
    grantedtime = -1
    update_interval = 30 #1 * 60 ## Adjust this to change EV update interval


    #################################  Registering  federate from json  ########################################
    subid = {}
    fed = h.helicsCreateValueFederateFromConfig(f"st_control.json")
    federate_name = h.helicsFederateGetName(fed)
    logger.info("HELICS Version: {}".format(h.helicsGetVersion()))
    logger.info("{}: Federate {} has been registered".format(federate_name, federate_name))
    subkeys_count = h.helicsFederateGetInputCount(fed)

    for i in range(0, subkeys_count):
        subid["m{}".format(i)] = h.helicsFederateGetInputByIndex(fed, i)
        h.helicsInputSetDefaultComplex(subid["m{}".format(i)], 0, 0)
        sub_key = h.helicsSubscriptionGetTarget(subid["m{}".format(i)])
        logger.info("{}: Registered Subscription ---> {}".format(federate_name, sub_key))

    ######################   Entering Execution Mode  ##########################################################
    h.helicsFederateEnterInitializingMode(fed)
    status = h.helicsFederateEnterExecutingMode(fed)


    for i in range(0, subkeys_count):
        sub = subid["m{}".format(i)]
        Gld_sw_status = h.helicsInputGetString(sub)
    logger.info("{}: Switch state in GLD => {} .".format(federate_name, Gld_sw_status))

    for t in range(0, total_inteval, update_interval):
        check_and_update_status(grantedtime)
        logger.info("{} - {}".format(grantedtime, t))
        while grantedtime < t:
            grantedtime = h.helicsFederateRequestTime(fed, t+1)  #offset included
    
    logger.info("{}: Federate Granted Time = {}".format(federate_name,grantedtime))        

    ##############################   Terminating Federate   ########################################################
    t = 60 * 60 * hours
    while grantedtime < t:
        grantedtime = h.helicsFederateRequestTime(fed, t+1)  #offset included
    logger.info("{}: Destroying federate".format(federate_name))
    running = False
    destroy_federate(fed)
    logger.info("{}: Done!".format(federate_name))


