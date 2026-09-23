import multiprocessing, time


def print_numbers():

    for i in range(1,6):
        print(f"Número: {i}")
        time.sleep(1)


def print_letters():

    for letter in "ABCDE":
        print(f"Letra: {letter}")
        time.sleep(1)


if __name__ == "__main__":
    process1 = multiprocessing.Process(target=print_numbers)
    process2 = multiprocessing.Process(target=print_letters)

    process1.start()
    process2.start()

    process1.join()
    process2.join()