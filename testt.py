import pygame
import serial
import socket
import struct
import threading
import RPi.GPIO as GPIO
from subprocess import call

#SETUP UDP RECIEVER - PUT IP OF SAPBERRYBERRY
UDP_IP = "0.0.0.0"
UDP_PORT = 49006

#DIM VARS ARE FROM 0 TO 100
Suction_DIM=100
DISPLAY_DIM=100

C172_MAX_FUEL_PER_TANK_KG = 76
C172_MAX_OIL_TEMP = 245
C172_MIN_OIL_TEMP = 75
C172_MAX_OIL_PRES = 115
BYTE = 255

print("SETTING GPIO")
#SETUP GPIO TO CONTROLL DISPLAY BACKLIGHT
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
#BCM 18 = GPIO 12 = PWM PIN
#GPIO.setup(12, GPIO.OUT)
#PIN, FREQUENCY
#DisplayBacklight = GPIO.PWM(12, 100)
#start at half brightness
#DisplayBacklight.start(DISPLAY_DIM)

#SETUP PYGAME 
pygame.init()
print("PG INIT")
pygame.mouse.set_visible(False)
MainBG = (21,21,21)
Screen = pygame.display.set_mode((800,480), pygame.FULLSCREEN)
Screen.fill(MainBG)
Screen.blit(pygame.image.load(r'LoadingScreen.jpg'),(0,0))
pygame.display.update()
print("PG DP UPDATE")
# #CREATE SPRITE HOLDERS
FuelSprites=[]
OilTempSprites=[]
OilPressSprites=[]

print("LOADING FUEL")
#LOAD SPRITES INTO SPRITE HOLDERS - 10 are for power on animation - 265 (1 byte) are for indications
for x in range(266):
	if(x+1<10):
		FuelSprites.append(pygame.image.load(r'Fuel/Fuel000'+str(x+1)+'.jpg'))
		OilTempSprites.append(pygame.image.load(r'OilTemp/OilTemp000'+str(x+1)+'.jpg'))		
	elif(x+1<100):
		FuelSprites.append(pygame.image.load(r'Fuel/Fuel00'+str(x+1)+'.jpg'))
		OilTempSprites.append(pygame.image.load(r'OilTemp/OilTemp00'+str(x+1)+'.jpg'))
	else:
		FuelSprites.append(pygame.image.load(r'Fuel/Fuel0'+str(x+1)+'.jpg'))
		OilTempSprites.append(pygame.image.load(r'OilTemp/OilTemp0'+str(x+1)+'.jpg'))

print("LOADING PRESSURE")
#Oil press indicates 0 when powered off - therefore no powero on animation needed
for x in range(256):
	if(x+1<10):
		OilPressSprites.append(pygame.image.load(r'OilPress/OilPress000'+str(x+1)+'.jpg'))
	elif(x+1<100):
		OilPressSprites.append(pygame.image.load(r'OilPress/OilPress00'+str(x+1)+'.jpg'))
	else:
		OilPressSprites.append(pygame.image.load(r'OilPress/OilPress0'+str(x+1)+'.jpg'))

#UPDATE SCREEN WHEN ALL LOADED
Screen.fill(MainBG)
Screen.blit(FuelSprites[0],(174,32))
Screen.blit(FuelSprites[0],(485,32))
Screen.blit(OilTempSprites[0],(174,280))
Screen.blit(OilPressSprites[0],(485,280))
pygame.display.update()

print("FINISHED LOADING")
def UDP_COMM_THREAD(UDP_IP,UDP_PORT):
	print("THREAD STARTED")
	#OCREATE AND OPEN UDP RECIEVER
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	
	global Fuel_Left, Fuel_Right,Oil_Temp, Oil_Press, Suction, POWERED_ON
	while True:
		data, addr = sock.recvfrom(30)

		Fuel_Left = float(struct.unpack('>f', bytearray([data[4],data[5],data[6],data[7]]))[0])
		Fuel_Right = float(struct.unpack('>f', bytearray([data[8],data[9],data[10],data[11]]))[0])
		Oil_Temp = float(struct.unpack('>f', bytearray([data[12],data[13],data[14],data[15]]))[0])
		Oil_Press = float(struct.unpack('>f', bytearray([data[16],data[17],data[18],data[19]]))[0])
		Suction = float(struct.unpack('>f', bytearray([data[20],data[21],data[22],data[23]]))[0])
		POWERED_ON = bool(struct.unpack('>f', bytearray([data[24],data[25],data[26],data[27]]))[0])

		print(Oil_Press)

