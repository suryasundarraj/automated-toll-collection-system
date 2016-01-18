'''*********************************************************************************
SERVER - AUTOMATED TOLL BOOTH
*********************************************************************************'''
#Import the Modules Required
from pubnub import Pubnub
import datetime

vehicleDetails = dict()
vehicleRfid = dict()
vehicleSetting = dict()
vehicleTransaction = dict()
TOLL_CHARGE = 50
TOLL_CROSSED = "NH14 TOLL"
l_date = " "
# Initialize the Pubnub Keys 
g_pub_key = "pub-c-913ab39c-d613-44b3-8622-2e56b8f5ea6d"
g_sub_key = "sub-c-8ad89b4e-a95e-11e5-a65d-02ee2ddab7fe"
#Available Balance, Name, V. Type
vehicleDetails["KA01M1234"] = [500,"RAJ","LMV",0]
vehicleDetails["KA03M4321"] = [500,"SUNDAR","LMV",0]
vehicleDetails["KA51M0321"] = [500,"SURYA","LMV",0]
vehicleRfid = {"50008AB784E9":"KA01M1234","39005D5CFDC5":"KA03M4321","39005E641E1D":"KA51M0321"}

'''****************************************************************************************
Function Name 	:	init
Description		:	Initalize the pubnub keys and Starts Subscribing 
Parameters 		:	None
****************************************************************************************'''
def init():
	#Pubnub Initialization
	global pubnub 
	pubnub = Pubnub(publish_key=g_pub_key,subscribe_key=g_sub_key)
	pubnub.subscribe(channels='vehicleIdentificanDevice-resp', callback=callback, error=callback, reconnect=reconnect, disconnect=disconnect)
	pubnub.subscribe(channels='vehicleIdentificanApp-req', callback=appcallback, error=appcallback, reconnect=reconnect, disconnect=disconnect)

'''****************************************************************************************
Function Name 	:	appSetting
Description		:	Once App request for the settings, server responds with the details
					and block status
Parameters 		:	p_vehicleNumber - Vehicle Number 
					p_blockStatus - Responds with block status is active
****************************************************************************************'''
def appSetting(p_vehicleNumber,p_blockStatus):
	if(p_vehicleNumber != None and p_blockStatus != None):
		if(vehicleDetails.has_key(p_vehicleNumber)):
			vehicleSetting["vehicleNumber"] = p_vehicleNumber
			vehicleSetting["availableBal"] = vehicleDetails[p_vehicleNumber][0]
			vehicleSetting["ownerName"] = vehicleDetails[p_vehicleNumber][1]
			vehicleSetting["vehicleType"] = vehicleDetails[p_vehicleNumber][2]
			vehicleDetails[p_vehicleNumber][3] = int(p_blockStatus)
			vehicleSetting["blockStatus"] = vehicleDetails[p_vehicleNumber][3]
			# print vehicleSetting
			if(vehicleDetails[p_vehicleNumber][3] == 0):
				pubnub.publish(channel=p_vehicleNumber, message=vehicleSetting)
			else:
				pubnub.publish(channel=p_vehicleNumber, message={"warning":"Vehicle is Blocked"})
		else:
			pubnub.publish(channel=p_vehicleNumber, message={"warning":"Vehicle Not Registered with the Automated System"})
	else:
		pass


'''****************************************************************************************
Function Name 	:	generalSetting
Description		:	Once App request for the settings, server responds with the details
Parameters 		:	p_vehicleNumber - Vehicle Number 
****************************************************************************************'''
def generalSetting(p_vehicleNumber):
	if(p_vehicleNumber != None):
		if(vehicleDetails.has_key(p_vehicleNumber)):
			if(vehicleDetails[p_vehicleNumber][3] == 0):
				vehicleSetting["vehicleNumber"] = p_vehicleNumber
				vehicleSetting["availableBal"] = vehicleDetails[p_vehicleNumber][0]
				vehicleSetting["ownerName"] = vehicleDetails[p_vehicleNumber][1]
				vehicleSetting["vehicleType"] = vehicleDetails[p_vehicleNumber][2]
				pubnub.publish(channel=p_vehicleNumber, message=vehicleSetting)
			else:
				appSetting(p_vehicleNumber,vehicleDetails[p_vehicleNumber][3])
		else:
			pubnub.publish(channel=p_vehicleNumber, message={"warning":"Vehicle Not Registered with the Automated System"})
	else:
		pass

