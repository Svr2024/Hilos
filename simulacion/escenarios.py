import time

class Escenarios:

    def __init__(self, buffer, log, ventana, pausa=0.8):
        self.buffer = buffer
        self.log = log
        self.ventana = ventana
        self.pausa = pausa

    def _limpiar_y_resetear(self):
        self.ventana.limpiar_consola()
        self.buffer.reset()
        self.ventana.actualizar_buffer_ui()

    def desbordamiento(self):
        self._limpiar_y_resetear()

        for i in range(12):
            dato = f"D{i}"
            exito = self.buffer.producir_si_hay_espacio(dato)
            if exito:
                self.log(f" INFO: {dato} almacenado. Buffer ahora tiene {self.buffer.count}/{self.buffer.tamaño} elementos.")
            else:
                self.log(f" WARN: ¡Buffer LLENO! {dato} PERDIDO.")
            self.ventana.actualizar_buffer_ui()
            self.ventana.update()
            time.sleep(self.pausa)

    def vacio(self):
        self._limpiar_y_resetear()

        for i in range(5):
            dato, exito = self.buffer.consumir_si_hay_dato()
            if exito:
                self.log(f" INFO: Consumido: {dato}")
            else:
                self.log(f" WARN: Buffer vacío, no se puede consumir.")
            self.ventana.actualizar_buffer_ui()
            self.ventana.update()
            time.sleep(self.pausa)

    def carrera(self):
        self._limpiar_y_resetear()
        self.log("=== ESCENARIO: CONDICIÓN DE CARRERA (simulación) ===")
        self.log("Simulamos dos productores escribiendo en la misma celda sin sincronización.\n")
        
        self.log("Paso 1: Escribimos 'X' en posición 0")
        self.buffer.buffer[0] = "X"
        self.ventana.actualizar_buffer_ui()
        self.ventana.update()
        time.sleep(self.pausa)
        
        self.log("Paso 2: Escribimos 'Y' en la misma posición 0")
        self.buffer.buffer[0] = "Y"
        self.ventana.actualizar_buffer_ui()
        self.ventana.update()
        time.sleep(self.pausa)
        
        self.log("\nResultado final: el buffer[0] contiene 'Y'. El dato 'X' se perdió (sobrescritura).")