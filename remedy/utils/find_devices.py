import sounddevice as sd


def find_device():
    for dev in sd.query_devices():
        if dev['name'] == 'USB Audio Device: - (hw:1,0)':
            dev_speaker = dev['index']
        elif dev['name'] == 'HDA Intel PCH: ALC222 Analog (hw:3,0)':
            dev_headphones = dev['index']
    return dev_headphones, dev_speaker
    
    
if __name__ == '__main__':
    print(find_device())