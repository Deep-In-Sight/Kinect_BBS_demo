import sys
import socket
import selectors
import traceback

from . import libserver

sel = selectors.DefaultSelector()


def accept_wrapper(sock, e_key, e_enc, e_ans):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr, e_key, e_enc, e_ans)
    sel.register(conn, selectors.EVENT_READ, data=message)


#if len(sys.argv) != 3:
#    print("usage:", sys.argv[0], "<host> <port>")
#    sys.exit(1)

#host, port = sys.argv[1], int(sys.argv[2])

def run_server(e_key, e_enc, e_ans, lock):
    host = "10.100.82.55"
    port = 2345

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((host, port))
    lsock.listen()
    print("listening on", (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    # read and register incoming message
                    accept_wrapper(key.fileobj, e_key, e_enc, e_ans) 
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
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()
    
    e_ans.clear() # answer is passed. 
