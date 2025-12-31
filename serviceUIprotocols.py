from dataclasses import dataclass
import json
from dataclasses_json import dataclass_json
from enum import Enum
# Note : 
# @dataclass_json
# @dataclass
# class myjsonclass():


#################
# Service
@dataclass 
class Service():
    name:str
    fifo_path:str
    main_formid:str




#####################
# Messages
#--------------------
# register_request from service to UI
# Register/unregister

class Message_register_actions():
    Register="Register"
    Unregister="Unregister"

@dataclass_json
@dataclass
class Message_register():    
    service_name: str
    action : str # register or unregister
    service_fifo : str
    main_formid : str = "main"
    messageformat:str="message_register"
    
def valid_register_request(request:str,logger=None):
    def display_warning(message:str,logger=None):
        if logger:  logger.warn(message)
        else:       print(f"Warning:{message}")
                    
    if logger: logger.debug(f"valid_register_request : Validating received message")
    try: 
        message_dict = json.loads(request)
    except: 
        display_warning(f"valid_register_request: Invalid message structure or invalid json {request}",logger)
        return None
    
    if message_dict.get("messageformat") != Message_register.messageformat:
        display_warning(f"valid_register_request: Invalid message format for register_request - {message_dict}",logger)
        return None
    if logger: logger.debug(f"valid_register_request: Message format is valid. Validating action")
    register_request=Message_register(**message_dict)
    if register_request.action not in ( Message_register_actions.Register, Message_register_actions.Unregister):
        display_warning(f"valid_register_request: Invalid actions {register_request.action}",logger)
        return None
    if logger: logger.debug(f"valid_register_request: Action is valid. Validating fifo")
    if register_request.service_fifo is None or register_request.service_fifo =="": 
        display_warning(f"valid_register_request: Fifo file is requiered {register_request.service_fifo}",logger)
        return None
    if register_request.service_name is None or register_request.service_name =="":
        display_warning(f"valid_register_request: Service name is requiered {register_request.service_fifo}",logger)
        return None

    return register_request     




#------------------------------------------------------------
# from UI to service : return from widget interaction
# 
@dataclass_json
@dataclass
class Message_widgetReturn():
    service_name: str
    formid: str
    widget_id : str
    widget_type : str
    widget_data : dict

#------------------------------------------------------------
# From service to UI - new form/data to display
# 

@dataclass_json
@dataclass
class WidgetDef():
    type:str
    name:str
    title:str

@dataclass_json
@dataclass
class MenuChoice():
    code:str
    label:str
    data : str


@dataclass_json
@dataclass
class WidgetMenu():
    name:str
    title:str=""
    choices: list[MenuChoice]|None=None
    type:str="menu"

@dataclass_json
@dataclass
class WidgetEdit():
    name:str
    title:str=""
    label:str=""
    data:str=""
    password:str="False"
    visible:str="True"
    type:str="edit"

@dataclass_json
@dataclass
class WidgetText():
    name:str
    title:str=""
    label:str=""
    visible:str="True"
    getmoreinterval:int=0 # in seconds
    type:str="text"


@dataclass_json
@dataclass
class Message_formDisplay():
    service_name: str
    formid: str
    form_title: str
    form_subtitle:str=""
    widgets: list[WidgetMenu|WidgetEdit|WidgetText]|None=None

if __name__ == "__main__":
    ch1 = MenuChoice(code="a",label="A",data="data")
    ch2 = MenuChoice(code="b",label="B",data="data")
    testchoices = [ch1,ch2]
    widget1 = WidgetMenu(name="test", title="Test menu",choices=testchoices)
    widget2 = WidgetMenu(name="test2", title="Test menu 2")
    widgets_list: list[WidgetMenu|WidgetEdit|WidgetText]|None=[widget1,widget2]
    test_message_formDisplay:Message_formDisplay = Message_formDisplay(
        service_name="test",
        formid="form1",
        form_title="Form 1",
        widgets=widgets_list)
    print(f"dataclass : {test_message_formDisplay}")
    message_formDisplay_json = test_message_formDisplay.to_json() # type: ignore
    print(f"json : {message_formDisplay_json}")

