import pygame
import socket
import threading
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


def UDP_COMM_THREAD(UDP_IP,UDP_PORT):
	#OCREATE AND OPEN UDP RECIEVER
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	global Fuel_Left, Fuel_Right,Oil_Temp, Oil_Press, Suction, Suction_DIM, DISPLAY_DIM, Status
	while True:
		data, addr = sock.recvfrom(9) # buffer size is 9 bytes, check DATA FORMAT below
		#DATA FORMAT:
		# BYTE 0-FUEL L, BYTE 1-FUEL R, BYTE 2-OIL TEMP, BYTE 3-OIL PRESS, BYTE 4,5-SUCTION, BYTE 6-DISPLAY_DIM, BYTE 7-SUCTION_DISPLAY_DIM, BYTE 8-SUSPEND RPI	
		Fuel_Left = int(data[0])+1
		Fuel_Right = int(data[1])+1
		Oil_Temp = int(data[2])+1
		Oil_Press = int(data[3])+1
		Suction = int.from_bytes(bytearray([data[4],data[5]]), byteorder='big', signed=False)
		DISPLAY_DIM = int(data[6])
		Suction_DIM = int(data[7])
		Status = int(data[8])
		print(Status)

def main():
	#Start recieveing info
	UDP_COMM = threading.Thread(target=UDP_COMM_THREAD, args=(UDP_IP,UDP_PORT))
	UDP_COMM.start()


if __name__ == '__main__':    
    main()
    quit()