'''****************************************************************************************
Function Name 	:	vehicleIdentified
Description		:	When the vehicle is scanned, the amount is deducted
Parameters 		:	p_RfidNumber - Unique RFID Number
****************************************************************************************'''
def vehicleIdentified(p_RfidNumber):
	if(vehicleRfid.has_key(p_RfidNumber)):
		message = {}
		l_todayDate = datetime.datetime.today()
		l_todayDate = l_todayDate.date()
		l_endTime = datetime.datetime.now()
		l_date1 = str(l_todayDate.day) + "/" + str(l_todayDate.month) + "/" + str(l_todayDate.year) + " " + str(l_endTime.hour) + ":" + str(l_endTime.minute) + ":" + str(l_endTime.second)
		l_date = str(l_todayDate.day) + "/" + str(l_todayDate.month) + "/" + str(l_todayDate.year)
		l_time = str(l_endTime.hour) + ":" + str(l_endTime.minute) + ":" + str(l_endTime.second)
		if(vehicleDetails[vehicleRfid[p_RfidNumber]][3] <= 0):
			if(vehicleDetails[vehicleRfid[p_RfidNumber]][0] < 0):
				message["warning"] = "Please Recharge"
			else:
				message["warning"] = " "
			vehicleDetails[vehicleRfid[p_RfidNumber]][0] = vehicleDetails[vehicleRfid[p_RfidNumber]][0] - 50
			message["vehicleNumber"] = vehicleRfid[p_RfidNumber]
			message["availableBal"] = vehicleDetails[vehicleRfid[p_RfidNumber]][0]
			message["ownerName"] = vehicleDetails[vehicleRfid[p_RfidNumber]][1]
			message["vehicleType"] = vehicleDetails[vehicleRfid[p_RfidNumber]][2]
			message["amtDeducted"] = TOLL_CHARGE
			message["NHCrossed"] = TOLL_CROSSED
			message["dateTime"] = l_date
			message["dateTime1"] = l_time
			if(not(vehicleTransaction.has_key(vehicleRfid[p_RfidNumber]))):
				vehicleTransaction[vehicleRfid[p_RfidNumber]] = []
			vehicleTransaction[vehicleRfid[p_RfidNumber]].append([l_date1,message["NHCrossed"],50,"--",vehicleDetails[vehicleRfid[p_RfidNumber]][0]])
			pubnub.publish(channel=vehicleRfid[p_RfidNumber], message=message)
		else:
			message["NHCrossed"] = TOLL_CROSSED	
			message["dateTime"] = l_date
			message["dateTime1"] = l_time
			message["warning"] = "Vehicle is Blocked"
			pubnub.publish(channel=vehicleRfid[p_RfidNumber], message=message)
	else:
		pass

'''****************************************************************************************
Function Name 	:	appRecharge
Description		:	Rechares the amount for each user
Parameters 		:	p_vehicleNum - Vehicle Number
					p_rechargeAmt - Required Recharge Amount
****************************************************************************************'''
def appRecharge(p_vehicleNum,p_rechargeAmt):
	if(vehicleDetails.has_key(p_vehicleNum)):
		vehicleDetails[p_vehicleNum][0] = vehicleDetails[p_vehicleNum][0] + int(p_rechargeAmt)
		vehicleSetting["vehicleNumber"] = p_vehicleNum
		vehicleSetting["availableBal"] = vehicleDetails[p_vehicleNum][0]
		vehicleSetting["ownerName"] = vehicleDetails[p_vehicleNum][1]
		vehicleSetting["vehicleType"] = vehicleDetails[p_vehicleNum][2]
		pubnub.publish(channel=p_vehicleNum, message=vehicleSetting)
		l_todayDate = datetime.datetime.today()
		l_todayDate = l_todayDate.date()
		l_endTime = datetime.datetime.now()
		l_date = str(l_todayDate.day) + "/" + str(l_todayDate.month) + "/" + str(l_todayDate.year) + " " + str(l_endTime.hour) + ":" + str(l_endTime.minute) + ":" + str(l_endTime.second)
		if(not vehicleTransaction.has_key(p_vehicleNum)):
			vehicleTransaction[p_vehicleNum] = []
		vehicleTransaction[p_vehicleNum].append([l_date,"--","--",p_rechargeAmt,vehicleDetails[p_vehicleNum][0]])
	else:
		pass

'''****************************************************************************************
Function Name 	:	appTransaction
Description		:	When app requests for the Transaction details, responds the details
					of the previous transaction
Parameters 		:	p_vehicleNum - Vehicle Number
****************************************************************************************'''
def appTransaction(p_vehicleNum):
	if(vehicleTransaction.has_key(p_vehicleNum)): 
		message = {}
		length = {}
		for key, value in vehicleTransaction.items():
			length[key] = len([item for item in value if item])
		for i in range(length[p_vehicleNum]):
			message[i] = vehicleTransaction[p_vehicleNum][i]
		pubnub.publish(channel=p_vehicleNum+p_vehicleNum, message=message)
		message.clear()
	else:
		pass

'''****************************************************************************************
Function Name 	:	callback
Description		:	Waits for the message from the vehicleIdentificanDevice-resp channel
Parameters 		:	message - Sensor Status sent from the hardware
					channel - channel for the callback
****************************************************************************************'''
def callback(message, channel):
	if(message.has_key("vehicleRFIDnum")):
		vehicleIdentified(message["vehicleRFIDnum"])
	else:
		pass

'''****************************************************************************************
Function Name 	:	appcallback
Description		:	Waits for the Request sent from the APP 
Parameters 		:	message - Request sent from the app
					channel - channel for the appcallback
****************************************************************************************'''
def appcallback(message, channel):
	# 0 - Update Status, 1 - Rechare Amt, 2 - Transaction History 
	if(message.has_key("requester") and message.has_key("requestType")):
		if(message["requestType"] == 0 and message.has_key("vehicleNumber")):
			if(message.has_key("requestValue")):
				appSetting(message["vehicleNumber"],message["requestValue"])
			else:
				generalSetting(message["vehicleNumber"])
		elif(message["requestType"] == 1 and message.has_key("vehicleNumber")):
			appRecharge(message["vehicleNumber"],message["rechargeAmt"])
		elif(message["requestType"] == 2 and message.has_key("vehicleNumber")):
			appTransaction(message["vehicleNumber"])
		else:
			pass
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

 
