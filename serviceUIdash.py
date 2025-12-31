from mbewareCommonTools import createlogger, ExitCode, load_config
import serviceUIglobals
from serviceUIglobals import logger
from time import sleep
# CAREFULL : FLASK HAS A QUIRK THAT IT RESTART ITSELF IN DEBUG-MODE
# serviceUI has 2 "main" loops and we might add a "management" loop

# Loop 1 (asyncio): 
#                   task1 : listen to services register/unregister requests
#                           add/remove the service from the list
#                   task2 : check queue for message from flask and process them

# Loop 2 (flask):   Wait for webUI trigger or refresh data timeout
#                   send message to service
#                   wait for response (with timeout)
#                   display new form/info (or timeout error)
from serviceUIfifohelper import readFifo
from serviceUIprotocols import *
import pathlib
from typing import Any


###import asyncio
###from asyncio import sleep
###all_tasks:dict[str,asyncio.Task]={}
###all_loops:dict[str,asyncio.EventLoop]={}
import threading
import json

# def createLoop():
#     global all_tasks    
#     loop = asyncio.new_event_loop()
#     logger.debug(f"{loop=}")
#     asyncio.set_event_loop(loop)
#     all_tasks["registeringLoop"]=loop.create_task(mainloop())
#     loop.run_forever()



# async def mainloop():
#     i=0
#     loop=asyncio.get_running_loop()
#     all_tasks["mainLoop"]=loop.create_task(registeringLoop())

#     while True:
#         i+=1
#         logger.debug(f"mainloop: {i=}")
#         await sleep(10)

def startRegisteringLoop():
    thread = threading.Thread(target=registeringLoop)
    thread.start()

def valid_register_request(request:str):
    logger.debug(f"valid_register_request : Validating received message")
    try: 
        message_dict = json.loads(request)
    except: 
        logger.error(f"valid_register_request: Invalid message structure or invalid json {request}")
        return None
    
    if message_dict.get("messageformat") != Message_register.messageformat:
        logger.error(f"valid_register_request: Invalid message format from  {config['register_fifo_path']} - {message_dict}")
        return None
    logger.debug(f"valid_register_request: Message format is valid. Validating action")
    register_request=Message_register(**message_dict)
    if register_request.action not in ( Message_register_actions.Register, Message_register_actions.Unregister):
        logger.error(f"valid_register_request: Invalid actions {register_request.action}")
        return None
    logger.debug(f"valid_register_request: Action is valid. Validating fifo")
    if register_request.service_fifo is None or register_request.service_fifo =="": 
        logger.error(f"valid_register_request: Fifo file is requiered {register_request.service_fifo}")
        return None
    if register_request.service_name is None or register_request.service_name =="":
        logger.error(f"valid_register_request: Service name is requiered {register_request.service_fifo}")
        return None

    return register_request     

service_list:dict[str,Message_register] = {}

def registeringLoop(): #register loop
    logger.debug(f"registeringLoop:start")
    
    global config
    global service_list
    newdata=True
    while True:

        # we have to loop, because registering fifo closes when reading the last entry. 
        json_message, returncode = readFifo(config['register_fifo_path'],config['register_fifo_timeout']) 
        if json_message == "" and newdata:
            logger.debug(f"registeringLoop:fifo at {config['register_fifo_path']} was empty")
            newdata=False
        elif json_message is None and newdata:
            logger.debug(f"registeringLoop:fifo at {config['register_fifo_path']} timedout")
            newdata=False
        elif returncode != ExitCode.Success:
            logger.debug(f"registeringLoop:fifo at {config['register_fifo_path']} returned with {returncode} {json_message=}")
            newdata=True
        else:
            newdata=True
            register_request = valid_register_request(json_message)
            if register_request: 
                thisrequest = register_request
                service_list[register_request.service_name] = thisrequest
                logger.debug(f"registeringLoop: {register_request.service_name} has been registered")
   
def main():
    global config
    global service_list
    config = load_config("serviceUI.toml")
    # start listening to the Fifo for services to register
    logger.debug("Starting the registereing loop") 
    startRegisteringLoop()
    # start the webserver to display the UI
    #####

    # everything is done. We wait forever. (Not needen if Flask, but do not forget to kill loop in flask.exit)
    while True:
        sleep(22)
        
        logger.debug("Service list : ")
        for service in service_list.keys():
            logger.debug(f"   {service} : {service_list[service].service_fifo} -{service_list[service].main_formid }")
        logger.debug("main(): new loop....")    
if __name__ == "__main__":
    main()

    