# sudo apt update
# sudo apt install --upgrade python3-setuptools
# sudo apt-get install build-essential python3-dev python3-pip libgpiod2

# Run in virtual environment:
# python3 -m venv env
# source env/bin/activate #deactivate

# create requirements.txt
# ```
# adafruit-circuitpython-dht
# adafruit-blinka
# pytz
# ```

# pip3 install -r requirements.txt
# or install individually
# pip3 install adafruit-circuitpython-dht
# pip3 install adafruit-blinka
# pip3 install pytz


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


# ### Example before actual DHT22
# ```py
# import os
# import json
# import asyncio
# from azure.iot.device.aio import IoTHubDeviceClient

# async def main():
#     # Fetch the connection string from an environment variable
#     conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")

#     # Create instance of the device client using the connection string
#     device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

#     # Connect the device client.
#     await device_client.connect()

#     # Prepare the data to be sent as a JSON message
#     temperature = 23.5  # Example temperature value
#     humidity = 60.0      # Example humidity value
    
#     # Create a JSON object
#     message = {
#         "temperature": temperature,
#         "humidity": humidity 
#       }
  
#     # Convert the Python dictionary (message) to a JSON string
#     message_json = json.dumps(message)

#     # Send the JSON string as a message to IoT Hub
#     print("Sending message...")
#     await device_client.send_message(message_json)
#     print("Message successfully sent!")

#     # Finally, shut down the client
#     await device_client.shutdown()


# if __name__ == "__main__":
#     asyncio.run(main())

# ```

# Another example (showing while loop every 5secs)
# ```py
# import os
# import json
# import asyncio
# from azure.iot.device.aio import IoTHubDeviceClient

# async def main():
#     # Fetch the connection string from an environment variable
#     conn_str = os.getenv("IOTHUB_DEVICE_CONNECTION_STRING")

#     # Create instance of the device client using the connection string
#     device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

#     # Connect the device client
#     await device_client.connect()

#     try:
#         while True:
#             # Prepare the data to be sent as a JSON message
#             temperature = 23.5  # Example temperature value
#             humidity = 60.0      # Example humidity value
            
#             # Create a JSON object
#             message = {
#                 "temperature": temperature,
#                 "humidity": humidity 
#             }

#             # Convert the Python dictionary (message) to a JSON string
#             message_json = json.dumps(message)

#             # Send the JSON string as a message to IoT Hub
#             print("Sending message...")
#             await device_client.send_message(message_json)
#             print("Message successfully sent!")

#             # Wait for 5 seconds before sending the next message
#             await asyncio.sleep(5)

#     except KeyboardInterrupt:
#         # Handle the program exit gracefully when interrupted
#         print("Program interrupted. Shutting down...")

#     finally:
#         # Finally, shut down the client when done
#         await device_client.shutdown()

# if __name__ == "__main__":
#     asyncio.run(main())

# ```




