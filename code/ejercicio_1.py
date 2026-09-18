import threading
import time

def tarea ():
    for i in range (5):
        print("hello")
        time.sleep(1)


def main():
    thread = threading.Thread(target=tarea)
    thread.start()
    thread.join()
    print("Finalizando el hilo principal")

if __name__ == "__main__":
    main()
