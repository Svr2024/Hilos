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
        self.geometry("1000x600")
        self.configure(fg_color="#8FD3D5")

        # BUFFER
  
        self.buffer = BufferCircular(10)

       
        # SEMÁFOROS
      
        self.semaforos = {
            "mutex": threading.Semaphore(1),
            "vacios": threading.Semaphore(10),
            "llenos": threading.Semaphore(0)
        }

        self.running = {"state": False}

        # ESCENARIOS
    
        self.escenarios = Escenarios(self.buffer, self.log)

      
        # FONDO
       
        self.bg_image = ctk.CTkImage(
            light_image=Image.open("images/fondo.jpg"),
            size=(1000, 600)
        )

        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        
        # TÍTULO
       
        self.titulo = ctk.CTkLabel(
            self,
            text="Simulación de escenarios",
            font=("Arial", 30, "bold"),
            text_color="#138688",
            fg_color="transparent"
        )
        self.titulo.place(relx=0.5, rely=0.1, anchor="center")

        
        # BOTONES 
     
        estilo_btn = {
            "fg_color": "#FFD900",
            "text_color": "#138688",
            "hover_color": "#FFC300",
            "corner_radius": 12,
            "width": 160,
            "height": 40
        }

      
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.place(relx=0.5, rely=0.25, anchor="center")

        self.btn_desbordamiento = ctk.CTkButton(
            self.frame_botones,
            text="Desbordamiento",
            command=self.escenarios.desbordamiento,
            **estilo_btn
        )
        self.btn_desbordamiento.grid(row=0, column=0, padx=10)

        self.btn_vacio = ctk.CTkButton(
            self.frame_botones,
            text="Vacío",
            command=self.escenarios.vacio,
            **estilo_btn
        )
        self.btn_vacio.grid(row=0, column=1, padx=10)

        self.btn_carrera = ctk.CTkButton(
            self.frame_botones,
            text="Carrera",
            command=self.escenarios.carrera,
            **estilo_btn
        )
        self.btn_carrera.grid(row=0, column=2, padx=10)

        self.btn_semaforos = ctk.CTkButton(
            self.frame_botones,
            text="Semáforos",
            command=self.iniciar_hilos,
            **estilo_btn
        )
        self.btn_semaforos.grid(row=0, column=3, padx=10)

        # BOTÓN DETENER
     
        self.btn_detener = ctk.CTkButton(
            self,
            text="Detener",
            fg_color="#FF4C4C",
            text_color="white",
            hover_color="#FF1F1F",
            command=self.detener_hilos,
            width=160,
            height=40
        )
        self.btn_detener.place(relx=0.5, rely=0.35, anchor="center")

       
        # CONSOLA
       
        self.textbox = ctk.CTkTextbox(
            self,
            width=850,
            height=250,
            fg_color="white",
            text_color="black"
        )
        self.textbox.place(relx=0.5, rely=0.6, anchor="center")

     
        # VOLVER
       
        ctk.CTkButton(
            self,
            text="Volver",
            command=self.volver_inicio,
            fg_color="#FFD900",
            text_color="#138688",
            hover_color="#FFC300"
        ).place(relx=0.5, rely=0.9, anchor="center")

   
    # LOG

    def log(self, msg):
        self.after(0, lambda: self._log(msg))

    def _log(self, msg):
        self.textbox.insert("end", msg + "\n")
        self.textbox.see("end")

  
    # HILOS
 
    def iniciar_hilos(self):
        self.textbox.delete("0.0", "end")

        self.running["state"] = True

        productor = Productor(self.buffer, self.semaforos, self.log, self.running)
        consumidor = Consumidor(self.buffer, self.semaforos, self.log, self.running)

        threading.Thread(target=productor.run, daemon=True).start()
        threading.Thread(target=consumidor.run, daemon=True).start()

        self.log(" Simulación con semáforos iniciada")

    def detener_hilos(self):
        self.running["state"] = False
        self.log(" Simulación detenida")

    def volver_inicio(self):
        self.running["state"] = False
        self.parent.deiconify()
        self.destroy()