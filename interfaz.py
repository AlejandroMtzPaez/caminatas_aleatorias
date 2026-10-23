import csv
import math
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk


COLOR_FONDO = "#98b7c1"
COLOR_TEXTO = "#000000"
COLOR_SUPERFICIE = "#ffffff"
FUENTE = "Arial"


class InterfazCaminata:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Simulación de caminata aleatoria")
        self.ventana.geometry("980x680")
        self.ventana.minsize(760, 560)
        self.ventana.configure(bg=COLOR_FONDO)

        self.parametros = None
        self._resultados_backend = queue.Queue()
        self._en_ejecucion = False
        self._datos_grafica = []
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
        estilo.configure(
            "TNotebook.Tab",
            font=(FUENTE, 10),
            padding=(10, 6),
        )
        estilo.configure(
            "Treeview",
            font=(FUENTE, 9),
            rowheight=24,
        )
        estilo.configure(
            "Treeview.Heading",
            font=(FUENTE, 9, "bold"),
        )
        estilo.map(
            "TButton",
            background=[("active", "#303030"), ("disabled", "#666666")],
            foreground=[("disabled", COLOR_SUPERFICIE)],
        )

    def _crear_interfaz(self):
        self.pestanas = ttk.Notebook(self.ventana)
        self.pestanas.pack(fill="both", expand=True, padx=18, pady=16)
        self.pestana_individual = tk.Frame(self.pestanas, bg=COLOR_FONDO, padx=10, pady=12)
        self.pestana_multiple = tk.Frame(self.pestanas, bg=COLOR_FONDO, padx=24, pady=20)
        self.pestanas.add(self.pestana_individual, text="Simulación individual")
        self.pestanas.add(self.pestana_multiple, text="Simulaciones múltiples")

        contenedor = self.pestana_individual
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
        self._crear_panel_multiple(self.pestana_multiple)

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

        self.boton_ejecutar = ttk.Button(
            panel,
            text="Ejecutar simulación",
            command=self._validar_parametros,
        )
        self.boton_ejecutar.grid(row=7, column=0, sticky="ew", pady=(8, 14))

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

    def _crear_panel_multiple(self, padre):
        padre.columnconfigure(0, weight=1)
        padre.rowconfigure(3, weight=1)

        tk.Label(
            padre,
            text="Simulaciones múltiples",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=(FUENTE, 17, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 16))

        parametros = tk.Frame(padre, bg=COLOR_SUPERFICIE, padx=18, pady=14)
        parametros.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        parametros.columnconfigure(1, weight=1)
        parametros.columnconfigure(2, weight=1)
        parametros.columnconfigure(3, weight=1)

        tk.Label(
            parametros,
            text="Dimensión del sistema",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 10, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 16))
        self.entrada_dimension_multiple = ttk.Entry(parametros, width=12)
        self.entrada_dimension_multiple.insert(0, "2")
        self.entrada_dimension_multiple.grid(row=0, column=1, sticky="w")

        self.entradas_pasadas = self._crear_entradas_serie(
            parametros,
            fila=1,
            titulo="Pasos por caminata",
        )
        self.entradas_repeticiones = self._crear_entradas_serie(
            parametros,
            fila=2,
            titulo="Repeticiones",
        )
        for entrada, valor in zip(
            self.entradas_pasadas + self.entradas_repeticiones,
            (100, 1000, 10000, 100, 1000, 10000),
        ):
            entrada.insert(0, str(valor))

        acciones = tk.Frame(padre, bg=COLOR_FONDO)
        acciones.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        self.boton_multiple = ttk.Button(
            acciones,
            text="Ejecutar",
            command=self._validar_parametros_multiples,
        )
        self.boton_multiple.pack(side="left")
        self.estado_multiple = tk.Label(
            acciones,
            text="",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=(FUENTE, 9),
            anchor="w",
            justify="left",
        )
        self.estado_multiple.pack(side="left", padx=14, fill="x", expand=True)

        resultados = tk.Frame(padre, bg=COLOR_SUPERFICIE, padx=18, pady=16)
        resultados.grid(row=3, column=0, sticky="nsew")
        resultados.columnconfigure(0, weight=1)
        resultados.rowconfigure(1, weight=1)

        tk.Label(
            resultados,
            text="Resultados de las combinaciones",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 11, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 8))
        contenedor_tabla = tk.Frame(resultados, bg=COLOR_SUPERFICIE)
        contenedor_tabla.grid(row=1, column=0, sticky="nsew")
        contenedor_tabla.columnconfigure(0, weight=1)
        contenedor_tabla.rowconfigure(0, weight=1)
        self.tabla_multiple = ttk.Treeview(
            contenedor_tabla,
            columns=("pasos", "repeticiones", "promedio", "tiempo"),
            show="headings",
            height=9,
        )
        for columna, titulo, ancho in (
            ("pasos", "Pasos", 120),
            ("repeticiones", "Repeticiones", 140),
            ("promedio", "Promedio distancia máxima", 240),
            ("tiempo", "Tiempo (s)", 140),
        ):
            self.tabla_multiple.heading(columna, text=titulo)
            self.tabla_multiple.column(
                columna,
                width=ancho,
                anchor="e" if columna in ("promedio", "tiempo") else "center",
            )
        self.tabla_multiple.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(
            contenedor_tabla,
            orient="vertical",
            command=self.tabla_multiple.yview,
        )
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla_multiple.configure(yscrollcommand=barra.set)

        self.promedio_global = tk.Label(
            resultados,
            text="Promedio general ponderado por caminatas: —",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 10, "bold"),
            anchor="w",
        )
        self.promedio_global.grid(row=2, column=0, sticky="ew", pady=(12, 4))
        self.tiempo_multiple = tk.Label(
            resultados,
            text="Tiempo total: —",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 10),
            anchor="w",
        )
        self.tiempo_multiple.grid(row=3, column=0, sticky="ew")

    @staticmethod
    def _crear_entradas_serie(padre, fila, titulo):
        tk.Label(
            padre,
            text=titulo,
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 10, "bold"),
            anchor="w",
        ).grid(row=fila, column=0, sticky="w", padx=(0, 16), pady=(12, 0))
        entradas = []
        for columna in range(1, 4):
            campo = ttk.Entry(padre, width=12)
            campo.grid(row=fila, column=columna, sticky="ew", padx=(0, 10), pady=(12, 0))
            entradas.append(campo)
        return entradas

    def _crear_panel_resultados(self, padre):
        panel = tk.Frame(padre, bg=COLOR_SUPERFICIE, padx=20, pady=20)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)
        panel.rowconfigure(6, weight=2)

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
            text="Resultados por caminata",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 10, "bold"),
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 8))

        contenedor_tabla = tk.Frame(panel, bg=COLOR_SUPERFICIE)
        contenedor_tabla.grid(row=2, column=0, sticky="nsew")
        contenedor_tabla.columnconfigure(0, weight=1)
        contenedor_tabla.rowconfigure(0, weight=1)
        self.tabla = ttk.Treeview(
            contenedor_tabla,
            columns=("caminata", "distancia", "tiempo"),
            show="headings",
            height=7,
        )
        self.tabla.heading("caminata", text="Caminata")
        self.tabla.heading("distancia", text="Distancia máxima")
        self.tabla.heading("tiempo", text="Tiempo (µs)")
        self.tabla.column("caminata", width=100, anchor="center", stretch=False)
        self.tabla.column("distancia", width=180, anchor="e")
        self.tabla.column("tiempo", width=150, anchor="e")
        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_tabla = ttk.Scrollbar(
            contenedor_tabla,
            orient="vertical",
            command=self.tabla.yview,
        )
        barra_tabla.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=barra_tabla.set)

        tk.Label(
            panel,
            text="Distancia máxima por caminata",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 10, "bold"),
            anchor="w",
        ).grid(row=5, column=0, sticky="ew", pady=(14, 8))
        self.grafica = tk.Canvas(
            panel,
            height=240,
            bg=COLOR_SUPERFICIE,
            highlightthickness=1,
            highlightbackground="#b5b5b5",
        )
        self.grafica.grid(row=6, column=0, sticky="nsew")
        self.grafica.bind("<Configure>", self._dibujar_grafica)

        self.tiempo = tk.Label(
            panel,
            text="Tiempo total de ejecución: —",
            bg=COLOR_SUPERFICIE,
            fg=COLOR_TEXTO,
            font=(FUENTE, 9),
            anchor="w",
        )
        self.tiempo.grid(row=7, column=0, sticky="ew", pady=(12, 0))

    def _validar_parametros(self):
        if self._en_ejecucion:
            return

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
            if not 1 <= valor <= 2_147_483_647:
                self._mostrar_estado(
                    "Cada parámetro debe ser un entero entre 1 y 2 147 483 647.",
                    error=True,
                )
                entrada.focus_set()
                return
            valores[clave] = valor

        self.parametros = valores
        self._en_ejecucion = True
        self._configurar_botones_ejecucion("disabled")
        self._limpiar_resultados("Simulación en curso...")
        self._mostrar_estado("Simulación en curso...")
        threading.Thread(
            target=self._ejecutar_backend,
            args=(valores,),
            daemon=True,
        ).start()
        self.ventana.after(
            100,
            self._revisar_resultado_backend,
        )

    def _ruta_backend(self):
        if getattr(sys, "frozen", False):
            directorio = Path(
                getattr(sys, "_MEIPASS", Path(sys.executable).parent)
            )
            ruta = directorio / "caminata_backend.exe"
        else:
            raiz = Path(__file__).resolve().parent
            candidatos = (
                raiz / "build" / "caminata_backend.exe",
                raiz / "caminata_backend.exe",
            )
            ruta = next((candidato for candidato in candidatos if candidato.is_file()), None)
            if ruta is None:
                raise FileNotFoundError(
                    "No se encontró build/caminata_backend.exe. "
                    "Genera el backend ejecutando build.ps1."
                )

        if not ruta.is_file():
            raise FileNotFoundError(f"No se encontró el ejecutable C++: {ruta}")
        return ruta

    def _ejecutar_backend(self, valores):
        try:
            directorio_resultados = Path.home() / "CaminatasAleatorias"
            directorio_resultados.mkdir(parents=True, exist_ok=True)
            proceso = subprocess.run(
                [
                    str(self._ruta_backend()),
                    "--gui",
                    str(valores["dimensiones"]),
                    str(valores["pasos"]),
                    str(valores["repeticiones"]),
                ],
                cwd=directorio_resultados,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            registros = None
            if proceso.returncode == 0:
                registros = self._leer_csv_resultados(
                    directorio_resultados / "distancias_maximas.csv",
                    valores["repeticiones"],
                )
            self._resultados_backend.put(
                (
                    "individual",
                    proceso.returncode,
                    proceso.stdout,
                    proceso.stderr,
                    registros,
                    directorio_resultados / "distancias_maximas.csv",
                )
            )
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            self._resultados_backend.put(("individual", None, "", str(error), None, None))

    def _revisar_resultado_backend(self):
        try:
            modo, codigo, salida, error, registros, ruta_csv = (
                self._resultados_backend.get_nowait()
            )
        except queue.Empty:
            self.ventana.after(100, self._revisar_resultado_backend)
            return

        self._en_ejecucion = False
        self._configurar_botones_ejecucion("normal")
        if codigo != 0:
            detalle = error.strip() or salida.strip() or "Error desconocido."
            self._mostrar_estado_modo(modo, f"Falló la simulación: {detalle}", error=True)
            return

        if modo == "multiple":
            self._mostrar_resultados_multiples(salida, registros, ruta_csv)
            return

        try:
            tiempo = self._interpretar_tiempo_total(salida)
        except ValueError as error:
            self._mostrar_estado(f"Respuesta inválida del backend: {error}", error=True)
            return

        for indice, distancia, tiempo_us in registros:
            self.tabla.insert(
                "",
                "end",
                values=(indice, f"{distancia:.4f}", f"{tiempo_us:.4f}"),
            )
        self._datos_grafica = [distancia for _, distancia, _ in registros]
        self._dibujar_grafica()
        self.tiempo.configure(text=f"Tiempo total de ejecución: {tiempo:.6f} s")
        self._mostrar_estado(f"Simulación completada. CSV: {ruta_csv}")

    def _validar_parametros_multiples(self):
        if self._en_ejecucion:
            return

        try:
            dimension = self._leer_entero_positivo(
                self.entrada_dimension_multiple,
                "dimensión",
            )
            pasos = [
                self._leer_entero_positivo(entrada, "pasos")
                for entrada in self.entradas_pasadas
            ]
            repeticiones = [
                self._leer_entero_positivo(entrada, "repeticiones")
                for entrada in self.entradas_repeticiones
            ]
        except ValueError as error:
            self._mostrar_estado_modo("multiple", str(error), error=True)
            return

        if len(set(pasos)) != 3 or len(set(repeticiones)) != 3:
            self._mostrar_estado_modo(
                "multiple",
                "Los tres valores de pasos y repeticiones deben ser distintos.",
                error=True,
            )
            return

        parametros = {
            "dimension": dimension,
            "pasos": pasos,
            "repeticiones": repeticiones,
        }
        self._en_ejecucion = True
        self._configurar_botones_ejecucion("disabled")
        self._limpiar_resultados_multiples()
        self._mostrar_estado_modo("multiple", "Ejecutando...")
        threading.Thread(
            target=self._ejecutar_backend_multiple,
            args=(parametros,),
            daemon=True,
        ).start()
        self.ventana.after(100, self._revisar_resultado_backend)

    @staticmethod
    def _leer_entero_positivo(entrada, nombre):
        try:
            valor = int(entrada.get().strip())
        except ValueError as error:
            raise ValueError(f"El valor de {nombre} debe ser un entero positivo.") from error
        if not 1 <= valor <= 2_147_483_647:
            raise ValueError(f"El valor de {nombre} debe estar entre 1 y 2 147 483 647.")
        return valor

    def _ejecutar_backend_multiple(self, parametros):
        try:
            directorio_resultados = Path.home() / "CaminatasAleatorias"
            directorio_resultados.mkdir(parents=True, exist_ok=True)
            proceso = subprocess.run(
                [
                    str(self._ruta_backend()),
                    "--multiple",
                    str(parametros["dimension"]),
                    *(str(valor) for valor in parametros["pasos"]),
                    *(str(valor) for valor in parametros["repeticiones"]),
                ],
                cwd=directorio_resultados,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            registros = None
            if proceso.returncode == 0:
                registros = self._leer_csv_multiples(
                    directorio_resultados / "simulaciones_multiples.csv",
                    parametros["pasos"],
                    parametros["repeticiones"],
                )
            self._resultados_backend.put(
                (
                    "multiple",
                    proceso.returncode,
                    proceso.stdout,
                    proceso.stderr,
                    registros,
                    directorio_resultados / "simulaciones_multiples.csv",
                )
            )
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            self._resultados_backend.put(("multiple", None, "", str(error), None, None))

    @staticmethod
    def _leer_csv_multiples(ruta, pasos, repeticiones):
        combinaciones = {}
        with ruta.open("r", newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            columnas = {
                "pasos",
                "repeticiones",
                "promedio_distancia_maxima",
                "tiempo_s",
            }
            if lector.fieldnames is None or not columnas.issubset(lector.fieldnames):
                raise ValueError("el CSV múltiple no contiene las columnas esperadas.")

            for fila in lector:
                try:
                    numero_pasos = int(fila["pasos"])
                    numero_repeticiones = int(fila["repeticiones"])
                    promedio = float(fila["promedio_distancia_maxima"])
                    tiempo = float(fila["tiempo_s"])
                except (TypeError, ValueError) as error:
                    raise ValueError("el CSV múltiple contiene valores no numéricos.") from error
                clave = (numero_pasos, numero_repeticiones)
                if (
                    numero_pasos not in pasos
                    or numero_repeticiones not in repeticiones
                    or clave in combinaciones
                    or not math.isfinite(promedio)
                    or promedio < 0
                    or not math.isfinite(tiempo)
                    or tiempo < 0
                ):
                    raise ValueError("el CSV múltiple contiene resultados fuera de rango.")
                combinaciones[clave] = (promedio, tiempo)

        esperadas = {(p, r) for p in pasos for r in repeticiones}
        if set(combinaciones) != esperadas:
            raise ValueError("el CSV múltiple no contiene las 9 combinaciones esperadas.")
        return [
            (p, r, *combinaciones[(p, r)])
            for p in pasos
            for r in repeticiones
        ]

    @staticmethod
    def _interpretar_resumen_multiple(salida):
        resumen = {}
        claves = {
            "PROMEDIO_GENERAL",
            "TIEMPO_TOTAL_SEGUNDOS",
        }
        for linea in salida.splitlines():
            campos = linea.split(",")
            if len(campos) != 2 or campos[0] not in claves or campos[0] in resumen:
                raise ValueError(f"línea inesperada en el resumen: {linea}")
            try:
                valor = float(campos[1])
            except ValueError as error:
                raise ValueError("el resumen contiene valores no numéricos.") from error
            if not math.isfinite(valor) or valor < 0:
                raise ValueError("el resumen contiene valores fuera de rango.")
            resumen[campos[0]] = valor
        if set(resumen) != claves:
            raise ValueError("faltan el promedio general o el tiempo total.")
        return resumen["PROMEDIO_GENERAL"], resumen["TIEMPO_TOTAL_SEGUNDOS"]

    def _mostrar_resultados_multiples(self, salida, registros, ruta_csv):
        try:
            promedio, tiempo_total = self._interpretar_resumen_multiple(salida)
        except ValueError as error:
            self._mostrar_estado_modo("multiple", f"Respuesta inválida: {error}", error=True)
            return

        for pasos, repeticiones, promedio_combinacion, tiempo in registros:
            self.tabla_multiple.insert(
                "",
                "end",
                values=(
                    pasos,
                    repeticiones,
                    f"{promedio_combinacion:.4f}",
                    f"{tiempo:.6f}",
                ),
            )
        self.promedio_global.configure(
            text=f"Promedio general ponderado por caminatas: {promedio:.4f}"
        )
        self.tiempo_multiple.configure(
            text=f"Tiempo total: {tiempo_total:.6f} s"
        )
        self._mostrar_estado_modo("multiple", f"Simulación completada. CSV: {ruta_csv}")

    def _limpiar_resultados_multiples(self):
        self.tabla_multiple.delete(*self.tabla_multiple.get_children())
        self.promedio_global.configure(
            text="Promedio general ponderado por caminatas: —"
        )
        self.tiempo_multiple.configure(text="Tiempo total: —")

    def _configurar_botones_ejecucion(self, estado):
        self.boton_ejecutar.configure(state=estado)
        self.boton_multiple.configure(state=estado)

    def _mostrar_estado_modo(self, modo, mensaje, error=False):
        if modo == "multiple":
            etiqueta = self.estado_multiple
        else:
            etiqueta = self.estado
        etiqueta.configure(text=mensaje, fg="#9b1c1c" if error else COLOR_TEXTO)

    @staticmethod
    def _leer_csv_resultados(ruta, repeticiones):
        registros = []
        indices = set()
        with ruta.open("r", newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            columnas = {"caminata", "distancia_maxima", "tiempo_us"}
            if lector.fieldnames is None or not columnas.issubset(lector.fieldnames):
                raise ValueError("el CSV no contiene las columnas esperadas.")

            for fila in lector:
                try:
                    indice = int(fila["caminata"])
                    distancia = float(fila["distancia_maxima"])
                    tiempo_us = float(fila["tiempo_us"])
                except (TypeError, ValueError) as error:
                    raise ValueError("el CSV contiene valores no numéricos.") from error

                if (
                    not 1 <= indice <= repeticiones
                    or indice in indices
                    or not math.isfinite(distancia)
                    or distancia < 0
                    or not math.isfinite(tiempo_us)
                    or tiempo_us < 0
                ):
                    raise ValueError("el CSV contiene resultados fuera de rango.")
                indices.add(indice)
                registros.append((indice, distancia, tiempo_us))

        if len(registros) != repeticiones:
            raise ValueError("el CSV no contiene una fila por cada caminata.")
        registros.sort(key=lambda registro: registro[0])
        return registros

    @staticmethod
    def _interpretar_tiempo_total(salida):
        tiempo = None

        for linea in salida.splitlines():
            campos = linea.split(",")
            if campos[0] == "TIEMPO_SEGUNDOS" and len(campos) == 2:
                if tiempo is not None:
                    raise ValueError("el backend devolvió más de un tiempo total.")
                try:
                    tiempo = float(campos[1])
                except ValueError as error:
                    raise ValueError("tiempo de ejecución no numérico.") from error
                if not math.isfinite(tiempo) or tiempo < 0:
                    raise ValueError("tiempo de ejecución fuera de rango.")
            elif linea.strip():
                raise ValueError(f"línea inesperada: {linea}")

        if tiempo is None:
            raise ValueError("falta el tiempo total de ejecución.")
        return tiempo

    def _limpiar_resultados(self, mensaje):
        self.tabla.delete(*self.tabla.get_children())
        self._datos_grafica = []
        self.grafica.delete("all")
        self.grafica.create_text(
            12,
            12,
            text=mensaje,
            anchor="nw",
            fill="#555555",
            font=(FUENTE, 9),
        )
        self.tiempo.configure(text="Tiempo total de ejecución: —")

    def _dibujar_grafica(self, _evento=None):
        if not self._datos_grafica:
            return

        lienzo = self.grafica
        lienzo.delete("all")
        ancho = lienzo.winfo_width()
        alto = lienzo.winfo_height()
        margen_izquierdo = 58
        margen_derecho = 18
        margen_superior = 18
        margen_inferior = 42
        ancho_grafica = max(1, ancho - margen_izquierdo - margen_derecho)
        alto_grafica = max(1, alto - margen_superior - margen_inferior)
        maximo = max(self._datos_grafica)
        escala_y = maximo if maximo > 0 else 1.0

        for division in range(5):
            proporcion = division / 4
            y = margen_superior + alto_grafica * (1 - proporcion)
            valor = escala_y * proporcion
            lienzo.create_line(
                margen_izquierdo,
                y,
                ancho - margen_derecho,
                y,
                fill="#d9d9d9",
            )
            lienzo.create_text(
                margen_izquierdo - 8,
                y,
                text=f"{valor:.3g}",
                anchor="e",
                fill=COLOR_TEXTO,
                font=(FUENTE, 8),
            )

        puntos = []
        total = len(self._datos_grafica)
        for indice, distancia in enumerate(self._datos_grafica):
            proporcion_x = indice / (total - 1) if total > 1 else 0.5
            x = margen_izquierdo + ancho_grafica * proporcion_x
            y = margen_superior + alto_grafica * (1 - distancia / escala_y)
            puntos.extend((x, y))

        if len(puntos) >= 4:
            lienzo.create_line(*puntos, fill=COLOR_TEXTO, width=2)
        for indice in range(0, len(puntos), 2):
            x, y = puntos[indice], puntos[indice + 1]
            lienzo.create_oval(x - 2, y - 2, x + 2, y + 2, fill=COLOR_TEXTO, outline="")

        lienzo.create_line(
            margen_izquierdo,
            margen_superior,
            margen_izquierdo,
            margen_superior + alto_grafica,
            fill=COLOR_TEXTO,
        )
        lienzo.create_line(
            margen_izquierdo,
            margen_superior + alto_grafica,
            ancho - margen_derecho,
            margen_superior + alto_grafica,
            fill=COLOR_TEXTO,
        )
        lienzo.create_text(
            margen_izquierdo,
            alto - 16,
            text="1",
            anchor="n",
            fill=COLOR_TEXTO,
            font=(FUENTE, 8),
        )
        lienzo.create_text(
            ancho - margen_derecho,
            alto - 16,
            text=str(total),
            anchor="ne",
            fill=COLOR_TEXTO,
            font=(FUENTE, 8),
        )
        lienzo.create_text(
            margen_izquierdo + ancho_grafica / 2,
            alto - 2,
            text="Número de caminata",
            anchor="s",
            fill=COLOR_TEXTO,
            font=(FUENTE, 8),
        )
        lienzo.create_text(
            12,
            margen_superior + alto_grafica / 2,
            text="Distancia máxima",
            angle=90,
            fill=COLOR_TEXTO,
            font=(FUENTE, 8),
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
