#!/usr/bin/env python3
import os 
#import subprocess
#import sys
import socket
import selectors
import traceback

from . import libclient
from bbsQt.constants import COPY_SCRIPT, HOST, PORT, BIN_PYTHON
#from bbsQt.constants import DIR_KEY_SERVER, S_ACCOUNT, S_PASSWORD, SCP_PORT

# only one selector throughout the application.
sel = selectors.DefaultSelector()

# content = self.request["content"]
# content_type = self.request["type"]
# content_encoding = self.request["encoding"]

def create_request(action, value):
    """ Should be matched with Message.queue_request()
    queue_request() separates requests by their 'type', not 'action'. 
    """
    if action == "share_key":
        return dict(
            type="key",
            encoding="binary",
            content=value,
            action=action,
        )
    # File sender
    # elif action == "transfer":
    #     return dict(
    #         type="file",
    #         encoding='binary',
    #         content=value  # file name
    #     )
    elif action == "query":
        return dict(
            type="ctxt",
            encoding='binary',
            content=value  # file name
        )
    # else:
    #     return dict(
    #         type="binary/custom-client-binary-type",
    #         encoding="binary",
    #         content=bytes(action + value, encoding="utf-8"),
    #     )


def start_connection(host, port, request):
    addr = (host, port)
    print("[comm] starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    sock.connect_ex(addr)
    
    print("socket connecting???")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    #################################################
    print(sel, sock, events, message) #############
    sel.register(sock, events, data=message)


def query(fn_dict):
    action = "query"

    print("[comm] Ciphertext ready")
    #fn_dict = queue.get()

    fn_enc = fn_dict['fn_enc_skeleton']
    #print("[comm] found a encrypted data file:", fn_enc)
    if os.path.isfile(fn_enc):
        print("[comm] communicator found ciphertext file:", fn_enc)
        #e_enc.clear()

    # File transfer request 
    request = create_request(action, fn_enc)
    print("[comm] request", request)
    start_connection(HOST, PORT, request)

    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    answer_list = message.process_events(mask)
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
        #sel.close() 
        pass


    ans = {'filename':answer_list}
    print("[comm] got a response from server")
    return ans
