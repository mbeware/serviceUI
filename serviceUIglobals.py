from mbewareCommonTools import createlogger, change_loglevel
from serviceUIprotocols import Service

logger = None                          # global logger ####################################    
service_list:dict[str,Service] = {}    # global service_list ##############################

config = {}

def init(loggername = "serviceUIdash.log",loggerlevel=None):
    global logger
    logger = createlogger(loggername)
    if loggerlevel: 
        change_loglevel(loggername,loggerlevel)

