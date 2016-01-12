'''*********************************************************************************
SERVER - KITCHEN TRACKER
*********************************************************************************'''
#Import the Modules Required
from pubnub import Pubnub
import datetime

carDetails = dict()
carRfid = dict()
carSetting = dict()
TIME_ZONE = "Asia/Kolkata"
# Initialize the Pubnub Keys 
g_pub_key = "pub-c-913ab39c-d613-44b3-8622-2e56b8f5ea6d"
g_sub_key = "sub-c-8ad89b4e-a95e-11e5-a65d-02ee2ddab7fe"
#Available Balance, Name, V. Type
carDetails["KA01M1234"] = [500,"RAJ","LMV",0]
carDetails["KA03M4321"] = [500,"SUNDAR","LMV",0]
carDetails["KA51M0321"] = [500,"SURYA","LMV",0]
carRfid = {"50008AB784E9":"KA01M1234","39005D5CFDC5":"KA03M4321","39005E641E1D":"KA51M0321"}

'''****************************************************************************************

Function Name 	:	init
Description		:	Initalize the pubnub keys and Starts Subscribing 
Parameters 		:	None

****************************************************************************************'''
def init():
	#Pubnub Initialization
	global pubnub 
	pubnub = Pubnub(publish_key=g_pub_key,subscribe_key=g_sub_key)
	pubnub.subscribe(channels='carIdentificanDevice-resp', callback=callback, error=callback, reconnect=reconnect, disconnect=disconnect)
	pubnub.subscribe(channels='carIdentificanApp-req', callback=appcallback, error=appcallback, reconnect=reconnect, disconnect=disconnect)

def appSetting(p_carNumber):
	if(carDetails.has_key(p_carNumber)):
		carSetting["vechileNumber"] = p_carNumber
		carSetting["availableBal"] = carDetails[p_carNumber][0]
		carSetting["ownerName"] = carDetails[p_carNumber][1]
		carSetting["vechileType"] = carDetails[p_carNumber][2]
		print carSetting
		print pubnub.publish(channel=p_carNumber, message=carSetting)
	else:
		pubnub.publish(channel=p_carNumber, message='Car Not Registered with the Automated System')

def vechileIdentified(p_RfidNumber):
	if(carRfid.has_key(p_RfidNumber)):
		message = {}
		if(carDetails[carRfid[p_RfidNumber]][0] < 0):
			message["warning"] = "Please Recharge"
		else:
			message["warning"] = " "
		carDetails[carRfid[p_RfidNumber]][0] = carDetails[carRfid[p_RfidNumber]][0] - 50
		message["vechileNumber"] = carRfid[p_RfidNumber]
		message["availableBal"] = carDetails[carRfid[p_RfidNumber]][0]
		message["ownerName"] = carDetails[carRfid[p_RfidNumber]][1]
		message["vechileType"] = carDetails[carRfid[p_RfidNumber]][2]
		message["amtDeducted"] = 50
		message["NHCrossed"] = "NH14 TOLL"
		l_todayDate = datetime.datetime.today()
		l_todayDate = l_todayDate.date()
		l_endTime = datetime.datetime.now()
		l_date = str(l_todayDate.day) + "/" + str(l_todayDate.month) + "/" + str(l_todayDate.year) + "  " + str(l_endTime.hour) + ":" + str(l_endTime.minute) + ":" + str(l_endTime.second)
		message["dateTime"] = l_date
		print message
		pubnub.publish(channel=carRfid[p_RfidNumber], message=message)
	else:
		pass

def appRecharge(p_vechileNum,p_rechargeAmt):
	if(carDetails.has_key(p_vechileNum)):
		carDetails[p_vechileNum][0] = carDetails[p_vechileNum][0] + int(p_rechargeAmt)
		carSetting["vechileNumber"] = p_vechileNum
		carSetting["availableBal"] = carDetails[p_vechileNum][0]
		carSetting["ownerName"] = carDetails[p_vechileNum][1]
		carSetting["vechileType"] = carDetails[p_vechileNum][2]
		print carSetting
		print pubnub.publish(channel=p_vechileNum, message=carSetting)
	else:
		pass

'''****************************************************************************************

Function Name 	:	callback
Description		:	Waits for the message from the kitchenDevice-resp channel
Parameters 		:	message - Sensor Status sent from the hardware
					channel - channel for the callback
	
****************************************************************************************'''
def callback(message, channel):
	if(message.has_key("carRFIDnum")):
		vechileIdentified(message["carRFIDnum"])
	else:
		pass

'''****************************************************************************************

Function Name 	:	appcallback
Description		:	Waits for the Request sent from the APP 
Parameters 		:	message - Request sent from the app
					channel - channel for the appcallback

****************************************************************************************'''
def appcallback(message, channel):
	if(message.has_key("requester") and message.has_key("requestType")):
		if(message["requestType"] == 0):
			appSetting(message["vechileNumber"])
		elif(message["requestType"] == 1):
			appRecharge(message["vechileNumber"],message["rechargeAmt"])
	else:
		pass

'''****************************************************************************************

Function Name 	:	error
Description		:	If error in the channel, prints the error
Parameters 		:	message - error message

****************************************************************************************'''
def error(message):
    print("ERROR : " + str(message))

'''****************************************************************************************

Function Name 	:	reconnect
Description		:	Responds if server connects with pubnub
Parameters 		:	message

****************************************************************************************'''
def reconnect(message):
    print("RECONNECTED")

'''****************************************************************************************

Function Name 	:	disconnect
Description		:	Responds if server disconnects from pubnub
Parameters 		:	message

****************************************************************************************'''
def disconnect(message):
    print("DISCONNECTED")

'''****************************************************************************************

Function Name 	:	__main__
Description		:	Conditional Stanza where the Script starts to run
Parameters 		:	None

****************************************************************************************'''
if __name__ == '__main__':
	#Initialize the Script
	init()

#End of the Script 
##*****************************************************************************************************##

 
