import random
import time

class Consumidor:

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

    
            self.ventana.actualizar_estado_hilos(
                consumidor_texto="Consumidor esperando",
                consumidor_desc="Esperando datos..."
            )
            self.ventana.update()
            self.llenos.acquire()
            self.mutex.acquire()

            indice = (self.buffer.out_index) % self.buffer.tamaño
            self.ventana.pintar_lectura(indice)

            dato = self.buffer.consumir()
            self.ventana.stats["consumidos"] += 1
            self.ventana.actualizar_panel_info()
            self.log("INFO", f"IA consumió {dato} desde posición {(self.buffer.out_index-1) % self.buffer.tamaño}")
            self.ventana.actualizar_buffer_ui()
            
            self.mutex.release()
            self.vacios.release()
            self.ventana.actualizar_semaforos_ui()
  
            self.ventana.actualizar_estado_hilos(
                consumidor_texto="Estado: activo",
                consumidor_desc=f"Último procesado: {dato}"
            )

            time.sleep(random.uniform(0.5, 1.2))