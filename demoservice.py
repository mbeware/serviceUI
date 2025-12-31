import random
from time import sleep
import json
from serviceUIprotocols import Message_register,  Message_register_actions as MRA




def register_service(service_name:str):

    register_fifo_path = "/tmp/serviceUI/register_service.fifo"
    serviceUIconnector_fifo_basepath = "/tmp/serviceUI/"

    service_fifo_path = f"{serviceUIconnector_fifo_basepath}/{service_name}" 
    webServerFifoPath = register_fifo_path

    registerMessage=Message_register(service_name,MRA.Register,service_fifo_path)
    jmes=registerMessage.to_json() # type: ignore
    with open(webServerFifoPath, "w") as f:
        print(f"{jmes}")
        f.write(jmes)
 
def main():
    quit=False
    i=0
    while not quit :
        mainloop = random.randint(10,30)
        registeri = random.randint(i+5,i+15)
        x=3 * mainloop
        print("main loop :",end="",flush=True)
        for _ in range(mainloop):
            sleep(1)
            i+=1
            print(".", end="", flush=True)
            if i == registeri:
                register_service(f"service{registeri}")
        print("")
        print(f"Looped {mainloop} times. Since demo started, looped for{i} times. Now waiting for {x} seconds")
        sleep(x)
        print("Back to ", end="")


if __name__ == "__main__":
    main()
