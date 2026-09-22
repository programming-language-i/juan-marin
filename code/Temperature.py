import threading
import time

def sen1():
    for i in range (5):
        print(f"{i+1} 30°C")
        time.sleep(1)

def sen2():
    for i in range (5):
        print(f"{i+1} 40°C")
        time.sleep(1)

def sen3():
    for i in range (5):
        print(f"{i+1} 50°C")
        time.sleep(1)

def sen4():
    for i in range (5):
        print(f"{i+1} 90°C")
        time.sleep(1)



def sensor1():
    thread = threading.Thread(target=sen1)
    print("Sensor 1 empieza a medir la temperatura")
    thread.start()
    thread.join()
    print("Sensor 1 terminado")
    print("    ")
    print("    ")




def sensor2():
    thread = threading.Thread(target=sen2)
    print("Sensor 2 empieza a medir la temperatura")
    thread.start()
    thread.join()
    print("Sensor 2 terminado")
    print("    ")
    print("    ")

def sensor3():
    thread = threading.Thread(target=sen3)
    print("Sensor 3 empieza a medir la temperatura")
    thread.start()
    thread.join()
    print("Sensor 3 terminado")
    print("    ")
    print("    ")

def sensor4():
    thread = threading.Thread(target=sen4)
    print("Sensor 4 empieza a medir la temperatura")
    thread.start()
    thread.join()
    print("Sensor 4 terminado")
    print("    ")
    print("    ")


if __name__ == "__main__":
    sensor1()
    sensor2()
    sensor3()
    sensor4()
