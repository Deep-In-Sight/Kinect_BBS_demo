import socket
import selectors
import traceback
from . import libserver
from bbsQt.constants import PORT

sel = selectors.DefaultSelector()

def accept_wrapper(sock, q_text, e_enc, e_ans):
    conn, addr = sock.accept()  # Should be ready to read
    print("[server comm] accepted connection from", addr)
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr, q_text, e_enc, e_ans)
    sel.register(conn, selectors.EVENT_READ, data=message)


def run_server(q_text, evaluator_ready, e_enc, e_ans, HOST):
    """
    The resultant prediction file name is assumed.
    """
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print("[SERVER] listening on", (HOST, PORT), '\n')
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    # wait for the model 
    evaluator_ready.wait()
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                ### No need to care about keys
                if key.data is None:
                    # read and register incoming message
                    accept_wrapper(key.fileobj, q_text, e_enc, e_ans) 
                else:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )
                        message.close()
                        print("[server comm] message closed")
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()
    
    e_ans.clear() # answer is passed. 
