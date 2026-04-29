import customtkinter as ctk
from PIL import Image
import threading
import psutil
import time

from simulacion.buffer import BufferCircular
from simulacion.escenarios import Escenarios
from simulacion.productor import Productor
from simulacion.consumidor import Consumidor


class VentanaSimulador(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.title("Simulación")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(fg_color="#C9EBED")

        # GRID PRINCIPAL 
        for i in range(4):
            self.grid_rowconfigure(i, weight=1)
        for j in range(4):
            self.grid_columnconfigure(j, weight=1)

        # LÓGICA
        self.buffer = BufferCircular(10)

        self.semaforos = {
            "mutex": threading.Semaphore(1),
            "vacios": threading.Semaphore(10),
            "llenos": threading.Semaphore(0)
        }

        self.running = {"state": False}
        self.busy_running = False
        self.escenarios = Escenarios(self.buffer, self.log_estandarizado, self, pausa=0.8)

        self.stats = {
            "producidos": 0,
            "consumidos": 0,
            "perdidos": 0,
            "escenario": "Ninguno",
            "estado_sistema": "Detenido"
        }

        # FONDO
        self.bg_image = ctk.CTkImage(
            light_image=Image.open("images/fondo.jpg"),
            size=(1200, 800)
        )

        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        # FILA 1

        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(frame_titulo, text="Simulación del \n" "radar inteligente",
                     font=("Arial", 20, "bold"), text_color="#0F7172").pack()
        ctk.CTkLabel(frame_titulo, text="Caso productores y consumidores",
                     font=("Arial", 14), text_color="#0F7172").pack()

        frame_esc = ctk.CTkFrame(self, fg_color="transparent")
        frame_esc.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(frame_esc, text="Escenarios", font=("Arial", 16, "bold")).pack()

        estilo_btn = {
            "fg_color": "#FFD900",
            "text_color": "#138688",
            "hover_color": "#FFC300",
            "corner_radius": 16,
            "width": 120,
            "height": 35
        }

        frame_btns = ctk.CTkFrame(frame_esc, fg_color="transparent")
        frame_btns.pack()

        ctk.CTkButton(frame_btns, text="Desbordamiento",
                      command=self.escenarios.desbordamiento, **estilo_btn).grid(row=0, column=0, padx=5)

        ctk.CTkButton(frame_btns, text="Vacío",
                      command=self.escenarios.vacio, **estilo_btn).grid(row=0, column=1, padx=5)

        ctk.CTkButton(frame_btns, text="Carrera",
                      command=self.escenarios.carrera, **estilo_btn).grid(row=0, column=2, padx=5)

        ctk.CTkButton(frame_btns, text="Semáforos",
                      command=self.iniciar_hilos, **estilo_btn).grid(row=0, column=3, padx=5)

        frame_control = ctk.CTkFrame(self, fg_color="transparent")
        frame_control.grid(row=0, column=2, sticky="nsew")

        ctk.CTkLabel(frame_control, text="Control", font=("Arial", 16, "bold")).pack()

        frame_ctrl_btns = ctk.CTkFrame(frame_control, fg_color="transparent")
        frame_ctrl_btns.pack()

        self.btn_detener = ctk.CTkButton(frame_ctrl_btns, text="Detener",
                                         fg_color="#FF4C4C", text_color="white",
                                         command=self.detener_hilos)
        self.btn_detener.grid(row=0, column=0, padx=5)

        self.btn_reanudar = ctk.CTkButton(frame_ctrl_btns, text="Reanudar",
                                          command=self.iniciar_hilos)
        self.btn_reanudar.grid(row=0, column=1, padx=5)

        frame_modo = ctk.CTkFrame(self, fg_color="transparent")
        frame_modo.grid(row=0, column=3, sticky="nsew")

        ctk.CTkLabel(frame_modo, text="Modo espera activa",
                     font=("Arial", 14, "bold")).pack()

        
        self.switch_busy = ctk.CTkSwitch(
            frame_modo,
            text="Activar while infinito",
            command=self.toggle_busy_wait
        )
        self.switch_busy.pack()

        # FILA 2

        frame_prod = ctk.CTkFrame(self,  fg_color="white")
        frame_prod.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(frame_prod, text="Productor (Sensor)", font=("Arial", 14, "bold")).pack()

        img_sensor = ctk.CTkImage(Image.open("images/sensor.jpeg"), size=(80, 80))
        ctk.CTkLabel(frame_prod, image=img_sensor, text="").pack()

        self.estado_prod = ctk.CTkLabel(frame_prod, text="Estado: Inactivo")
        self.estado_prod.pack()

        self.desc_prod = ctk.CTkLabel(frame_prod, text="Esperando inicio")
        self.desc_prod.pack()

        frame_buffer = ctk.CTkFrame(self,  fg_color="transparent")
        frame_buffer.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(frame_buffer, text="Buffer Circular", font=("Arial", 14, "bold")).pack()

        self.celdas = []
        grid_buf = ctk.CTkFrame(frame_buffer)
        grid_buf.pack()

        for i in range(2):
            for j in range(5):
                lbl = ctk.CTkLabel(grid_buf, text="", width=40, height=40, fg_color="white")
                lbl.grid(row=i, column=j, padx=3, pady=3)
                self.celdas.append(lbl)

        legend_frame = ctk.CTkFrame(frame_buffer, fg_color="transparent")
        legend_frame.pack(pady=5)

        def legend_item(parent, color, text):
            item = ctk.CTkFrame(parent, fg_color="transparent")
            item.pack(side="left", padx=5)
            ctk.CTkLabel(item, text="", width=15, height=15, fg_color=color).pack(side="left")
            ctk.CTkLabel(item, text=text).pack(side="left", padx=2)

        legend_item(legend_frame, "white", "Vacío")
        legend_item(legend_frame, "green", "Escribiendo")
        legend_item(legend_frame, "blue", "Leyendo")
        legend_item(legend_frame, "red", "Error")

        frame_cons = ctk.CTkFrame(self, fg_color="white")
        frame_cons.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(frame_cons, text="Consumidor (IA)", font=("Arial", 14, "bold")).pack()

        img_ia = ctk.CTkImage(Image.open("images/ia.jpeg"), size=(80, 80))
        ctk.CTkLabel(frame_cons, image=img_ia, text="").pack()

        self.estado_cons = ctk.CTkLabel(frame_cons, text="Estado: Inactivo")
        self.estado_cons.pack()

        self.desc_cons = ctk.CTkLabel(frame_cons, text="Esperando datos")
        self.desc_cons.pack()

        frame_sem = ctk.CTkFrame(self, fg_color="white")
        frame_sem.grid(row=1, column=3, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(frame_sem, text="Semáforos", font=("Arial", 14, "bold")).pack()

        self.lbl_vacios = ctk.CTkLabel(frame_sem, text="Vacíos: 10")
        self.lbl_vacios.pack()

        self.lbl_llenos = ctk.CTkLabel(frame_sem, text="Llenos: 0")
        self.lbl_llenos.pack()

        self.lbl_mutex = ctk.CTkLabel(frame_sem, text="Mutex: 1")
        self.lbl_mutex.pack()

        # FILA 3

        frame_console = ctk.CTkFrame(self, fg_color="transparent")
        frame_console.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(frame_console, text="Consola telemetría").pack(anchor="e")

        self.textbox = ctk.CTkTextbox(frame_console)
        self.textbox.pack(expand=True, fill="both")

        frame_info = ctk.CTkFrame(self,fg_color="white")
        frame_info.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.info_labels = {}
        campos = ["Registros", "Producidos", "Consumidos", "Perdidos", "Escenario", "Tiempo", "CPU Burst"]

        for c in campos:
            lbl = ctk.CTkLabel(frame_info, text=f"{c}: 0")
            lbl.pack(anchor="w")
            self.info_labels[c] = lbl

        ctk.CTkButton(self, text="Volver",
                      command=self.volver_inicio,
                      fg_color="#FFD900",
                      text_color="#138688").grid(row=3, column=0, columnspan=4)

    

    def escenario_busy_wait(self):
      self.limpiar_consola()
      self.buffer.reset()

      self.stats = {
        "producidos": 10,
        "consumidos": 0,
        "perdidos": 0,
        "escenario": "Busy Waiting (while infinito)",
        "estado_sistema": "Saturado"
      }

    # ---- se llena el buffer ----
      for i in range(self.buffer.tamaño):
        self.buffer.buffer[i] = f"D{i+1}"
      self.buffer.count = self.buffer.tamaño
      self.buffer.in_index = 0
      self.buffer.out_index = 0

      self.actualizar_panel_info()
      self.actualizar_buffer_ui()

     
      self.configure(fg_color="#FFF3A0")

    
      self.actualizar_estado_hilos(
        productor_texto="Productor ACTIVO",
        productor_desc="Sensor esperando espacio...",
        consumidor_texto="Consumidor inactivo",
        consumidor_desc="No consume (sistema saturado)"
       )

      self.busy_running = True  

      self.log_estandarizado("WARN", "Modo BUSY WAIT activado: buffer lleno, CPU en espera activa")

   
      def loop_busy():
       while self.busy_running:

        # Carga CPU
        start = time.time()
        while time.time() - start < 0.2:
            pass

        if not self.busy_running:
            break

        cpu = psutil.cpu_percent(interval=None)

        if not self.busy_running:
            break

        # doble validación antes de tocar UI
        self.after(0, lambda c=cpu:
            self.info_labels["CPU Burst"].configure(text=f"CPU Burst: {c}%")
            if self.busy_running else None
         )

        if not self.busy_running:
            break

        self.after(0, lambda:
            self.log_estandarizado("WARN", "Sensor esperando espacio... (busy waiting)")
             if self.busy_running else None
         )

    
      threading.Thread(target=loop_busy, daemon=True).start()
    def toggle_busy_wait(self):
      if self.switch_busy.get():
        self.running["state"] = False
        self.escenario_busy_wait()
      else:
        
        self.busy_running = False

        time.sleep(0.25) 
        self.limpiar_consola()
        self.buffer.reset()
        self.configure(fg_color="#C9EBED")
        self.actualizar_estado_hilos(
        productor_texto="Estado: Inactivo",
        consumidor_texto="Estado: Inactivo",
        productor_desc="Esperando inicio",
        consumidor_desc="Esperando datos"
         )
        
        self.after(50, self.limpiar_consola)
        self.after(50, lambda: self.info_labels["CPU Burst"].configure(text="CPU Burst: 0%"))

        self.stats = {
            "producidos": 0,
            "consumidos": 0,
            "perdidos": 0,
            "escenario": "Ninguno",
            "estado_sistema": "Detenido"
        }

        self.actualizar_panel_info()
        self.actualizar_buffer_ui()

        
        self.info_labels["CPU Burst"].configure(text="CPU Burst: 0%")


    def actualizar_panel_info(self):
        self.info_labels["Registros"].configure(text=f"Registros buffer: {self.buffer.count}")
        self.info_labels["Producidos"].configure(text=f"Producidos: {self.stats['producidos']}")
        self.info_labels["Consumidos"].configure(text=f"Consumidos: {self.stats['consumidos']}")
        self.info_labels["Perdidos"].configure(text=f"Perdidos: {self.stats['perdidos']}")
        self.info_labels["Escenario"].configure(text=f"Escenario: {self.stats['escenario']}")
        self.info_labels["Tiempo"].configure(text=f"Estado: {self.stats['estado_sistema']}")

    def resetear_estadisticas(self, nuevo_escenario):
        self.stats = {
            "producidos": 0,
            "consumidos": 0,
            "perdidos": 0,
            "escenario": nuevo_escenario,
            "estado_sistema": "Ejecutando"
        }
        self.actualizar_panel_info()

    def actualizar_estado_hilos(self, productor_texto=None, consumidor_texto=None, productor_desc=None, consumidor_desc=None):
        if productor_texto is not None:
            self.estado_prod.configure(text=productor_texto)
        if consumidor_texto is not None:
            self.estado_cons.configure(text=consumidor_texto)
        if productor_desc is not None:
            self.desc_prod.configure(text=productor_desc)
        if consumidor_desc is not None:
            self.desc_cons.configure(text=consumidor_desc)

    def log(self, msg):
        self.after(0, lambda: self._log(msg))

    def _log(self, msg):
        self.textbox.insert("end", msg + "\n")
        self.textbox.see("end")

    def log_estandarizado(self, nivel, mensaje):
        self.log(f"{nivel}: {mensaje}")

    def iniciar_hilos(self):
        self.resetear_estadisticas("Productor/Consumidor con semáforos")
        self.stats["estado_sistema"] = "Ejecutando"
        self.running["state"] = True

        self.productor = Productor(self.buffer, self.semaforos, self.log_estandarizado, self.running, self)
        self.consumidor = Consumidor(self.buffer, self.semaforos, self.log_estandarizado, self.running, self)

        threading.Thread(target=self.productor.run, daemon=True).start()
        threading.Thread(target=self.consumidor.run, daemon=True).start()

        self.log_estandarizado("INFO", "Simulación iniciada con semáforos")
        self.actualizar_estado_hilos("Productor activo", "Consumidor activo", "Esperando vacíos...", "Esperando llenos...")
        self.actualizar_semaforos_ui()
        
    def detener_hilos(self):
        self.running["state"] = False
        self.log("Simulación detenida")

    def volver_inicio(self):
        self.running["state"] = False
        self.parent.deiconify()
        self.destroy()

    def pintar_lectura(self, indice):
      """Pinta una celda de azul cuando es leída."""
      if 0 <= indice < len(self.celdas):
        celda = self.celdas[indice]
        celda.configure(fg_color="blue", text_color="black")
    def actualizar_buffer_ui(self):
      """Actualiza colores y textos de las celdas del buffer según su contenido."""
      estado = self.buffer.estado()

      for idx, celda in enumerate(self.celdas):
        dato = estado[idx]

        if dato is None:
            celda.configure(text="", fg_color="white")

        else:
          
            celda.configure(text=str(dato), fg_color="green", text_color="black")

    def limpiar_consola(self):
        self.textbox.delete("1.0", "end")
        
    def actualizar_semaforos_ui(self):
     self.lbl_vacios.configure(text=f"Vacíos: {self.semaforos['vacios']._value}")
     self.lbl_llenos.configure(text=f"Llenos: {self.semaforos['llenos']._value}")
     self.lbl_mutex.configure(text=f"Mutex: {self.semaforos['mutex']._value}")