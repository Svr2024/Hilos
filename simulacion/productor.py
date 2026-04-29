import random
import time

class Productor:

    def __init__(self, buffer, semaforos, log_callback, running_flag, ventana):
        self.buffer = buffer
        self.mutex = semaforos["mutex"]
        self.vacios = semaforos["vacios"]
        self.llenos = semaforos["llenos"]
        self.log = log_callback
        self.running = running_flag
        self.ventana = ventana

    def run(self):
        while self.running["state"]:
            dato = f"D{random.randint(1, 99)}"

 
            self.ventana.actualizar_estado_hilos(
                productor_texto="Productor esperando",
                productor_desc="Verificando espacio..."
            )
            self.ventana.update()
            self.vacios.acquire()
            self.mutex.acquire()

            # Escribir en buffer
            self.buffer.producir(dato)
            self.ventana.stats["producidos"] += 1
            self.ventana.actualizar_panel_info()
            self.log("INFO", f"Sensor depositó {dato} en posición {(self.buffer.in_index-1) % self.buffer.tamaño}")
            self.ventana.actualizar_buffer_ui()

            self.mutex.release()
            self.llenos.release()
            
            self.ventana.actualizar_semaforos_ui()

            
            self.ventana.actualizar_estado_hilos(
                productor_texto="Estado: activo",
                productor_desc=f"Último dato: {dato}"
            )

            time.sleep(random.uniform(0.3, 1.0))