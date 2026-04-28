import customtkinter as ctk
from PIL import Image

class VentanaInicio(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Simulador de Hilos")
        self.geometry("900x600")

        # FONDO
        self.bg_image = ctk.CTkImage(
            light_image=Image.open("images/fondo.jpg"),
            size=(900, 600)
        )

        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # TÍTULO
        self.titulo = ctk.CTkLabel(
            self,
            text=" Caso de Productores y Consumidores ",
            font=("Helvetica", 36, "bold"),
            text_color="#138688"
        )
        self.titulo.place(relx=0.5, rely=0.2, anchor="center")

        # DESCRIPCION
        texto = (
            "Sistema de captura de un radar de tráfico inteligente en Barquisimeto.\n"
            "Un sensor de alta velocidad captura metadatos de vehículos y los deposita \n"
             "en un área de memoria compartida que tiene capacidad para exactamente 10 registros.\n"
             "Por otro lado, un proceso de análisis de inteligencia artificial  extrae esos datos \n"
             "para identificar infracciones. \n "
        )

        self.descripcion = ctk.CTkLabel(
            self,
            text=texto,
            font=("Segoe UI", 18),
            text_color="#138688",
            justify="center"
        )
        self.descripcion.place(relx=0.5, rely=0.4, anchor="center")

        # BOTON
        self.boton = ctk.CTkButton(
            self,
            text="Iniciar Simulación",
            command=self.ir_simulador
        )
        self.boton.place(relx=0.5, rely=0.7, anchor="center")

    def ir_simulador(self):
        self.withdraw()  

        from ui.ventana_simulador import VentanaSimulador
        VentanaSimulador(self) 