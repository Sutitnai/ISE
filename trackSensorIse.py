import serial  as sr
from matplotlib import pyplot as plt
import timeit  as tmi
from time import sleep

def trackSerial(com_port: str, mesuring_time: int) -> dict[str, list[float]]:
    mesurements = {"time": [], "mesurements": []}
    print("trying to connect to serial Port..")
    try:
        serial_port = sr.Serial(port=com_port, baudrate=9600)
        print("connected!")
    except sr.serialutil.SerialException:
        print("connection fialed")
    print(serial_port)
    sleep(1)
    print("mesuring")
    start_time = tmi.default_timer()
    while(tmi.default_timer() - start_time) < mesuring_time:
        remTime = round((mesuring_time -(tmi.default_timer() - start_time)) / 1, 2) #calculates the remaining time for the mesurement
        print("\r>> Time remaining: {} s.".format(remTime), end='')
        if serial_port.in_waiting > 1:
            serial_input = serial_port.readline()
            try:
                serial_str = serial_input.decode("Ascii")
                mesurement_bit = float(serial_str)
                mesurement = mesurement_bit #* (5.0 / 1023.0)
            except UnicodeDecodeError:
                mesurement = 0.0
            mesurements["mesurements"].append(mesurement)
            mesurements["time"].append(tmi.default_timer() - start_time)
    return mesurements        


def plot_data(mesurements: dict[str, list[float]]):
    plt.plot(mesurements["time"], mesurements["mesurements"])
    plt.xlabel("Runntime in secconds")
    plt.ylabel("Sensor readings in V")
    plt.show()



if __name__ == "__main__":
    print("Welcome")
    comPort = input("Enter the com port: ")
    print("you've selected: " + comPort)
    mesuringTime = input("Enter the time you want to measure in s: ")
    print("your measuring time is: " + mesuringTime)
    i = 0
    plot_data(trackSerial(com_port=comPort, mesuring_time=int(mesuringTime)))