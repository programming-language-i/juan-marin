import threading, time


def print_numbers():

    for i in range(1,6):
        print(f"Número: {i}")
        time.sleep(1)


def print_letters():

    for letter in "ABCDE":
        print(f"Letra: {letter}")
        time.sleep(1)


if __name__ == "__main__":
    thread1 = threading.Thread(target=print_numbers)
    thread2 = threading.Thread(target=print_letters)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()