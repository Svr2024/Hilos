import random
import time

class Productor:

    def __init__(self, buffer, semaforos, log_callback, running_flag):
        self.buffer = buffer
        self.mutex = semaforos["mutex"]
        self.vacios = semaforos["vacios"]
        self.llenos = semaforos["llenos"]
        self.log = log_callback
        self.running = running_flag

    def run(self):
        while self.running["state"]:

            dato = f"D{random.randint(1, 99)}"

            self.vacios.acquire()
            self.mutex.acquire()

            self.buffer.producir(dato)
            self.log(f"🟢 Sensor produjo: {dato}")

            self.mutex.release()
            self.llenos.release()

            time.sleep(random.uniform(0.3, 1.0))