'''*********************************************************************************
TESTAPP - AUTOMATED TOLL BOOTH
*********************************************************************************'''
from pubnub import Pubnub
from threading import Thread
import sys

g_pub_key = "pub-c-913ab39c-d613-44b3-8622-2e56b8f5ea6d"
g_sub_key = "sub-c-8ad89b4e-a95e-11e5-a65d-02ee2ddab7fe"
g_vechileData = dict()

def init():
	#Pubnub Key Initialization
	global pubnub 
	pubnub = Pubnub(publish_key=g_pub_key,subscribe_key=g_sub_key)
	pubnub.subscribe(channels='KA01M1234', callback=callback, error=callback,
					connect=connect, reconnect=reconnect, disconnect=disconnect)

def callback(message, channel):
	g_vechileData.update(message)
	print g_vechileData

def dataHandling(stdin):
		l_action = int(stdin.readline().strip())
		if(l_action == 0):
			pubnub.publish(channel='vehicleIdentificanApp-req',message={"requester":"APP","requestType":0, "vehicleNumber":"KA01M1234"})
		elif(l_action == 1):
			pubnub.publish(channel='vehicleIdentificanApp-req', 
					message={"requester":"APP","requestType":1, "vehicleNumber":"KA01M1234", "rechargeAmt":500})
		elif(l_action == 2):
			pubnub.publish(channel='vehicleIdentificanApp-req', 
					message={"requester":"APP","requestType":2, "vehicleNumber":"KA01M1234"})
		elif(l_action == 3):
			print g_vechileData
		else:
			pass
			
def error(message):
    print("ERROR : " + str(message))
  
def connect(message):
    print "CONNECTED"
  
def reconnect(message):
	print("RECONNECTED")
  
def disconnect(message):
	print("DISCONNECTED")

if __name__ == '__main__':
	init()
	while True:
		t1 = Thread(target=dataHandling, args=(sys.stdin,))
		t1.start()
		t1.join()

		
#End of the Script 
##*****************************************************************************************************##
	