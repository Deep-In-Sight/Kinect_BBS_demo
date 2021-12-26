import os
import time

def run(queue, lock, e_enc, e_quit):
    e_enc.wait()
    fn_dict = queue.get()
    fn_enc = fn_dict['fn_enc_skeleton']
    #print("[comm] found a encrypted data file:", fn_enc)
    if os.path.isfile(fn_enc):
        print("communicator found ciphertext file:", fn_enc)
        e_enc.clear()

    print("sending file to server.. ")
    time.sleep(3)

    ans = {'answer':"good"}
    print("got a response from server")
    queue.put(ans)

    # while .... client에서 signal 받으면 끄기
    time.sleep(10)
    print("Sending quit signal.......................")
    e_quit.set()


