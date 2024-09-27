# IoT

## Pre-requisites

Install Azure CLI and asign in

```bash
az login
```

Set the right subscription if neccessary
```bash
az account set -s "AzureforAfrica Training"
```

## Set up Azure IoT Hub w/ Python SDK (pip3 install azure-iot-device)

Set up Variables
```bash
RESOURCE_GROUP=<your resource group>
IOT_HUB_NAME=<your IoT Hub name>
DEVICE_ID=<your device id>
```



**Create Azure IoT hub**

```bash
az iot hub create --resource-group $RESOURCE_GROUP --name $IOT_HUB_NAME
```

**Add required extention to az cli**
```bash
az extension add --name azure-iot
```

**Create Device**
```bash
az iot hub device-identity create --hub-name $IOT_HUB_NAME --device-id $DEVICE_ID
```

**Get Connection String and add to variable**
```bash
export IOTHUB_DEVICE_CONNECTION_STRING=$(az iot hub device-identity connection-string show --device-id $DEVICE_ID --hub-name $IOT_HUB_NAME)
```

**_(Optional) View the Connection String_**
```bash
echo $IOTHUB_DEVICE_CONNECTION_STRING


#output:

HostName=$IOT_HUB_NAME.azure-devices.net;DeviceId=$DEVICE_ID;SharedAccessKey=<some value>
```

## Monitor the output
Now, we can run the command below to monitor the output:

```bash
az iot hub monitor-events --hub-name $IOT_HUB_NAME --output json
```
Notice we have not specified any resource group or subscription, the azure IoT hub is unique within a subscription.


## (Remove) Set up Connection String in Env

Set Env variable (bash)
```bash
export IOTHUB_DEVICE_CONNECTION_STRING="HostName=<iot-hub-name>.azure-devices.net;DeviceId=DNT22-TempAndHumiditySensor;SharedAccessKey=xxxxxx=" #Bash
```

or
Set Env variable (cmd/pwsh)
```cmd
set IOTHUB_DEVICE_CONNECTION_STRING=<your connection string here> 
```


## Setup Python

Run in virtual environment:

```bash
python3 -m venv env
source env/bin/activate
```
Create Requirements 
`requirements.txt`
```txt
adafruit-circuitpython-dht
adafruit-blinka
paho-mqtt
azure-iot-device
```
Install the requirement.txt
```bash
pip3 install -r requirements.txt
```

## Testing the Process
Create a file called 
`test.py`
```py
import os
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient


async def main():
    # Fetch the connection string from an environment variable
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")

    # Create instance of the device client using the authentication provider
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the device client.
    await device_client.connect()

    # Send a single message
    print("Sending message...")
    await device_client.send_message("This is a message that is being sent")
    print("Message successfully sent!")

    # finally, shut down the client
    await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

```

Now, before we run the program, lets ensure that we are monitoring the event. In a different terminal, run:

```bash
# This reads all devices in the hub
az iot hub monitor-events --hub-name $IOT_HUB_NAME --output json

#or run and specify the device id
az iot hub monitor-events --hub-name $IOT_HUB_NAME --device-id $DEVICE_ID --output json

e.g.
az iot hub monitor-events --hub-name <iot-hub-name> --device-id DNT22-TempAndHumiditySensor --output json
```

Then run the script
```bash
python3 run.py
```

Notice that we get the output in the monitor-event.

---

# Reading Temp and Humidity with DHT22 via Rasberry Pi

## Pre-requisite
Make sure you have your Raspberry Pi setup

Make sure you have the DHT22 device already (you can purchase from here www.amazon.com/xyx)

Connect the DHT22 as follows:
OUT to Pin 7 (GPIO-4)
+ve to Pin 4 (5V)
-ve to Pin 6 (GND)

Set up Raspberry to work with DHT22:

Update
sudo apt update
sudo apt full-upgrade
sudo apt-get update


Dependencies for working with DHT on python in Raspberry:
sudo apt update
sudo apt install --upgrade python3-setuptools
sudo apt-get install build-essential python3-dev python3-pip libgpiod2

Update Requirements 
`requirements.txt`
```txt
azure-iot-device
adafruit-circuitpython-dht
adafruit-blinka
```
Install the requirement.txt
```bash
pip3 install -r requirements.txt
```

## Create python file

