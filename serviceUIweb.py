from typing import Any
from flask import Flask, render_template,render_template_string, request, redirect
from serviceUIglobals import logger , service_list, config


class myFlask(Flask):
    def __init__(self,name:str):
        global config
        Flask.__init__(self,name)
        
        self.selectedService:str|None=None
        self.currentFormid=config["WEBUIFORMID"]
        self.currentForm=self.selectServiceForm(service_list)
        self.received_route="/"
        with open ("./templates/dynaform.html","r") as f:
            self.dynhtml = f.read()
    
    def printform(self,form:dict[str,Any]):
        logger.debug(form)
        logger.debug("***************")
        for formattr in form.keys():
            if formattr == "widgets":
                widgets = form[formattr] # list
                for widget in widgets:
                    wname = widget["name"]
                    for wattr in widget.keys():
                        if wattr == "choices":
                            for choice in widget[wattr]:
                                logger.debug(f"...{wname}...{wattr}...{choice}")
                        else:    
                            logger.debug(f"...{wname}...{wattr}={widget[wattr]}")

            else:
                logger.debug(f"{formattr}={form[formattr]}")

    def selectServiceForm(self,param_service_list=None)-> dict[str,Any]:
        global service_list
        global config
        if not param_service_list:
            widgetService = service_list
            param_service_list=widgetService["choices"]
        form:dict[str,Any]={}
        form["service"]=config["WEBUISERVICE"]
        form["type"] = "Form"
        form["formid"] = config["WEBUIFORMID"]
        form["callback"] = "serviceSelected"
        form["title"] = "List of registered services"
        form["subtitle"] = "select a service"    
        form["widgets"]=[{"type":"Menu","name":"service_select","title":"Select a service","choices":param_service_list}]
        return form

    def navMenuToSelectService(self)-> list[dict[str,Any]]:
        global config
        toolbar = []
        navWidget:dict[str,Any]={}
        
        navWidget["type"] = "Menu"
        navWidget["name"] = config["WEBUIBACKTOSELECT"]
        navWidget["title"] =""
        navWidget["choices"]=[{"label" : config["WEBUIFORMID"], 
                                "description" : "Go to List of registered services" }
                                ]
        toolbar.append(navWidget)          
        return toolbar
