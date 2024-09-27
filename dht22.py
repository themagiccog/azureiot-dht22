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