def main():
	#Set defaults in case there is no UDP connection to do so
	global Fuel_Left, Fuel_Right,Oil_Temp, Oil_Press, Suction, POWERED_ON
	Fuel_Left = 0.0
	Fuel_Right = 0.0
	Oil_Temp = 0.0
	Oil_Press = 0.0
	Suction = 0.0
	POWERED_ON = True

	#Start recieveing info
	UDP_COMM = threading.Thread(target=UDP_COMM_THREAD, args=(UDP_IP,UDP_PORT))
	UDP_COMM.start()

	clock = pygame.time.Clock()

	PLAY = True
	GAUGES_FRAMES_OFFSET = 0
	
	#OPEN SERIAL CONNECTION TO HMI DISPLAY
	ANIM_POWER_ON = 0
	Fuel_L_Indication=0
	Fuel_R_Indication=0
	Oil_T_Indication=0
	Oil_P_Indication=0
	Suction_Indication=0

	Fuel_Left_byte = 0 
	Fuel_Right_byte = 0
	Oil_Temp_byte = 0 
	Oil_Press_byte = 0 
	Suction_byte = 0

	#OPEN SERIAL CONNECTION TO HMI DISPLAY
	ser = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=5)
	#PLAY LOOP	
	while PLAY:
		#This must be here, oterways pygame freezes
		for event in pygame.event.get():
			pass
		#------------------------------------------

		#FUEL LEFT
		if Fuel_Left < C172_MAX_FUEL_PER_TANK_KG:
			Fuel_Left_byte = int(Fuel_Left / C172_MAX_FUEL_PER_TANK_KG * BYTE) 
		else:
			Fuel_Left_byte = BYTE
		#FUEL RIGHT
		if Fuel_Right<C172_MAX_FUEL_PER_TANK_KG:
			Fuel_Right_byte = int(Fuel_Right / C172_MAX_FUEL_PER_TANK_KG * BYTE) 
		else:
			Fuel_Right_byte = BYTE
		# OIL TEMP
		if Oil_Temp > C172_MIN_OIL_TEMP:
			if Oil_Temp < C172_MAX_OIL_TEMP:
				Oil_Temp_byte = int(( (Oil_Temp) - C172_MIN_OIL_TEMP) / (C172_MAX_OIL_TEMP - C172_MIN_OIL_TEMP) * BYTE) 
			else:
				Oil_Temp_byte = BYTE
		else:
			Oil_Temp_byte = 0

		#OIL PRESSURE
		if Oil_Press < C172_MAX_OIL_PRES:
			Oil_Press_byte = int(Oil_Press / C172_MAX_OIL_PRES * BYTE) 
		else:
			Oil_Press_byte = BYTE

		#SUCTION/VACUUM
		if Suction<3:
			Suction_Indication = int(Suction/3*118)
		elif Suction<7:
			Suction_Indication = int(Suction/7*303)
		else:
			Suction_Indication = 304

		if POWERED_ON:
			#Animate gaugle needles powering on
			if ANIM_POWER_ON<10:
				ANIM_POWER_ON+=1
				Fuel_L_Indication += int((Fuel_Left_byte-Fuel_L_Indication)/2)
				Fuel_R_Indication += int((Fuel_Right_byte-Fuel_R_Indication)/2)
				Oil_T_Indication += int((Oil_Temp_byte-Oil_T_Indication)/2)
				Oil_P_Indication += int((Oil_Press_byte-Oil_P_Indication)/2)
			else:
				Fuel_L_Indication=int(Fuel_Left_byte)
				Fuel_R_Indication=int(Fuel_Right_byte)
				Oil_T_Indication=int(Oil_Temp_byte)
				Oil_P_Indication=int(Oil_Press_byte)
		else:
			if ANIM_POWER_ON>0:
				ANIM_POWER_ON-=1
				Fuel_L_Indication += int((0-Fuel_L_Indication)/2)
				Fuel_R_Indication += int((0-Fuel_R_Indication)/2)
				Oil_T_Indication += int((0-Oil_T_Indication)/2)
				Oil_P_Indication += int((0-Oil_P_Indication)/2)
			else:
				Fuel_L_Indication=0
				Fuel_R_Indication=0
				Oil_T_Indication=0
				Oil_P_Indication=0
	
		#UPDATE SCREEN				
		Screen.fill(MainBG)
		Screen.blit(FuelSprites[ANIM_POWER_ON+Fuel_L_Indication],(174,32))
		Screen.blit(FuelSprites[ANIM_POWER_ON+Fuel_R_Indication],(485,32))
		Screen.blit(OilTempSprites[ANIM_POWER_ON+Oil_T_Indication],(174,280))
		Screen.blit(OilPressSprites[ANIM_POWER_ON+Oil_P_Indication],(485,280))
		pygame.display.update()

		# #DisplayBacklight.ChangeDutyCycle(DISPLAY_DIM)
		# #update DIMMING at HMI display
		suct_cmd_str = "dim="+str(Suction_DIM)+"ÿÿÿ"
		suct_cmd_ba = bytearray()
		suct_cmd_ba.extend(map(ord,suct_cmd_str))
		ser.write(suct_cmd_ba)
		#update SUCTION at HTMI display
		suct_cmd_str = "p0.pic="+str(Suction_Indication)+"ÿÿÿ"
		suct_cmd_ba = bytearray()
		suct_cmd_ba.extend(map(ord,suct_cmd_str))
		ser.write(suct_cmd_ba)
		#Aim at 30 pfs
		clock.tick(33)


if __name__ == '__main__':    
    main()
    #DisplayBacklight.stop()
    #GPIO.cleanup()
    pygame.quit()
    #SHUT DOWN BERRY ON EXIT
    #call("sudo nohup shutdown -h now", shell=True)
    quit()