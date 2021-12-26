#!/usr/bin/env python3
import os 
#import sys
import socket
import selectors
import traceback

from . import libclient

sel = selectors.DefaultSelector()


def create_request(action, value):
    if action == "share_key":
        return dict(
            type="key",
            encoding="binary",
            content=dict(action=action, value=value),
        )
    # File sender
    elif action == "transfer":
        return dict(
            type="file",
            encoding='binary',
            content=value  # file name
        )
    else:
        return dict(
            type="binary/custom-client-binary-type",
            encoding="binary",
            content=bytes(action + value, encoding="utf-8"),
        )


def start_connection(host, port, request):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


def run_share_key(q_text, e_key, lock, debug=True):
    #host = '127.0.0.1'
    host = '10.100.82.55'
    port = 2345
    action = "share_key"

    e_key.wait()
    if debug: print("[comm] HEAAN keys are ready")
    fn_dict = q_text.get()
    #key_path = fn_dict['root_path']    

    fn_tar = fn_dict['keys_to_share']
    print("[comm] sending gzipped key file:", fn_tar)
    if os.path.isfile(fn_tar):
        print("[comm] found HEAAN keys:", fn_tar)
        #e_enc.clear()

    # File transfer request 
    
    if debug: print("[comm] sending keys", fn_tar)
    print("fn_dict", fn_dict)
    
    # fn_tar = "./keys2.tar.gz"
    ans = share_key(host, port, action, fn_tar)
    print("run_share_key done")
    #q_text.put(ans)


def share_key(host, port, action, fn_key, debug=True):
    # print("sending file to server.. ")
    # time.sleep(3)

    # ans = {'answer':"good"}
    # print("got a response from server")
    # queue.put(ans)

    # while .... client에서 signal 받으면 끄기
    # print("Sending quit signal.......................")
    # e_quit.set()


    #host, port = sys.argv[1], int(sys.argv[2])
    #action, value = sys.argv[3], sys.argv[4]
    #host = '10.100.82.55'
    request = create_request(action, fn_key)
    start_connection(host, port, request)
    
    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()
        print("connection closed.")

    
    ans = {'answer':"good"}
    print("[comm] got a response from server")
    return ans
    


def query(queue, lock, e_enc, e_quit):
    # print("sending file to server.. ")
    # time.sleep(3)

    # ans = {'answer':"good"}
    # print("got a response from server")
    # queue.put(ans)

    # while .... client에서 signal 받으면 끄기
    # print("Sending quit signal.......................")
    # e_quit.set()


    #host, port = sys.argv[1], int(sys.argv[2])
    #action, value = sys.argv[3], sys.argv[4]
    host = '10.100.82.55'
    port = 2345
    action = "transfer"


    #e_enc.wait()
    print("[comm] Ciphertext ready")
    fn_dict = queue.get()

    fn_enc = fn_dict['fn_enc_skeleton']
    #print("[comm] found a encrypted data file:", fn_enc)
    if os.path.isfile(fn_enc):
        print("communicator found ciphertext file:", fn_enc)
        e_enc.clear()

    # File transfer request 
    request = create_request(action, fn_enc)
    start_connection(host, port, request)

    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()


    ans = {'answer':"good"}
    print("got a response from server")
    queue.put(ans)