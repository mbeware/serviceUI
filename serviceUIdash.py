# my stuff
import copy
from typing import Any
from mbewareCommonTools import  ExitCode, load_config, DEBUG
from serviceUIglobals import logger , service_list, config
from serviceUIprotocols import valid_register_request, Service

import serviceUIglobals # import what ever wasn't

from serviceUIfifohelper import readFifo, sendDataAndWaitForResponse

#
import threading


from time import sleep
# CAREFULL : FLASK HAS A QUIRK THAT IT RESTART ITSELF IN DEBUG-MODE
# Loop 2 (flask):   Wait for webUI trigger or refresh data timeout
#                   send message to service
#                   wait for response (with timeout)
#                   display new form/info (or timeout error)




# region: Registering Services ###########################################################################################

def startRegisteringLoop():
    thread = threading.Thread(target=registeringLoop)
    thread.start()


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
            register_request = valid_register_request(json_message,logger)
            if register_request: 
                newService = Service(name=register_request.service_name,
                                     fifo_path=register_request.service_fifo,
                                     main_formid=register_request.main_formid)
                service_list[register_request.service_name] = newService
                logger.debug(f"registeringLoop: {register_request.service_name} has been registered")
                logger.info("Service list : ")
                for service in service_list.keys():
                    logger.info(f"   {service} : {service_list[service].fifo_path} -{service_list[service].main_formid }")
# endregion   

# region: flask App ######################################################################################################
from serviceUIweb import *
from flask import Flask, render_template,render_template_string, request, redirect

def actOnResponse(json_response):
    pass

app = myFlask(__name__)        
@app.route("/")
def index():
    form : dict[str,Any] = {}
    if (app.currentFormid==config["WEBUIFORMID"]) or (not app.selectedService):
        widgetService = service_list
        form = app.selectServiceForm(widgetService["choices"])
    
    else : 
        form = copy.deepcopy(app.currentForm)
        navmenu = app.navMenuToSelectService()
        form["widgets"].extend(navmenu)
    app.printform(form)
    return render_template_string(app.dynhtml, **form)


# ----- MENU ACTION ---------------------------------------------------------
@app.route("/menu_action", methods=["POST"])
def menu_action():
    global selected_service
    route:str = "/"
    choice = request.form.get("choice")
    service = request.form.get("service")
    formid = request.form.get("formid")
    widgetname = request.form.get("widget_name")
    if widgetname == config["WEBUIBACKTOSELECT"] and choice == config["WEBUIFORMID"] : 
        selected_service = None
        app.currentFormid=choice
        route = "/"
    else:
        if app.currentFormid == config["WEBUIFORMID"]:
            service = choice
            selected_service = service
            app.selectedService=service

        message={"service":service,"formid":formid,"widget_type":"menu","widget_name":widgetname,"choice":choice}   
        if selected_service:
            response = sendDataAndWaitForResponse(sendpath=service_list[selected_service].fifo_path,
                                    receivepath=config["response_fifo_path"],
                                    data=message,
                                    timeout=config["response_fifo_timeout"])     
            if response:
                toto = actOnResponse(response)
            else:
                route = "/timeout"
        else: 
            route = "/"
    return redirect(route)


# ----- TEXT INPUT ACTION ---------------------------------------------------
@app.route("/text_input_action", methods=["POST"])
def text_input_action():
    value = request.form.get("value")
    logger.debug(f"[FR] Texte reçu: {value}")
    # TODO: send to pipe
    return ""   # redirect("/")


# ----- TEXT BLOCK AUTO REFRESH ---------------------------------------------
LIVE_LOGS=["a","b","c"]

@app.route("/refresh_block")
def refresh_block():
    idx = int(request.args.get("index", 1))  # noqa: F841
    # TODO: read actual logs from service FIFO
    return "\n".join(LIVE_LOGS)

@app.route("/timeout")
def timeout():
    selected_service=None
    return render_template("timeout.html")    

# endregion

def main():
    global config
    global service_list
    global selected_service
    selected_service = None
    config = load_config("serviceUI.toml")
    # start listening to the Fifo for services to register
    logger.debug("Starting the registereing loop") 
    startRegisteringLoop()
    # start the webserver to display the UI
    #serviceUIweb.run(debug=False, port=5000) 
    # everything is done. We wait forever. (Not needen if Flask, but do not forget to kill loop in flask.exit)
    while True:
        sleep(22)
        

        logger.debug("main(): new loop....")    
if __name__ == "__main__":
    serviceUIglobals.init(loggerlevel=DEBUG) # create the logger, and change the level to debug. 
    main()

    