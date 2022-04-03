import pygame
import socket
import threading
#import RPi.GPIO as GPIO
#from subprocess import call
#SETUP UDP RECIEVER - PUT IP OF SAPBERRYBERRY
UDP_IP = "192.168.0.106"
UDP_PORT = 5005
#CREATE VARIABLES FOR PARAMS
global Fuel_Left, Fuel_Right,Oil_Temp, Oil_Press, Suction, Suction_DIM, DISPLAY_DIM, Status
Fuel_Left = 0
Fuel_Right = 0
Oil_Temp = 0
Oil_Press = 0
Suction = 0
Status = 10
#DIM VARS ARE FROM 0 TO 100
Suction_DIM=50
DISPLAY_DIM=50



#SETUP PYGAME 
pygame.init()
pygame.mouse.set_visible(False)
MainBG = (21,21,21)
Screen = pygame.display.set_mode((800,480), pygame.RESIZABLE)
Screen.fill(MainBG)
Screen.blit(pygame.image.load(r'LoadingScreen.jpg'),(0,0))
pygame.display.update()

# #CREATE SPRITE HOLDERS
FuelSprites=[]
OilTempSprites=[]
OilPressSprites=[]

# #LOAD SPRITES INTO SPRITE HOLDERS - 10 are for power on animation - 265 (1 byte) are for indications
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
# #Oil press indicates 0 when powered off - therefore no powero on animation needed
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

def UDP_COMM_THREAD(UDP_IP,UDP_PORT):
	#OCREATE AND OPEN UDP RECIEVER
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	global Fuel_Left, Fuel_Right,Oil_Temp, Oil_Press, Suction, Suction_DIM, DISPLAY_DIM, Status
	while True:
		data, addr = sock.recvfrom(9) # buffer size is 8 bytes, check DATA FORMAT below
		#DATA FORMAT:
		# BYTE 0-FUEL L, BYTE 1-FUEL R, BYTE 2-OIL TEMP, BYTE 3-OIL PRESS, BYTE 4,5-SUCTION, BYTE 6-DISPLAY_DIM, BYTE 7-SUCTION_DISPLAY_DIM, BYTE 8-SUSPEND RPI	
		Fuel_Left = int(data[0])
		Fuel_Right = int(data[1])
		Oil_Temp = int(data[2])
		Oil_Press = int(data[3])
		Suction = int.from_bytes(bytearray([data[4],data[5]]), byteorder='big', signed=False)
		DISPLAY_DIM = int(data[6])
		Suction_DIM = int(data[7])
		Status = int(data[8])
		
def main():
	#Start recieveing info
	UDP_COMM = threading.Thread(target=UDP_COMM_THREAD, args=(UDP_IP,UDP_PORT))
	UDP_COMM.start()
	clock = pygame.time.Clock()
	PLAY = True

	GAUGES_FRAMES_OFFSET = 0

	global Fuel_Left, Fuel_Right,Oil_Temp, Oil_Press, Suction, Suction_DIM, DISPLAY_DIM, Status
	#OPEN SERIAL CONNECTION TO HMI DISPLAY
	POWERED_ON = True
	ANIM_POWER_ON = 0
	Fuel_L_Indication=0
	Fuel_R_Indication=0
	Oil_T_Indication=0
	Oil_P_Indication=0
	#PLAY LOOP	
	while PLAY:
		#This must be here, oterways pygame freezes
		for event in pygame.event.get():
			pass
		#------------------------------------------
		if Status == 0:
			#SHUT DOWN SYSTEM
			PLAY = False
		elif Status == 1:
			#ELECTRICAL POER FOR GAUGES IS ON
			POWERED_ON = True
		elif Status == 2:
			#ELECTRICAL POER FOR GAUGES IS OFF
			POWERED_ON = False

		if POWERED_ON:
			#Animate gaugle needles powering on
			if ANIM_POWER_ON<10:
				ANIM_POWER_ON+=1
				Fuel_L_Indication += int((Fuel_Left-Fuel_L_Indication)/2)
				Fuel_R_Indication += int((Fuel_Right-Fuel_R_Indication)/2)
				Oil_T_Indication += int((Oil_Temp-Oil_T_Indication)/2)
				Oil_P_Indication += int((Oil_Press-Oil_P_Indication)/2)
			else:
				Fuel_L_Indication=Fuel_Left
				Fuel_R_Indication=Fuel_Right
				Oil_T_Indication=Oil_Temp
				Oil_P_Indication=Oil_Press
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
	
		# #UPDATE SCREEN				
		Screen.fill(MainBG)
		Screen.blit(FuelSprites[ANIM_POWER_ON+Fuel_L_Indication],(174,32))
		Screen.blit(FuelSprites[ANIM_POWER_ON+Fuel_R_Indication],(485,32))
		Screen.blit(OilTempSprites[ANIM_POWER_ON+Oil_T_Indication],(174,280))
		Screen.blit(OilPressSprites[ANIM_POWER_ON+Oil_P_Indication],(485,280))
		pygame.display.update()
		
		
		#Aim at 30 pfs
		clock.tick(33)

if __name__ == '__main__':    
    main()
    pygame.quit()
    quit()