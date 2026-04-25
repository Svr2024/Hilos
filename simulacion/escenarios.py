class Escenarios:

    def __init__(self, buffer, log):
        self.buffer = buffer
        self.log = log

    def desbordamiento(self):
        self.log("Desbordamiento")

        for i in range(12):
            self.buffer.producir(f"D{i}")
            self.log(f"Intento producir D{i}")

        self.log(str(self.buffer.estado()))

    def vacio(self):
        self.log("Vacío")

        for i in range(5):
            dato = self.buffer.consumir()
            self.log(f"Consumido: {dato}")

    def carrera(self):
        self.log("Condición de carrera simulada")

        self.buffer.buffer[0] = "X"
        self.buffer.buffer[0] = "Y"

        self.log(str(self.buffer.estado()))