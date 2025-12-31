from mbewareCommonTools import createlogger, change_loglevel
import logging

loggername = "serviceUIdash.log"
logger = createlogger(loggername)
change_loglevel(loggername,logging.DEBUG)
