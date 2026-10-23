import tkinter as tk
from tkinter import ttk


COLOR_FONDO = "#98b7c1"
COLOR_TEXTO = "#000000"
COLOR_SUPERFICIE = "#ffffff"
FUENTE = "Lucida Sans Unicode"


class InterfazCaminata:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Simulación de caminata aleatoria")
        self.ventana.geometry("980x680")
        self.ventana.minsize(760, 560)
        self.ventana.configure(bg=COLOR_FONDO)

        self.parametros = None
        self._crear_estilos()
        self._crear_interfaz()

    def _crear_estilos(self):
        estilo = ttk.Style(self.ventana)
        estilo.theme_use("clam")
        estilo.configure(
            "TEntry",
            fieldbackground=COLOR_SUPERFICIE,
            foreground=COLOR_TEXTO,
            padding=8,
            font=(FUENTE, 10),
        )
        estilo.configure(
            "TButton",
            background=COLOR_TEXTO,
            foreground=COLOR_SUPERFICIE,
            padding=(12, 9),
            font=(FUENTE, 10, "bold"),
        )
        estilo.map(
            "TButton",
            background=[("active", "#303030"), ("disabled", "#666666")],
            foreground=[("disabled", COLOR_SUPERFICIE)],
        )

    def _crear_interfaz(self):
        contenedor = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=28, pady=24)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=1)
        contenedor.rowconfigure(1, weight=1)

        tk.Label(
            contenedor,
            text="Simulación de caminata aleatoria",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=(FUENTE, 19, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 20))

        contenido = tk.Frame(contenedor, bg=COLOR_FONDO)
        contenido.grid(row=1, column=0, sticky="nsew")
        contenido.columnconfigure(0, weight=0, minsize=280)
        contenido.columnconfigure(1, weight=1)
        contenido.rowconfigure(0, weight=1)

        self._crear_panel_parametros(contenido)
        self._crear_panel_resultados(contenido)

    def _crear_panel_parametros(self, padre):
        panel = tk.Frame(padre, bg=COLOR_SUPERFICIE, padx=20, pady=20)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        panel.columnconfigure(0, weight=1)

        tk.Label(
            panel,
            text="Parámetros",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 13, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 18))

        self.entradas = {}
        parametros = (
            ("dimensiones", "Dimensión del sistema"),
            ("pasos", "Número de pasos"),
            ("repeticiones", "Repeticiones del experimento"),
        )
        for fila, (clave, etiqueta) in enumerate(parametros, start=1):
            tk.Label(
                panel,
                text=etiqueta,
                bg=COLOR_SUPERFICIE,
                fg=COLOR_TEXTO,
                font=(FUENTE, 10),
                anchor="w",
                wraplength=230,
                justify="left",
            ).grid(row=fila * 2 - 1, column=0, sticky="ew", pady=(0, 6))
            entrada = ttk.Entry(panel)
            entrada.grid(row=fila * 2, column=0, sticky="ew", pady=(0, 14))
            self.entradas[clave] = entrada

        ttk.Button(
            panel,
            text="Ejecutar simulación",
            command=self._validar_parametros,
        ).grid(row=7, column=0, sticky="ew", pady=(8, 14))

        self.estado = tk.Label(
            panel,
            text="Ejecutable C++: pendiente de integración.",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 9),
            anchor="w",
            justify="left",
            wraplength=230,
        )
        self.estado.grid(row=8, column=0, sticky="ew")

    def _crear_panel_resultados(self, padre):
        panel = tk.Frame(padre, bg=COLOR_SUPERFICIE, padx=20, pady=20)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        tk.Label(
            panel,
            text="Resultados",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 13, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 18))

        tk.Label(
            panel,
            text="Distancias máximas por caminata",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 10, "bold"),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.distancias = self._crear_area_resultado(panel, 2)

        tk.Label(
            panel,
            text="Tiempo de ejecución",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 10, "bold"),
            anchor="w",
        ).grid(row=3, column=0, sticky="ew", pady=(18, 8))
        self.tiempo = self._crear_area_resultado(panel, 4, height=3)

    @staticmethod
    def _crear_area_resultado(padre, fila, height=12):
        area = tk.Text(
            padre,
            height=height,
            wrap="word",
            bg=COLOR_SUPERFICIE,
            fg="#555555",
            font=(FUENTE, 9),
            relief="solid",
            borderwidth=1,
            padx=10,
            pady=8,
        )
        area.grid(row=fila, column=0, sticky="nsew")
        area.insert("1.0", "Los resultados aparecerán aquí.")
        area.configure(state="disabled")
        return area

    def _validar_parametros(self):
        self.parametros = None
        valores = {}
        for clave, entrada in self.entradas.items():
            texto = entrada.get().strip()
            try:
                valor = int(texto)
            except ValueError:
                self._mostrar_estado(
                    "Introduce valores enteros positivos en todos los campos.",
                    error=True,
                )
                entrada.focus_set()
                return
            if valor <= 0:
                self._mostrar_estado(
                    "Todos los parámetros deben ser mayores que cero.",
                    error=True,
                )
                entrada.focus_set()
                return
            valores[clave] = valor

        self.parametros = valores
        self._mostrar_estado(
            "Parámetros válidos. La conexión con el ejecutable C++ está pendiente."
        )

    def _mostrar_estado(self, mensaje, error=False):
        self.estado.configure(
            text=mensaje,
            fg="#9b1c1c" if error else COLOR_TEXTO,
        )


if __name__ == "__main__":
    ventana = tk.Tk()
    InterfazCaminata(ventana)
    ventana.mainloop()