Create python file, `dht22.py`
```py
import os
import json
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient
import adafruit_dht
import board
import time
from datetime import datetime
import pytz

# Initialize the DHT22 sensor on GPIO4 (Pin 7)
dht_device = adafruit_dht.DHT22(board.D4)

# Set Sleep time
sleep_time = 5

# Function to convert Celsius to Fahrenheit
def celsius_to_fahrenheit(celsius):
    return celsius * 9.0 / 5.0 + 32.0

# Function to format the date and time with timezone
def format_timestamp():
    # Get the current time in the local timezone
    tz = pytz.timezone('America/Chicago')  # Replace with your local timezone if necessary
    now = datetime.now(tz)
    formatted_time = now.strftime("[%D - %H:%M:%S]")  # add %Z to display the timezone (CST, CDT, etc.) and %I for 12-hour and %p to show AM or PM
    return formatted_time


# Read data from DHT22 and send it to Azure IoT Hub
async def publish_sensor_data(device_client):
    try:
        # Read temperature and humidity
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity

        if humidity is not None and temperature_c is not None:
            #Convert to F
            temperature = celsius_to_fahrenheit(temperature_c)
            # Frint Temperature and Humidity with timestamp
            timestamp = format_timestamp()
            print(f"{timestamp} - Temperature: {temperature:.2f} F  Humidity: {humidity:.1f}%")
            # Create a message payload (to send)
            message = {
                "temperature": temperature,
                "humidity": humidity
            }
            message_json = json.dumps(message)

            # Send message to Azure IoT Hub
            # Send the JSON string as a message to IoT Hub
            print("Sending message...")
            await device_client.send_message(message_json)
            print("Message successfully sent!")
        else:
            print("Failed to retrieve data from DHT22 sensor")

            # Sleep for x seconds before the next reading
        await asyncio.sleep(sleep_time)
        
    except RuntimeError as error:
        # Errors happen fairly often with DHT sensors, just keep retrying
        print(f"Error: {error}")

    except asyncio.CancelledError:
      # Gracefully handle the CancelledError
      print("Task was cancelled, stopping...")
      raise  # Re-raise to properly propagate cancellation




async def main():
    # Fetch the connection string from an environment variable
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")

    # Create instance of the device client using the connection string
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the device client
    await device_client.connect()

    try:
        print(f'Reading temperature and humidity every {sleep_time} seconds. Press Ctrl+C to stop.')
        while True:
            # Publish sensor data, pass the device_client.
            await publish_sensor_data(device_client)

    # #No need for Keyboard interrupt here, its handled in publish_sensor_data function
    # except KeyboardInterrupt:
    #     # Handle the program exit gracefully when interrupted
    #     print("Program interrupted. Shutting down...")

    finally:
        # Finally, shut down the client when done
        print("Shutting down Device Client Connection...")
        await device_client.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    # Handle the program exit gracefully when interrupted
    except KeyboardInterrupt:
        print("Program terminated by user.")

```

Monitor Events:

```bash
# This reads all devices in the hub
az iot hub monitor-events --hub-name $IOT_HUB_NAME --query "event.payload" #--output json

#or run and specify the device id
az iot hub monitor-events --hub-name $IOT_HUB_NAME --device-id $DEVICE_ID  -q "select payload from devices" #--output json

e.g.
az iot hub monitor-events --hub-name <iot-hub-name> --device-id DNT22-TempAndHumiditySensor  -q "select payload from devices where deviceId = 'DNT22-TempAndHumiditySensor'" #--output json --query "event.payload"
```

SELECT payload
FROM devices
WHERE deviceId = 'DNT22-TempAndHumiditySensor'

az iot hub monitor-events -n {iothub_name} -q "select payload from devices where deviceId = 'DNT22-TempAndHumiditySensor'"

az iot hub monitor-events --hub-name <iot-hub-name>  -q "select payload from devices where deviceId = 'DNT22-TempAndHumiditySensor'"

---
### Example before actual DHT22
```py
import os
import json
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient

async def main():
    # Fetch the connection string from an environment variable
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")

    # Create instance of the device client using the connection string
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the device client.
    await device_client.connect()

    # Prepare the data to be sent as a JSON message
    temperature = 23.5  # Example temperature value
    humidity = 60.0      # Example humidity value
    
    # Create a JSON object
    message = {
        "temperature": temperature,
        "humidity": humidity 
      }
  
    # Convert the Python dictionary (message) to a JSON string
    message_json = json.dumps(message)

    # Send the JSON string as a message to IoT Hub
    print("Sending message...")
    await device_client.send_message(message_json)
    print("Message successfully sent!")

    # Finally, shut down the client
    await device_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

```

Another example (showing while loop every 5secs)
```py
import os
import json
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient

async def main():
    # Fetch the connection string from an environment variable
    conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")

    # Create instance of the device client using the connection string
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # Connect the device client
    await device_client.connect()

    try:
        while True:
            # Prepare the data to be sent as a JSON message
            temperature = 23.5  # Example temperature value
            humidity = 60.0      # Example humidity value
            
            # Create a JSON object
            message = {
                "temperature": temperature,
                "humidity": humidity 
            }

            # Convert the Python dictionary (message) to a JSON string
            message_json = json.dumps(message)

            # Send the JSON string as a message to IoT Hub
            print("Sending message...")
            await device_client.send_message(message_json)
            print("Message successfully sent!")

            # Wait for 5 seconds before sending the next message
            await asyncio.sleep(5)

    except KeyboardInterrupt:
        # Handle the program exit gracefully when interrupted
        print("Program interrupted. Shutting down...")

    finally:
        # Finally, shut down the client when done
        await device_client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())

```




