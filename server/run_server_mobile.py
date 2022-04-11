import socket
import argparse
from bbsQt.comm.utils import extract_ip
import fase

# HOST = "172.30.98.224"
#HOST = ["192.168.35.75","10.100.82.89", "61.74.232.166"][2]

def main():
    HOST = extract_ip()
    #HOST = '127.0.0.1'
    print("[SERVER] This server's IP:", HOST)

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
    server_path = "./"


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
            fn_data = data.decode()
            data_received = True
            #data =  np.fromstring(data[BUFFER:][::-1], dtype=np.int16)[::-1]
            print("file name", fn_data)

        if data_received:
            ######################################################
            ## ADD code to generate predict0.dat ... predict4.dat HERE

            henc = HEAAN_Evaluator(server_path)
            _, action, _ = fn_data.split("_")
            action = int(action.replace("Cat",""))
            
            henc.eval_once("/home/etri_ai1/work/Kinect_BBS_demo/server/"+fn_data, action)

            print("evaluation done. ")
            bytesToSend = 'Ready to Send Back'.encode()
            # bytesToSend = (1).to_bytes(2, 'little')

            client_socket.sendall(bytesToSend)

        client_socket.close()	



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--fpga", dest='use_fpga', action='store_true')
    parser.add_argument("--cuda", dest='use_cuda', action='store_true')
    args = parser.parse_args()

    if args.use_fpga:
        fase.USE_FPGA = True
    elif args.use_cuda:
        fase.USE_CUDA = True

    # import HEAAN_Evaluator *after* setting which HEAAN variants to use
    from bbsQt.core.evaluator import HEAAN_Evaluator

    main()

        
        
