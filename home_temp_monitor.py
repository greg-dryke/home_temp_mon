# Read Imports
import os
import os.path
import glob
import time
import sys
import traceback

#Adafruit Write Imports
#import time
import datetime
from Adafruit_IO import Client

from pyutils.Log import Log

# Fix gateway imports
from subprocess import call

log_file_path = '/var/log/temp_monitor.log'
log = Log(log_file_path)
#log_file = open(log_file_path, 'a')
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
reset_gateway_cmd = 'sudo ip route add default via 192.168.2.1'.split()
adaKeyPath = './adakey.secret'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c


def ResetGateway():
    call(reset_gateway_cmd)

def GetKey():
    if os.path.isfile(adaKeyPath):
        try:
            f = open(adaKeyPath , 'r')
            lines = f.readlines()
            f.close()
            return str(lines[0]).strip()
        except Exception as e:
            log.LogError("Exception on start, could not read ADA IO key. Path: " + adaKeyPath)
            log.LogError("No data will be published to adafruit IO")
            LogToAda("Exception on start, could not read ADA IO key. Path: " + adaKeyPath)
            LogToAda("No data will be published to adafruit IO")
            return None
    else:
        log.LogWarning("No key file found for adafruit IO. Path: " + adaKeyPath)
        log.LogWarning("No data will be published to adafruit IO")
        return None

def LogToAda(msg):
    if aio is not None:
        try:
            aio.send('errors', msg)
        except:
            print e
            pass

aio = None

aioKey = GetKey()
if aioKey is not None:
    aio = Client(aioKey)

try:
    log.LogInfo("Monitoring started.")
    while True:
        log.LogInfo("Reading temperature...")
        try:
            temp = read_temp()
        except Exception as e:
            exceptStr = ""
            try:
                exceptStr = str(e)
            except Exception as f:
                log.LogError("Exception when converting exception to string from reading")
                LogToAda("Exception when converting exception to string from reading")
            log.LogError("Error Reading Temp. Error: "+exceptStr)
            LogToAda("Error Reading Temp. Error: "+exceptStr)
            sleep(10)
            continue

        log.LogInfo('Current Temp: '+str(temp))

        try:
            if aio is not None:
                aio.send('home-temp', temp)
        except Exception as e:
            exceptStr = ""
            try:
                exceptStr = str(e)
            except Exception as f:
                log.LogError("Exception when converting exception to string from sending")
                LogToAda("Exception when converting exception to stringfrom sending")
            log.LogError("Error Sending Data to Aadafruit IO. Error: " + exceptStr)
            LogToAda("Error Sending Data to Aadafruit IO. Error: " + exceptStr)
            if '403 Forbidden' in exceptStr:
                log.LogError('403 error. Exiting')
                sys.exit()
            log.LogInfo("Attempting to reset gateway and restore connectivity...")
            ResetGateway()
            time.sleep(10)
            continue

        log.FlushLog()
        time.sleep(120)
except Exception as e:
    log.LogError(str(e))
    LogToAda(str(e))
    _, _, trace = sys.exc_info()
    log.LogTraceback(e, trace)
finally:
    log.FlushLog()
