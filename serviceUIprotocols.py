from dataclasses import dataclass
import json
from dataclasses_json import dataclass_json

#####################
# Messages
#--------------------
# announce from service to UI
# Register/unregister
@dataclass
@dataclass_json
class message_announce():
    service_name: str
    action : str # register or unregister
    service_fifo : str|None
    main_formid : str = "main"

#------------------------------------------------------------
# from UI to service : return from widget interaction
# 

@dataclass
@dataclass_json
class message_widgetReturn():
    service_name: str
    formid: str
    widget_id : str
    widget_type : str
    widget_data : dict

#------------------------------------------------------------
# From service to UI - new form/data to display
# 

@dataclass
@dataclass_json
class widgetDef():
    type:str
    name:str
    title:str

@dataclass_json
@dataclass
class menuChoice():
    code:str
    label:str
    data : str


@dataclass_json
@dataclass
class widgetMenu():
    name:str
    title:str=""
    choices: list[menuChoice]|None=None
    type:str="menu"

@dataclass_json
@dataclass
class widgetEdit():
    name:str
    title:str=""
    label:str=""
    data:str=""
    password:str="False"
    visible:str="True"
    type:str="edit"

@dataclass_json
@dataclass
class widgetText():
    name:str
    title:str=""
    label:str=""
    visible:str="True"
    getmoreinterval:int=0 # in seconds
    type:str="text"


@dataclass_json
@dataclass
class message_formDisplay():
    service_name: str
    formid: str
    form_title: str
    form_subtitle:str=""
    widgets: list[widgetMenu|widgetEdit|widgetText]|None=None

if __name__ == "__main__":
    ch1 = menuChoice(code="a",label="A",data="data")
    ch2 = menuChoice(code="b",label="B",data="data")
    testchoices = [ch1,ch2]
    widget1 = widgetMenu(name="test", title="Test menu",choices=testchoices)
    widget2 = widgetMenu(name="test2", title="Test menu 2")
    widgets_list: list[widgetMenu|widgetEdit|widgetText]|None=[widget1,widget2]
    test_message_formDisplay:message_formDisplay = message_formDisplay(
        service_name="test",
        formid="form1",
        form_title="Form 1",
        widgets=widgets_list)
    
    message_formDisplay_json = test_message_formDisplay.to_json()
    print(message_formDisplay_json)

