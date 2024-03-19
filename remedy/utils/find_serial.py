import serial.tools.list_ports as list_ports

device_signature = 'f331:0002'

def find_serial_device(device_signature):
    """Return the device path based on vender & product ID.
    
    The device is something like (like COM4, /dev/ttyUSB0 or /dev/cu.usbserial-1430)
    """
    candidates = list(list_ports.grep(device_signature))
    if not candidates:
        raise ValueError(f'No device with signature {device_signature} found')
    if len(candidates) > 1:
        raise ValueError(f'More than one device with signature {device_signature} found')
    return candidates[0].device

if __name__ == '__main__':
    print(find_serial_device(device_signature))