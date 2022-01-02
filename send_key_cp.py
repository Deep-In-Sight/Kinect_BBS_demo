import sys
import shutil
from bbsQt.constants import FN_KEYS, DIR_KEY_SERVER

if __name__ == "__main__":
    key_path = sys.argv[1]
    for fn in FN_KEYS:
        shutil.copy(key_path + fn, DIR_KEY_SERVER)

