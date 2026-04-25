import random
import time

class Consumidor:

    def __init__(self, buffer, semaforos, log_callback, running_flag):
        self.buffer = buffer
        self.mutex = semaforos["mutex"]
        self.vacios = semaforos["vacios"]
        self.llenos = semaforos["llenos"]
        self.log = log_callback
        self.running = running_flag

    def run(self):
        while self.running["state"]:

            self.llenos.acquire()
            self.mutex.acquire()

            dato = self.buffer.consumir()
            self.log(f" IA consumió: {dato}")

            self.mutex.release()
            self.vacios.release()

            time.sleep(random.uniform(0.5, 1.2))