import paho.mqtt.client as mqtt
import time, threading, ssl
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

class FloatModbusClient(ModbusClient):
    def read_float(self, address, number=1):
        reg_l = self.read_holding_registers(address, number * 2)
        if reg_l:
            return [utils.decode_ieee(f) for f in utils.word_list_to_long(reg_l)]
        else:
            return None

    def write_float(self, address, floats_list):
        b32_l = [utils.encode_ieee(f) for f in floats_list]
        b16_l = utils.long_list_to_word(b32_l)
        return self.write_multiple_registers(address, b16_l)


receivedMessages = []

def on_message(client, userdata, message):
  print("Received operation " + str(message.payload))
  if (message.payload.startswith("510")):
     print("Simulating device restart...")
     publish("s/us", "501,c8y_Restart");
     print("...restarting...")
     time.sleep(1)
     publish("s/us", "503,c8y_Restart");
     print("...done...")

def sendMeasurements():
	while True:
	c = FloatModbusClient(host='192.168.1.10', port=502, auto_open=True)
	bits = c.read_holding_registers(1000,2)
	write = c.write_multiple_registers(1002,[1])
	analog = c.read_float(1003,1)
	write_dec = c.write_float(1005,[10.11])
	a=analog[1]
	print(bits)
	print(analog)
    	publish("s/us", "200,Potentiometer,Volts," + str(a) + ",V");
  	thread = threading.Timer(3, sendMeasurements)
    	thread.daemon=True
    	thread.start()
	time.sleep(3)


def publish(topic, message, waitForAck = False):
  mid = client.publish(topic, message, 2)[1]
  if (waitForAck):
    while mid not in receivedMessages:
      time.sleep(0.25)

def on_publish(client, userdata, mid):
  receivedMessages.append(mid)

client = mqtt.Client(client_id="<<clientId>>")
client.username_pw_set("canautomotion/mgiri@canautomotion.com", "Canauto2006")
client.on_message = on_message
client.on_publish = on_publish

client.connect("canautomotion.cumulocity.com", 1883)
client.loop_start()
publish("s/us", "100,Janztec,Janztec MQTT", True)
publish("s/us", "110,000000005feb6a43,Galil Janztec,Rev0.1")
client.subscribe("s/ds")
sendMeasurements()




