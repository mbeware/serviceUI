# serviceUI
An easy way to add knobs and sliders to your running services.

## How it works

There is a "mini" webserver that allow all of your services to offer their own UI. This server can be accessed by any browser, but only the services that are registered will show up in the UI. In each services, you just need to add the connector module and define the navigation and the configuration/information screens. The communication between the service and the UI is done thru a OS fifo with some security, for this version. In version 2.0 we are going to add the option to use DBUS. 


