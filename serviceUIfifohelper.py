# Create a Fifo
# write to a fifo - no wait
# write to a fifo - wait for a listener
# write to a fifo - wait for response
# write async to a fifo
# try to read a fifo
# read a fifo NOW
# read a fifo async

from mbewareCommonTools import  ExitCode, ExitCodeDesc
from serviceUIglobals import logger
import os
from select import select
import asyncio



def createFifoPath(path):
    if not os.path.exists(path):
        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)
        os.mkfifo(path)
    
def openFifo(path,mode="r"):
    createFifoPath(path)
    return open(path, mode) 


def writeFifo(path,data):
    with openFifo(path,"a") as fifo_file:
        fifo_file.write(data)

def readData(fifo_file)->str:
    data = fifo_file.read()
    logger.debug(f'readData: received data :{data if not None else "None"}')
    if data is None: 
        data = ""
    return data

def readFifo(path,timeout:int=0)->tuple[str,int]:
    if timeout > 0:
        logger.debug(f'readFifo: {timeout=}, calling timeout version')
        return asyncio.run(readFifoWithTimeout(path,timeout))        
       
    else:
        logger.debug(f'readFifo: reading {path}')
        with  openFifo(path,"r") as fifo_file:
            data =  readData(fifo_file)
            return data,ExitCode.Success

async def async_readFifo(future_data,path,timeout):
    logger.debug(f'async_readFifo: {path}')
    data=""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(fd, 'r') as fifo_file:
            ready, _, _ = select([fifo_file], [], [], timeout)
            if not ready:
                logger.debug(f'async_readFifo: timeout ({timeout})s on {path}')
                future_data.set_result("")
                
            else: 
                logger.debug(f'async_readFifo: reading {path}')
                data = readData(fifo_file)
                future_data.set_result( data)
    except Exception as e:
        logger.error(f"async_readFifo: unknown error {e}, {data=} {path=} {timeout=}")
        future_data.set_result(( f'Exception : {e=}',ExitCode.General_error))
    finally:
        logger.debug(f"{data=},{ready=}")

async def readFifoWithTimeout(path,timeout):
        data = ""
        createFifoPath(path)
        loop = asyncio.get_running_loop()
        future_data = loop.create_future()
        loop.create_task(async_readFifo(future_data,path,timeout))
        logger.debug(f'readFifoWithTimeout: waiting for {path}')
        a= await future_data
        return a,0            


def sendDataAndWaitForResponse(sendpath,receivepath,data,timeout:int=0):
    errorcode=ExitCode.Success 
    logger.debug(f"sendDataAndWaitForResponse: sending {data} to {sendpath}")
    writeFifo(sendpath,data)
    logger.debug(f"sendDataAndWaitForResponse: waiting for response on {receivepath} for {timeout}s")
    response,errorcode = readFifo(receivepath,timeout)
    if errorcode != ExitCode.Success and errorcode != ExitCode.Timeout:
        logger.error(f"sendDataAndWaitForResponse: {errorcode} : {ExitCodeDesc[errorcode]} on fifo at {receivepath} : {response}")
    elif errorcode == ExitCode.Timeout:
        logger.debug(f"sendDataAndWaitForResponse: timeout on fifo at {receivepath} returning None")
        return None
    else:
        logger.debug(f"sendDataAndWaitForResponse: received response on fifo at {receivepath} : {response}")
    return response



        
            

