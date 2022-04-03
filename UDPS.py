import socket
import struct

UDP_IP = "192.168.0.106"
UDP_PORT = 5005

Fuel_Left = 200
Fuel_Right = 200
Oil_Temp = 25
Oil_Press = 24
Suction = 300
#DIM VARS ARE FROM 0 TO 100
DISPLAY_DIM = 5
Suction_DIM = 0

MESSAGE = struct.pack("B",Fuel_Left)
MESSAGE += struct.pack("B",Fuel_Right)
MESSAGE += struct.pack("B",Oil_Temp)
MESSAGE += struct.pack("B",Oil_Press)
MESSAGE += struct.pack(">H",Suction)
MESSAGE += struct.pack("B", DISPLAY_DIM)
MESSAGE += struct.pack("B", Suction_DIM)
MESSAGE += struct.pack("B", 2)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))