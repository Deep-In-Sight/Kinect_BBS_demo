import os 

def fn_pred(i):
    dir = "./"
    return dir+f"pred_{i}.dat"

def request_summary(request):
    #print("request", request)
    print("\n[Comm] Method: ", request.method)
    print("[Comm] Headers: ", request.headers)
    print("[Comm] Args: ", request.args)
    print("[Comm] Form data: ", request.form)
    print("[Comm] FILE: ", request.files)

def ready_for_connection_test(fn_in):
    with open(fn_in, "a") as fout:
        fout.write(">>>> Connection GOOD\n")

def check_for_keys():
    for fn in ["EncKey.txt", "MulKey.txt", "RotKey_1.txt"]:
        if not os.path.exists(fn):
            return False
    return True

def predictions_ready():
    """Check if all predictions are ready.
    """
    for i in range(5):
        if not os.path.exists(fn_pred(i)):
            return False
    return True
