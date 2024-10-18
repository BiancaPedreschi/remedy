from remedy.utils.common_functions import check_os
if check_os() in ['Linux']:
    import ctypes
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    xlib.XInitThreads()

import parallel
import time

from remedy.utils.common_functions import send_trigger_thread


def main():
    # Inizializzazione della porta parallela
    p = parallel.Parallel()

    # Definizione dei codici trigger
    RS_TRIG = 32 # Start/end of resting state
    
    # Send trigger start
    send_trigger_thread(p, RS_TRIG)
    
    time.sleep(5 * 60)
    
    # Send trigger end
    send_trigger_thread(p, RS_TRIG)
    
    return


if __name__ == "__main__":
    main()