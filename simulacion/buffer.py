class BufferCircular:

    def __init__(self, tamaño=10):
        self.tamaño = tamaño
        self.buffer = [None] * tamaño
        self.in_index = 0
        self.out_index = 0
        self.count = 0          # elementos actuales en el buffer

    def producir(self, dato):
        """Escribe sin control (sobrescribe si está lleno). Útil solo para escenarios con semáforos."""
        self.buffer[self.in_index] = dato
        self.in_index = (self.in_index + 1) % self.tamaño
        if self.count < self.tamaño:
            self.count += 1

    def consumir(self):
        """Lee sin control (asume que hay datos)."""
        dato = self.buffer[self.out_index]
        self.buffer[self.out_index] = None
        self.out_index = (self.out_index + 1) % self.tamaño
        if self.count > 0:
            self.count -= 1
        return dato

    def producir_si_hay_espacio(self, dato):
        """Retorna True si se pudo escribir, False si buffer lleno (pérdida)."""
        if self.count < self.tamaño:
            self.producir(dato)
            return True
        return False

    def consumir_si_hay_dato(self):
        """Retorna (dato, True) si había datos, (None, False) si vacío."""
        if self.count > 0:
            return self.consumir(), True
        return None, False

    def esta_lleno(self):
        return self.count == self.tamaño

    def esta_vacio(self):
        return self.count == 0

    def reset(self):
        """Limpia el buffer y reinicia índices."""
        self.buffer = [None] * self.tamaño
        self.in_index = 0
        self.out_index = 0
        self.count = 0

    def estado(self):
        return self.buffer.copy()