import time

class Escenarios:

    def __init__(self, buffer, log, ventana, pausa=3):
        self.buffer = buffer
        self.log = log          
        self.ventana = ventana
        self.pausa = pausa

    def _limpiar_y_resetear(self, nombre_escenario):
        self.ventana.limpiar_consola()
        self.buffer.reset()
        self.ventana.resetear_estadisticas(nombre_escenario)
        self.ventana.actualizar_buffer_ui()
        self.ventana.actualizar_estado_hilos("Productor inactivo", "Consumidor inactivo", "Esperando inicio", "Esperando inicio")

    def _pintar_celda_azul_temporal(self, indice):
        """Pinta una celda de azul y la restaura después de la pausa/2"""
        if 0 <= indice < len(self.ventana.celdas):
            self.ventana.celdas[indice].configure(fg_color="blue")
            self.ventana.update()
            time.sleep(self.pausa / 2)  # Medio tiempo para ver el azul
            # Restaurar según si hay dato o no
            if self.buffer.buffer[indice] is not None:
                self.ventana.celdas[indice].configure(fg_color="green")
            else:
                self.ventana.celdas[indice].configure(fg_color="white")
            self.ventana.update()
            time.sleep(self.pausa / 2)  # Resto de la pausa

    def desbordamiento(self):
        self._limpiar_y_resetear("Desbordamiento")
        
        # Estado inicial del consumidor (más lento, procesa el primer dato)
        self.ventana.actualizar_estado_hilos(
            consumidor_texto="Consumidor ACTIVO (más lento)",
            consumidor_desc="Procesando primer dato D0..."
        )
        
        # Simular que el consumidor está procesando el primer dato lentamente
        primer_dato = "D0"
        self.ventana.stats["consumidos"] += 1
        self.log("INFO", f"Consumidor IA: Comenzó a procesar '{primer_dato}'")
        
        for i in range(12):
            dato = f"D{i}"
            
            if self.buffer.esta_lleno():
                # En lugar de perderlo, SOBRESCRIBE el dato más antiguo (política circular)
                # El dato sobrescrito está en la posición actual de escritura
                pos_sobrescrita = self.buffer.in_index
                dato_antiguo = self.buffer.buffer[pos_sobrescrita]
                
                # Sobrescribir el dato
                self.buffer.producir(dato)
                self.ventana.stats["producidos"] += 1
                self.ventana.stats["perdidos"] += 1  # Se considera pérdida del dato antiguo
                self.ventana.actualizar_panel_info()
                
                self.log("ERROR", f" DESBORDAMIENTO: Buffer LLENO, sobrescribiendo posición {pos_sobrescrita}")
                self.log("ERROR", f"   Dato sobrescrito: '{dato_antiguo}' → REEMPLAZADO por '{dato}'")
                
                # Pintar la celda sobrescrita de ROJO
                self.ventana.celdas[pos_sobrescrita].configure(fg_color="red")
                self.ventana.update()
                time.sleep(self.pausa / 1)
                
                # Actualizar estado del productor
                self.ventana.actualizar_estado_hilos(
                    productor_texto="Productor ACTIVO",
                    productor_desc=f"¡Buffer lleno! Sobrescribió {dato_antiguo} con {dato} en pos {pos_sobrescrita}"
                )
            else:
                # Buffer con espacio libre: escritura normal
                self.buffer.producir(dato)
                self.ventana.stats["producidos"] += 1
                self.ventana.actualizar_panel_info()
                pos = (self.buffer.in_index - 1) % self.buffer.tamaño
                self.log("INFO", f" Sensor depositó {dato} en posición {pos}")
                self.ventana.actualizar_estado_hilos(
                    productor_texto="Productor ACTIVO",
                    productor_desc=f"Depositó {dato} en pos {pos}"
                )
            
            # Actualizar UI y esperar
            self.ventana.actualizar_buffer_ui()
            self.ventana.update()
            time.sleep(self.pausa)
        
        self.ventana.stats["estado_sistema"] = "Completado con SOBRESCRITURAS"
        self.ventana.actualizar_panel_info()

    def vacio(self):
        """Escenario: Buffer inicia con 5 datos, luego se vacían progresivamente"""
        self._limpiar_y_resetear("Buffer Vacío")
        
        # ----- FASE 1: Cargar 5 datos iniciales -----
        for i in range(5):
            dato = f"D{i}"
            self.buffer.producir(dato)
            self.ventana.stats["producidos"] += 1
            pos = (self.buffer.in_index - 1) % self.buffer.tamaño
            self.log("INFO", f"Sensor depositó {dato} en posición {pos}")
            self.ventana.actualizar_estado_hilos(
                productor_texto="Productor activo",
                productor_desc=f"Depositó {dato} en pos {pos}"
            )
            self.ventana.actualizar_buffer_ui()  # verdes
            self.ventana.update()
            time.sleep(self.pausa)
        
        
        # ----- FASE 2: Consumir hasta vaciar -----
        consumos_exitosos = 0
        while not self.buffer.esta_vacio():
            pos_lectura = self.buffer.out_index
            dato_actual = self.buffer.buffer[pos_lectura]
            
            # Marcar celda como AZUL mientras se lee
            self.ventana.celdas[pos_lectura].configure(fg_color="blue")
            self.ventana.update()
            time.sleep(self.pausa / 2)
            
            # Consumir efectivamente
            dato = self.buffer.consumir()
            self.ventana.stats["consumidos"] += 1
            consumos_exitosos += 1
            
            self.log("INFO", f"IA consumió {dato} desde posición {pos_lectura}")
            self.ventana.actualizar_estado_hilos(
                consumidor_texto="Consumidor activo",
                consumidor_desc=f"Consumió {dato} de pos {pos_lectura}"
            )
            
            # La celda ahora queda vacía (blanco)
            self.ventana.actualizar_buffer_ui()  # pinta blancos donde no hay datos
            self.ventana.update()
            
            time.sleep(self.pausa)
        
       # ----- FASE 3: Intentos de consumo en vacío (ERROR: multas falsas) -----
        
        # Simular 3 lecturas erróneas (como si la IA siguiera accediendo al buffer vacío)
        for i in range(3):
            pos_lectura = self.buffer.out_index
            self.log("INFO", f"Intento {i+1}: IA accediendo posición {pos_lectura}")
            
            # Intentar leer aunque esté vacío (simulación de fallo)
            try:
                # En un buffer real sin control, leería basura o datos repetidos
                dato_erroneo = self.buffer.buffer[pos_lectura]
                if dato_erroneo is None:
                    # ERROR CRÍTICO: leyó una celda vacía
                    self.log("ERROR", f"IA procesó registro VACÍO en posición {pos_lectura}")
                    self.ventana.stats["perdidos"] += 1  # Contar como error
                    
                    # Marcar visualmente el error (rojo temporal)
                    self.ventana.celdas[pos_lectura].configure(fg_color="red")
                    self.ventana.update()
                    time.sleep(self.pausa / 2)
                    self.ventana.celdas[pos_lectura].configure(fg_color="white")
                    
                else:
                    # Si por algún motivo hay dato, es válido
                    self.log("INFO", f"IA consumió {dato_erroneo} (válido inesperado)")
                    self.ventana.stats["consumidos"] += 1
            except Exception as e:
                self.log("ERROR", f"ERROR CRÍTICO: IA leyendo fuera de bounds - Multa falsa generada")
            
            # Estado del consumidor: sigue activo (NO bloqueado porque no hay semáforos)
            self.ventana.actualizar_estado_hilos(
                consumidor_texto="Consumidor ACTIVO (sin bloqueo)",
                consumidor_desc=f"ERROR: Leyó celda vacía - Multa falsa #{i+1}"
            )
            
            self.ventana.actualizar_panel_info()
            self.ventana.update()
            time.sleep(self.pausa)
            self.ventana.stats["estado_sistema"] = "Completado con ERRORES"

    def carrera(self):
        self._limpiar_y_resetear("Condición de Carrera")

        # 1. Cargar un registro inicial en el buffer
        registro_inicial = "ABC | 85km/h"
        self.buffer.buffer[0] = registro_inicial
        self.ventana.actualizar_buffer_ui()
        self.log("INFO", f"celda 0 contiene inicialmente: '{registro_inicial}'")
        time.sleep(self.pausa)

        # 2. IA comienza a leer (pintar azul)
        self.log("INFO", "IA comienza a leer la celda 0...")
        self.ventana.celdas[0].configure(fg_color="blue")
        self.ventana.actualizar_estado_hilos(
            consumidor_texto="IA leyendo",
            consumidor_desc="Lectura parcial del registro..."
        )
        self.ventana.update()
        time.sleep(self.pausa)

        # IA lee parcialmente el dato
        lectura_parcial = registro_inicial[:5]
        self.log("INFO", f"IA lectura parcial: '{lectura_parcial}...'")

        # 3. Sensor interrumpe y escribe un nuevo registro (pintar verde)
        nuevo_registro = "ZXY | 120km/h"
        self.log("INFO", "Sensor interrumpe y comienza a escribir un nuevo registro...")

        # Escribir en buffer
        self.buffer.buffer[0] = nuevo_registro
        self.ventana.actualizar_buffer_ui()

        # Pintar verde para indicar escritura
        self.ventana.celdas[0].configure(fg_color="green")
        self.ventana.actualizar_estado_hilos(
            productor_texto="Sensor activo",
            productor_desc="Deposita nuevo registro mientras IA lee"
        )
        self.ventana.update()
        time.sleep(self.pausa)

        self.log("INFO", f"Sensor deposito: '{nuevo_registro}'")

        # 4. IA termina de leer → dato corrupto
        self.log("WARN", "IA termina de leer, pero el sensor cambió el dato durante la lectura")

        lectura_final = lectura_parcial + nuevo_registro[5:]
        self.log("ERROR", f"DATO CORRUPTO LEÍDO POR IA: '{lectura_final}'")

        # 5. Pintar celda en rojo (NO actualizar UI después)
        self.ventana.celdas[0].configure(fg_color="red")
        self.ventana.actualizar_estado_hilos(
            consumidor_texto="IA ERROR",
            consumidor_desc=f"Leyó registro {lectura_final} (multa falsa generada)"
        )
        self.ventana.update()
        time.sleep(self.pausa)

        # 6. Actualizar estadísticas
        self.ventana.stats["producidos"] += 1
        self.ventana.stats["perdidos"] += 1
        self.ventana.stats["consumidos"] += 1
        self.ventana.stats["estado_sistema"] = "Completado con CORRUPCIÓN"
        self.ventana.actualizar_panel_info()
