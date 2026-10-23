# Caminatas aleatorias

Simulador de caminatas aleatorias con backend en C++ e interfaz gráfica en Python/Tkinter.

## Ejecutar desde el código fuente

1. Instala Python 3 con Tkinter, un compilador MinGW-w64 que incluya `g++` y PyInstaller:

   ```powershell
   python -m pip install pyinstaller
   ```

2. Desde la raíz del proyecto, compila el backend:

   ```powershell
   New-Item -ItemType Directory -Force build
   g++ -std=c++17 -O2 main.cpp simulacion\sistema.cpp simulacion\particula.cpp -o build\caminata_backend.exe
   ```

3. Inicia la interfaz:

   ```powershell
   python interfaz.py
   ```

## Generar el ejecutable

En Windows, ejecuta desde la raíz del proyecto:

```powershell
.\build.ps1
```

El script compila el backend y lo incluye con la interfaz en un ejecutable autónomo:

```text
dist\CaminataAleatoria.exe
```

La distribución no necesita Python instalado. Para compilar, sí requiere `g++`, Python con Tkinter y PyInstaller. Los parámetros son enteros positivos. La fuente de la interfaz es Arial.

La pestaña **Simulación individual** presenta una tabla con la distancia máxima y el tiempo individual en microsegundos de cada caminata, además de una gráfica de distancias máximas y el tiempo total del experimento. Cada ejecución reescribe `CaminatasAleatorias\distancias_maximas.csv` dentro de la carpeta del usuario.

La pestaña **Simulaciones múltiples** ejecuta las nueve combinaciones de tres valores de pasos y tres valores de repeticiones. Los valores predeterminados para ambos grupos son 100, 1000 y 10000. La tabla muestra el promedio de distancia máxima y el tiempo de cada combinación; debajo se presenta el promedio general ponderado por el total de caminatas y el tiempo total. El CSV `CaminatasAleatorias\simulaciones_multiples.csv` se sobrescribe en cada ejecución múltiple.
