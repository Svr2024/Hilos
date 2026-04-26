import customtkinter as ctk
from PIL import Image
import threading

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

        self.escenarios = Escenarios(self.buffer, self.log)

        # FONDO
        self.bg_image = ctk.CTkImage(
            light_image=Image.open("images/fondo.jpg"),
            size=(1200, 800)
        )

        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

       
        # FILA 1
        

        # Col 1
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(frame_titulo, text="Simulación del radar inteligente",
                     font=("Arial", 20, "bold"), text_color="#0F7172").pack()
        ctk.CTkLabel(frame_titulo, text="Caso productores y consumidores",
                     font=("Arial", 14), text_color="#0F7172").pack()

        # Col 2
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

        # Col 3
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

        # Col 4
        frame_modo = ctk.CTkFrame(self, fg_color="transparent")
        frame_modo.grid(row=0, column=3, sticky="nsew")

        ctk.CTkLabel(frame_modo, text="Modo espera activa",
                     font=("Arial", 14, "bold")).pack()

        self.switch_busy = ctk.CTkSwitch(frame_modo, text="Activar while infinito")
        self.switch_busy.pack()

        # FILA 2
       

        # Productor
        frame_prod = ctk.CTkFrame(self,  fg_color="white")
        frame_prod.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(frame_prod, text="Productor (Sensor)", font=("Arial", 14, "bold")).pack()

        img_sensor = ctk.CTkImage(Image.open("images/sensor.jpeg"), size=(80, 80))
        ctk.CTkLabel(frame_prod, image=img_sensor, text="").pack()

        self.estado_prod = ctk.CTkLabel(frame_prod, text="Estado: Inactivo")
        self.estado_prod.pack()

        self.desc_prod = ctk.CTkLabel(frame_prod, text="Esperando inicio")
        self.desc_prod.pack()

        # Buffer
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

        # Leyenda colores buffer
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

        # Consumidor
        frame_cons = ctk.CTkFrame(self, fg_color="white")
        frame_cons.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(frame_cons, text="Consumidor (IA)", font=("Arial", 14, "bold")).pack()

        img_ia = ctk.CTkImage(Image.open("images/ia.jpeg"), size=(80, 80))
        ctk.CTkLabel(frame_cons, image=img_ia, text="").pack()

        self.estado_cons = ctk.CTkLabel(frame_cons, text="Estado: Inactivo")
        self.estado_cons.pack()

        self.desc_cons = ctk.CTkLabel(frame_cons, text="Esperando datos")
        self.desc_cons.pack()

        # Semaforos
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
       

        # Consola
        frame_console = ctk.CTkFrame(self, fg_color="transparent")
        frame_console.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(frame_console, text="Consola telemetría").pack(anchor="e")

        self.textbox = ctk.CTkTextbox(frame_console)
        self.textbox.pack(expand=True, fill="both")

        # Info sistema
        frame_info = ctk.CTkFrame(self,fg_color="white")
        frame_info.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.info_labels = {}
        campos = ["Registros", "Producidos", "Consumidos", "Perdidos", "Escenario", "Tiempo"]

        for c in campos:
            lbl = ctk.CTkLabel(frame_info, text=f"{c}: 0")
            lbl.pack(anchor="w")
            self.info_labels[c] = lbl

        # FILA 4


        ctk.CTkButton(self, text="Volver",
                      command=self.volver_inicio,
                      fg_color="#FFD900",
                      text_color="#138688").grid(row=3, column=0, columnspan=4)

    # LOG


    def log(self, msg):
        self.after(0, lambda: self._log(msg))

    def _log(self, msg):
        self.textbox.insert("end", msg + "\n")
        self.textbox.see("end")

   
    # HILOS
  

    def iniciar_hilos(self):
        self.running["state"] = True

        productor = Productor(self.buffer, self.semaforos, self.log, self.running)
        consumidor = Consumidor(self.buffer, self.semaforos, self.log, self.running)

        threading.Thread(target=productor.run, daemon=True).start()
        threading.Thread(target=consumidor.run, daemon=True).start()

        self.log("Simulación iniciada")

    def detener_hilos(self):
        self.running["state"] = False
        self.log("Simulación detenida")

    def volver_inicio(self):
        self.running["state"] = False
        self.parent.deiconify()
        self.destroy()
