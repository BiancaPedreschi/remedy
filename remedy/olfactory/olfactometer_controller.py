import time
import os
import os.path as op
import threading
import serial
import pandas as pd

listening = True
transfer = None
output_file = output_file_path = ()
port = "/dev/cu.usbmodem20220051"

class olfactometer():

    def __init__(self, output_file, echoing=False):#al posto di fn inserisci output_file
        self.ser = None
        self.port = "0"
        self.baudrate = None
        self.bytesize = None
        self.parity = None
        self.stopbits = None
        self.dsrdtr = None
        self.rtscts = None
        self.output_file = output_file

    def set_serial(
        self,
        port,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        dsrdtr=False,
        rtscts=False,
    ):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.dsrdtr = dsrdtr
        self.rtscts = rtscts

    def open(self, timeout=None):
        try:
            self.timeout = timeout
            if not self.ser:
                self.ser = serial.Serial(
                    self.port,
                    baudrate=self.baudrate,
                    bytesize=self.bytesize,
                    stopbits=self.stopbits,
                    parity=self.parity,
                    dsrdtr=self.dsrdtr,
                    rtscts=self.rtscts,
                    timeout=self.timeout,
                )

                if self.ser.isOpen():
                    print("Opened Serial Port")
            else:
                pass
                # TODO: implement
        except serial.SerialException as se:
            print("Monitor: Disconnected (Serial exception)")
            raise se
        except IOError:
            print("Monitor: Disconnected (I/O Error)")
        except KeyboardInterrupt:
            print("Monitor: Keyboard Interrupt. Exiting Now...")
        except ValueError as ve:
            raise ve

    def readline(self):
        return self.ser.readline().decode("ascii", "ignore")

    def _reader(self):
        try:
            while self.read:
                data = self.ser.readline()
                try:
                    msg = str(data, "utf-8").strip()
                    print(msg)
                    self.data_writer(msg)#dato che line corrisponde a data_writer self.data_writer(msg)
                except Exception as en:
                    print(f'Unable to write on output file')
                    pass

        except Exception as e:
            print(e)
            print("Lost connection!")

        return

    def run(self):
        self.read = True
        self.thw = threading.Thread(None, target=self._reader)
        self.thw.start()

    def stop(self):
        self.read = False
        self.thw.join()

    def write(self, data):
        data = data + '\r'
        if not self.ser:
            return 0

        try:
            if isinstance(data, str):
                data = bytes(data, "utf-8")
            self.ser.write(data)
            return 1
        except Exception as e:
            print(e)
            return 0

    def data_writer(self, msg):  # spostare dentro classe
        with open(self.output_file, 'a') as f:
            f.write(msg + '\n')

        return

    def isOpen(self):
        if not self.ser:
            return False
        else:
            return self.ser.isOpen()

    def _close(self):
        return self.ser.close()

    def close(self):
        if self.ser and self.ser.isOpen() == True:
            self._close()
            self.ser = None
            return True
        else:
            return True



monitor = olfactometer(output_file=output_file_path)
