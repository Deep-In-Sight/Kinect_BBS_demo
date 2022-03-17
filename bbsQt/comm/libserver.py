import sys
import selectors
import json
import io
import struct
import tarfile


BLOCKSIZE = 2**16
from bbsQt.constants import TEST_CLIENT
DEBUG=False

def untar(fn_tar):
    if fn_tar.endswith("tar.gz"):
        tar = tarfile.open(fn_tar, "r:gz")
        tar.extractall()
        members = tar.getnames()
        tar.close()
        return members
class Message:
    def __init__(self, selector, sock, addr, q_text, e_enc, e_ans):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.e_enc = e_enc
        self.e_ans = e_ans
        self.q_text = q_text
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(BLOCKSIZE)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            #print("sending a message to client", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding, note
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
            "note":note
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _create_response_json_content(self):
        action = self.request.get("action")
        content = {"result": f'Error: invalid action "{action}".'}
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def _create_response_key(self):
        if TEST_CLIENT:
            #self.e_key.set()  
            self.e_ans.set()

        else:
            self.e_key.set()
            self.e_ans.wait()
        #print("[_create_response_key] e_ans is set")
        content = {"result": "Evaluator is ready"}
        #else:
        #    content = {"result": f'Error: invalid action "{action}".'}
        content_encoding = "utf-8"
        response = {
            "note":"good",
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def _create_response_ctext(self, fn):
        if TEST_CLIENT:
            fn = './pred_0.dat'
        
        #print("_create_response_ctext,  e_ans is set")
        content = fn
        f = open(content, 'rb')
        response = {
            "note":content,
            "content_bytes": f.read(),
            "content_type": "ctxt",
            "content_encoding": "binary",
        }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            #print("[process_events], EVENT_WRITE")
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()
        #print("processed Json Header")

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            #print("[write] self.response_created", self.response_created)
            if not self.response_created:
                self.create_response()

        self._write()

    def close(self):
        print("[libserver] closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                "error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        """2Bytes-long proto header to inform the length of header"""
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return #  ???
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "key":
            self.request = data        
        elif self.jsonheader["content-type"] == "ctxt":
            self.request = data
            if DEBUG: print(self.jsonheader.keys())
            print("received file", self.jsonheader['note'], "from", self.addr)
        else:
            # Binary or unknown content-type
            self.request = data
            print(
                #f'received {self.jsonheader["content-type"]} request from',
                f'received', repr(self.request), 'request from',
                self.addr,
            )
            ## Do the real job here
            # and call create_response() to prepare the response
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        if DEBUG: print("[libserver] in create_response")
        if self.jsonheader["content-type"] == "key":
            # Save received file
            fn_list = self.jsonheader['note']
            print("[libserver] received file", fn_list, "from", self.addr)
            
            # tell server is ready?
            response = self._create_response_key()
        elif self.jsonheader["content-type"] == "ctxt":
            filename =self.jsonheader['note'] 
            with open(filename, "wb") as f:
                f.write(self.request)
            if DEBUG: print("[libserver] saving query ctxt done")
            self.q_text.put(filename)
            self.e_enc.set()
            if TEST_CLIENT:
                self.e_enc.clear()    
                output_file = {"root_path":'./',  # Not using root path
                        "filename":"preds.tar.gz"}
            else:
                # Evaluator.start_evaluate_loop() 기다리기
                self.e_ans.wait()# Wait for evaluator's answer
                output_file = self.q_text.get()
            response = self._create_response_ctext(output_file["filename"])            
        elif "file" in self.jsonheader["content-type"]:
            with open(self.jsonheader['note'], "wb") as f:
                f.write(self.request)
            print("[libserver] writing file done")
            response = self._make_prediction()
        
        message = self._create_message(**response)
        self._send_buffer += message
        self.response_created = True
        self.e_ans.clear()
        

    def _make_prediction(self):

        response = {
            "content_bytes": b"PREDICTION",
            "content_type": "ctxt",
            "content_encoding": "binary",
        }
        return response