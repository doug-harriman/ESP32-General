import belay

DEVICE = 'rfc2217://192.168.0.19:2217?ign_set_control'

device = belay.Device(DEVICE)

@device.task
def test():
    print("Hello, world!")
    print(dir())

test()