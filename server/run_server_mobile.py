import socket
import numpy as np
import time
import shutil

from bbsQt.core.evaluator import HEAAN_Evaluator

# HOST = "172.30.98.224"
HOST = ["192.168.35.75","10.100.82.90"][1]
PORT = 2345

# BYTES_PER_NUM   = 2 
# IMG_WIDTH       = 320 
# IMG_HEIGHT      = 240 
# BUFFER          = 4 
# MAX_AMPLITUDE   = 2500
# SKIP            = int(BUFFER/BYTES_PER_NUM)
# MAX_BYTES       = 5 * BYTES_PER_NUM +  BYTES_PER_NUM*IMG_WIDTH*IMG_HEIGHT + BUFFER

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()



while True:
	print("listening")
	client_socket, addr = server_socket.accept()
	data_received = False

	data = b''
	while len(data) < 5:
		data = client_socket.recv(1024)
		
	if not data:
		print("not data")
		client_socket.close()
		continue
	else:
		print(data.decode())
		data = data.decode()
		data_received = True
		#data =  np.fromstring(data[BUFFER:][::-1], dtype=np.int16)[::-1]
		#print(data.decode("utf8"))
		#print(str(data,'utf8') )


	if data_received:
		######################################################
		## ADD code to generate predict0.dat ... predict4.dat HERE

        henc = HEAAN_Evaluator(server_path, evaluator_ready)
        henc.eval_once(ctxt)

		## Testing delay ###
		shutil.copy(data, "predict0.dat")
		shutil.copy(data, "predict1.dat")
		shutil.copy(data, "predict2.dat")
		for i in range(10):
			print(f"counting {i}")
			time.sleep(1)
		## Testing delay ###
		######################################################
			

		print("calculating pdf done. ")
		bytesToSend = 'Ready to Send Back'.encode()
		# bytesToSend = (1).to_bytes(2, 'little')

		client_socket.sendall(bytesToSend)
	
	client_socket.close()	


	
	
