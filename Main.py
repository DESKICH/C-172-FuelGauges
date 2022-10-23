#import xpc
import socket
import struct
import time
from datetime import datetime


UDP_IP = "192.168.0.200"
UDP_PORT = 5005

UDP_IP_RPM = "192.168.0.202"
UDP_PORT_RPM = 5005

C172_MAX_FUEL_PER_TANK_LBS = 147
C172_MAX_FUEL_PER_TANK_KG = 76
C172_MAX_OIL_TEMP = 245
C172_MIN_OIL_TEMP = 75
C172_MAX_OIL_PRES = 115
BYTE = 255

DISPLAY_DIM = 100
Suction_DIM = 100

#client = xpc.XPlaneConnect()
#AvionicsList=["sim/cockpit2/fuel/fuel_level_indicated_left","sim/cockpit2/fuel/fuel_level_indicated_right","sim/cockpit2/engine/indicators/oil_temperature_deg_C","sim/cockpit2/engine/indicators/oil_pressure_psi","sim/cockpit/misc/vacuum","sim/cockpit/electrical/avionics_on","sim/cockpit2/engine/indicators/engine_speed_rpm","sim/cockpit2/electrical/battery_amps"]


POWER_OFF = False

while True:
	startTime = datetime.now()
	try:
		SIM_RESPONSE = client.getDREFs(AvionicsList)
		print(AvionicsList)
	except:
		print("UNABLE TO RECIEVE SIM RESPONSE")

	# print("GET DATA: "+str(datetime.now() - startTime))

	#Limit indications to maximum in case that the sim model contains more fuel than can be actually indicated

	#FUEL LEFT AND RIGHT
	if SIM_RESPONSE[0][0] < C172_MAX_FUEL_PER_TANK_KG:
		Fuel_L_indication = int(SIM_RESPONSE[0][0] / C172_MAX_FUEL_PER_TANK_KG*BYTE)
	else:
		Fuel_L_indication = BYTE
	if SIM_RESPONSE[1][0]<C172_MAX_FUEL_PER_TANK_KG:
		Fuel_R_indication = int(SIM_RESPONSE[1][0] / C172_MAX_FUEL_PER_TANK_KG*BYTE)
	else:
		Fuel_R_indication = BYTE

	# OIL TEMP
	if SIM_RESPONSE[2][0] > C172_MIN_OIL_TEMP:
		if SIM_RESPONSE[2][0] < C172_MAX_OIL_TEMP:
			Oil_Temp_indication = int(( (SIM_RESPONSE[2][0]) - C172_MIN_OIL_TEMP) / (C172_MAX_OIL_TEMP - C172_MIN_OIL_TEMP) * BYTE)
		else:
			Oil_Temp_indication = BYTE
	else:
		Oil_Temp_indication = 0

	#OIL PRESSURE
	if SIM_RESPONSE[3][0] < C172_MAX_OIL_PRES:
		Oil_Pres_indication = int(SIM_RESPONSE[3][0] / C172_MAX_OIL_PRES*BYTE)
	else:
		Oil_Pres_indication = BYTE

	#SUCTION/VACUUM
	if SIM_RESPONSE[4][0]<3:
		Suction = int(SIM_RESPONSE[4][0]/3*118)
	elif SIM_RESPONSE[4][0]<7:
		Suction = int(SIM_RESPONSE[4][0]/7*303)
	else:
		Suction = 304

	# print("FUEL CONVERSION: "+str(datetime.now() - startTime))

	# print("Fuel_L:"+str(Fuel_L_indication))
	# print("Fuel_R:"+str(Fuel_R_indication))
	# print("Oil_T:"+str(Oil_Temp_indication))
	# print("Oil_P:"+str(Oil_Pres_indication))
	# print("Suc:"+str(SIM_RESPONSE[4][0]))
	# print("-------------------")

	#MESSAGE TO RPI FUEL GAUGES
	MESSAGE = struct.pack("B",Fuel_L_indication)
	MESSAGE += struct.pack("B",Fuel_R_indication)
	MESSAGE += struct.pack("B",Oil_Temp_indication)
	MESSAGE += struct.pack("B",Oil_Pres_indication)
	MESSAGE += struct.pack(">H",Suction)
	MESSAGE += struct.pack("B", DISPLAY_DIM)
	MESSAGE += struct.pack("B", Suction_DIM)
	if POWER_OFF:
		MESSAGE += struct.pack("B", 0)
	else:
		#AVIONIC HAVE POWER
		if SIM_RESPONSE[5][0]>0:
			MESSAGE += struct.pack("B", 1)
		else:
			MESSAGE += struct.pack("B", 2)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
	# print("FUEL SEND: "+str(datetime.now() - startTime))
	#--------------------------------------------------------------
	#Engine speed
	if SIM_RESPONSE[6][0]<3500:
		Prop_Speed = int(SIM_RESPONSE[6][0] / 3500 * 600)
	else:
		Prop_Speed = 600

	#BATTERY AMPS
	if SIM_RESPONSE[7][0]>-60:
		if SIM_RESPONSE[7][0]<60:
			Bat_Amps = int(127 + (SIM_RESPONSE[7][0] / 60 * 128))
		else:
			Bat_Amps = 255
	else:
		Bat_Amps = 0
	# print("RPM CONVERSION: "+str(datetime.now() - startTime))
	#MESSAGE TO RPI RPM GAUGES
	# print(Prop_Speed)
	MESSAGE = struct.pack(">H",Prop_Speed)
	MESSAGE += struct.pack("B",Bat_Amps)
	MESSAGE += struct.pack("B", DISPLAY_DIM)
	if POWER_OFF:
		MESSAGE += struct.pack("B", 0)
	else:
		MESSAGE += struct.pack("B", 1)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto(MESSAGE, (UDP_IP_RPM, UDP_PORT_RPM))
	# print("RPM SEND: "+str(datetime.now() - startTime))
	#--------------------------------------------------------------
	# print("_______________________________")
	time.sleep(0.03)
