import os
import requests
from urllib.parse import unquote
from time import sleep


class ClientCommunicator:
    """HTTP(S) client for communicating with the server.

    Args:
        server_ip (str): IP address of the server.
        cert (str): Path to the certificate file.

    Methods:
        send_ctxt: Send a ciphertext to the server.
        send_keys: Send keys to the server.
        query_ready: Ask the server if predictions are ready.
        get_result: Get the prediction results from the server.
        
    """
    def __init__(self, server_ip, cert=None):
        self._server_ip = server_ip
        self._cert = cert
        self._predict_ready = False

        print("Paired with server at", self._server_ip)

    def query_ready(self, 
                    retry_interval=30,
                    max_trials = 10,
                    path = "/ready"):
        """Ask the server if predictions are ready.
        """
        url = self._server_ip + path
        print("URL", url )
        ret_ready = requests.get(url, verify=self._cert)

        n_trials = 0
        while ret_ready.ok and ret_ready.text != "ready":
            print("[Comm] Predictions are not ready yet")
            print("[Comm] Retrying in", retry_interval, "seconds...")
            sleep(retry_interval)
            ret_ready = requests.get(url, verify=self._cert)
            n_trials += 1

            if n_trials > max_trials:
                print("[Comm] Maximum polling trials reached. Quitting...")
                self._predict_ready = False
                return False
        
        # TODO: catch exception when ret_read.ok is False
        
        self._predict_ready = True
        return True

    def get_5results(self, save_dir="./", path="/result"):
        """Get the prediction results from the server.

        Predictions are saved in five files on the server.
        Iterate over the files and download them one by one.
        Predictions' ready status must have been checked by query_ready() in advance.
        """
        assert self._predict_ready, "Predictions are not ready yet"

        recieved_files = []
        for cnt in range(5):
            fn = f'{save_dir}/pred{cnt}.dat'
            if cnt == 0 :
                n_try_max = 10
                tsleep = 10
            else:
                n_try_max = 5
                tsleep = 2
        
            n_try = 0
            while n_try < n_try_max:
                r = requests.get(self._server_ip + path, 
                                stream=True, 
                                headers={"cnt":f"{cnt}"},
                                verify=self._cert)
                if r.ok:
                    self.save_binary(r, fn)
                    recieved_files.append(fn)
                    print(f"Result recieved: {len(recieved_files)}/5")
                    break
                else:
                    sleep(tsleep)
                    n_try+=1
            else:
                print("Retry limit reached. Try again later")
                return False

        return recieved_files

    def send_ctxt(self, fn, action, path="/upload"):
        print(f"Uploading {fn} to the server")
        print("action", action)
        ret = requests.post(self._server_ip + path, 
                    files={"file": open(fn, "rb")},
                    headers={"dtype":"ctxt", "action":str(action)},
                    verify=self._cert)
        
        if not ret.ok:
            # HTTP error handling
            print("Error in uploading the file to the server.")
            print(ret.status_code)
            print(ret)
            return False
        
        return True

    def send_keys(self, key_path, path="/keys"):
        """Send keys to the server"""
        # 미리 정해져있음 
        flists = [("enc_key", 'EncKey.txt'), 
                ('mul_key', 'MulKey.txt'),
                ('rot_key', 'RotKey_1.txt')]
        for dtype, fn in flists:
            r = requests.post(url = self._server_ip + path, 
                            files={'file':open(os.path.join(key_path, fn), 'rb')}, 
                            headers={'dtype':dtype},
                            verify=self._cert)
            if not r.ok:
                print("ERROR")
                return False
            
        return True

    def check_connection(self):
        """Check if the server is up and running."""
        fn = "test.txt"
        # 연결 테스트용
        with open(fn, "w") as f:
            f.write("Connecting from: " + self._server_ip + "\n")

        try:
            r = requests.post(self._server_ip+'/upload', 
                        files={'file':open(fn, 'rb')}, 
                        headers={'dtype':"test"},
                        verify=self._cert)
        except (requests.exceptions.ConnectionError, 
                requests.exceptions.InvalidURL, 
                requests.exceptions.Timeout) as e:
            print(e)
            print("Connection Error")
            
        except requests.exceptions.HTTPError:
            print("Connection Established")    

        ret = requests.get(self._server_ip+'/result',
                            files={"file": open(fn, "rb")},
                            headers={"dtype":"test"},
                            verify=self._cert)
        print(ret.text)

    @staticmethod
    def get_filename(response):
        if 'Content-Disposition' in response.headers:
            content_disposition = response.headers['Content-Disposition']
            parts = content_disposition.split(';')

            for part in parts:
                if 'filename' in part:
                    filename = part.split('=')[1]
                    filename = unquote(filename.strip(' "'))  # remove quotes and spaces
                    
        return filename

    @staticmethod
    def save_binary(r, fn_save):
        if r.ok:
            with open(fn_save, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            raise FileNotFoundError
        


