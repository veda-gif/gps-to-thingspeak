"""starts the main program loop"""
import config
import serial
import requests

API_URL = "https://api.thingspeak.com/channels/{channel}.json?api_key=%s&field1={lat}&field2={lon}"%config.API_KEY
READ_TIMEOUT = 3#seconds

def update_thingspeak(cfg, lat, lon):
    """updates thingspeak channel with lat lon"""
    url = API_URL.replace("{channel}", cfg["channel"]).replace("{lat}", str(lat)).replace("{lon}", str(lon))
    try:
        r = requests.put(url)
        if r.status_code == 200:
            print("updated ThingSpeak")
        elif r.status_code == 404:
            print("unable to update ThingSpeak - please verify channel and/or write key")
        else:
            print(r.content)
    except requests.exceptions.ConnectionError:
        print("unable to contact ThingSpeak - check internet connection")

def configure():
    """loads, configures, save, and return runtime configuration"""
    cfg = config.load_config()
    config.set_port(cfg)
    config.set_baud(cfg)
    config.set_update_rate(cfg)
    config.set_channel(cfg)
    config.set_write_key(cfg)
    config.save_config(cfg)

def run():
    """opens the serial port, reads and parses data, updates ThingSpeak"""
    print("***** RUN *****")
    cfg = config.load_config()
    ser = serial.Serial()
    ser.port = cfg["port"]
    ser.baudrate = cfg["baud"]
    ser.timeout = READ_TIMEOUT
    try:
        print("opening serial port")
        ser.open()
        print("serial port open")
    except:
        print("ERROR: unable to open serial port")
        raise KeyboardInterrupt

    while True:
        try:
            data = ser.readline()
            if data:
                print(data)
            else:
                update_thingspeak(cfg, 0, 0)
                print("input timeout")
        except KeyboardInterrupt:
            if ser.is_open:
                print("\nclosing serial port")
                ser.close()
            #bubble the exception out of the run() function
            raise KeyboardInterrupt

def menu():
    """provides a menu for the user to choose to run, confiure, or quit the application"""
    choice = None
    while not choice:
        print("\n***** MENU *****")
        print("r) RUN")
        print("c) CONFIGURE")
        print("q) QUIT")
        choice = input(">> ").lower()
        if choice == "r":
            return
        elif choice == "c":
            configure()
        elif choice == "q":
            exit()
        else:
            print("invalid option")
            choice = None

def main():
    """application entry point"""
    while True:
        try:
            run()
        except KeyboardInterrupt:
            menu()

main()
