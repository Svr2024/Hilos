class BufferCircular:

    def __init__(self, tamaño=10):
        self.tamaño = tamaño
        self.buffer = [None] * tamaño
        self.in_index = 0
        self.out_index = 0

    def producir(self, dato):
        self.buffer[self.in_index] = dato
        self.in_index = (self.in_index + 1) % self.tamaño

    def consumir(self):
        dato = self.buffer[self.out_index]
        self.buffer[self.out_index] = None
        self.out_index = (self.out_index + 1) % self.tamaño
        return dato

    def estado(self):
        return self.buffer