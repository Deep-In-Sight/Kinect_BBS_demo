import os
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

    #server_path = "./"

    server_path = os.getcwd()+'/' # = "./"랑 사실상 같음.
    # 1.
    # run_server.py 버전과 동일함. 
    # 둘 다 Kinect_BBS_demo/server/ 에서 실행한다고 가정할 때 같은 값, "Kinect_BBS_demo/server/"을 가짐
    
    incoming_dir = server_path
    # 2.
    # 핸드폰에서 설정한 server path와 비교 필요.
    # 핸드폰에서 "/home/etri_ai1/work/Kinect_BBS_demo/" 까지 써야하는지
    # "/home/etri_ai1/work/Kinect_BBS_demo/server/까지 써야하는지 확인 필요" <- 이게 맞는 듯 합니다. 
    #
    #
    # server_path/serkey/[EncKey, MulKey, RotKey_1,...].dat # 파일 이름 다를 수도 있음
    
    # 3.
    # fn_data: 모바일에서 전송받은 ctxt 파일 예) Kinect_BBS_demo/server/ctxt_01_e_.dat 

    # 4.    
    # server_path/predict1~5.dat # 서버에서 모바일로 보낼 계산 결과 파일 
    # 데스크탑 버전은 pred1.dat 이며, 서로 덮어쓰지 않도록 mobile은 predict1.dat로 바꾼 것으로 기억함.

    # 5.
    # server_path/models/Nmodel_??_??.pickle # 훈련된 모델 파일. 제 자리에 있을 것으로 예상


    print("SERVER SETUP")
    print("*************************************************************")
    print("incoming_dir:", incoming_dir)
    print("Keys will go to :", server_path+"serkey/")

    henc = None
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
            print("모바일이 보낸 파일 이름", fn_data)
            print("서버가 기대하는 ctxt 파일 위치:", incoming_dir+fn_data)

        if data_received:
            ######################################################
            ## ADD code to generate predict0.dat ... predict4.dat HERE
            if henc == None:
                henc = HEAAN_Evaluator(server_path)

            _, action, _ = fn_data.split("_")
            action = int(action.replace("Cat",""))
            
            henc.eval_once(incoming_dir+fn_data, action)

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

        
        
