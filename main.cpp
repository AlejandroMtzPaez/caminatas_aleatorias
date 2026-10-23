#include <iostream>
#include "simulacion/sistema.h"
using namespace std;

#include <chrono>
#include <charconv>
#include <fstream>
#include <iomanip>
#include <string_view>

namespace {
bool leerEnteroPositivo(const char* texto, int& valor) {
    const string_view entrada(texto);
    const auto resultado = from_chars(
        entrada.data(),
        entrada.data() + entrada.size(),
        valor
    );
    return resultado.ec == errc{} &&
           resultado.ptr == entrada.data() + entrada.size() &&
           valor > 0;
}
}

void menu(){
    cout << "\n- SIMULADOR: CAMINATA ALEATORIA -\n";
    cout << "1. Personalizar parámetros.\n";
    cout << "2. Generar tabla.\n";
    cout << "3. Salir.\n";
    cout << "Seleccione una opcion: ";
}

int main(int argc, char* argv[]){
    if (argc > 1 && string_view(argv[1]) == "--multiple") {
        int dimensiones;
        int pasos[3];
        int repeticiones[3];
        if (argc != 9 || !leerEnteroPositivo(argv[2], dimensiones)) {
            cerr << "Uso: caminata_backend.exe --multiple DIM P1 P2 P3 R1 R2 R3\n";
            return 2;
        }
        for (int i = 0; i < 3; i++) {
            if (!leerEnteroPositivo(argv[3 + i], pasos[i]) ||
                !leerEnteroPositivo(argv[6 + i], repeticiones[i])) {
                cerr << "Los pasos y las repeticiones deben ser enteros positivos.\n";
                return 2;
            }
        }
        for (int i = 0; i < 3; i++) {
            for (int j = i + 1; j < 3; j++) {
                if (pasos[i] == pasos[j] || repeticiones[i] == repeticiones[j]) {
                    cerr << "Los valores de pasos y repeticiones deben ser distintos.\n";
                    return 2;
                }
            }
        }

        ofstream archivo("simulaciones_multiples.csv", ios::trunc);
        if (!archivo) {
            cerr << "No se pudo crear simulaciones_multiples.csv\n";
            return 3;
        }
        archivo << "pasos,repeticiones,promedio_distancia_maxima,tiempo_s\n";
        archivo << fixed << setprecision(10);

        const auto inicioTotal = chrono::steady_clock::now();
        double sumaPonderada = 0.0;
        long long totalCaminatas = 0;
        for (int numPasos : pasos) {
            for (int n : repeticiones) {
                Sistema sim(dimensiones, n, numPasos);
                const auto inicio = chrono::steady_clock::now();
                sim.correrExperimento();
                const auto fin = chrono::steady_clock::now();
                const double tiempo = chrono::duration<double>(fin - inicio).count();
                const vector<double>& distancias = sim.getDistanciasMaximas();
                double sumaDistancias = 0.0;
                for (double distancia : distancias) {
                    sumaDistancias += distancia;
                }
                const double promedio = sumaDistancias / distancias.size();
                archivo << numPasos << "," << n << "," << promedio << "," << tiempo << "\n";
                sumaPonderada += sumaDistancias;
                totalCaminatas += n;
            }
        }
        const auto finTotal = chrono::steady_clock::now();
        archivo.close();
        if (!archivo) {
            cerr << "No se pudo completar simulaciones_multiples.csv\n";
            return 3;
        }

        const double tiempoTotal = chrono::duration<double>(
            finTotal - inicioTotal
        ).count();
        cout << fixed << setprecision(10);
        cout << "PROMEDIO_GENERAL,"
             << sumaPonderada / static_cast<double>(totalCaminatas) << "\n";
        cout << "TIEMPO_TOTAL_SEGUNDOS," << tiempoTotal << "\n";
        return 0;
    }

    if (argc > 1) {
        int dimensiones;
        int pasos;
        int repeticiones;

        if (argc != 5 || string_view(argv[1]) != "--gui" ||
            !leerEnteroPositivo(argv[2], dimensiones) ||
            !leerEnteroPositivo(argv[3], pasos) ||
            !leerEnteroPositivo(argv[4], repeticiones)) {
            cerr << "Uso: caminata_backend.exe --gui DIMENSION PASOS REPETICIONES\n";
            return 2;
        }

        Sistema sim(dimensiones, repeticiones, pasos);
        const auto inicio = chrono::high_resolution_clock::now();
        sim.correrExperimento();
        const auto fin = chrono::high_resolution_clock::now();
        const double tiempoTotal = chrono::duration<double>(fin - inicio).count();

        ofstream archivo("distancias_maximas.csv", ios::trunc);
        if (!archivo) {
            cerr << "No se pudo crear distancias_maximas.csv\n";
            return 3;
        }
        archivo << "caminata,distancia_maxima,tiempo_us\n";
        archivo << fixed << setprecision(10);
        const vector<double>& distancias = sim.getDistanciasMaximas();
        const vector<double>& tiempos = sim.getTiemposCaminataUs();
        for (size_t i = 0; i < distancias.size(); i++) {
            archivo << (i + 1) << "," << distancias[i] << "," << tiempos[i] << "\n";
        }
        archivo.close();
        if (!archivo) {
            cerr << "No se pudo completar distancias_maximas.csv\n";
            return 3;
        }

        cout << fixed << setprecision(10);
        cout << "TIEMPO_SEGUNDOS," << tiempoTotal << "\n";
        return 0;
    }

    int opcion;

    Sistema sim(1,1,1);

    do{
        menu();
        cin>> opcion;

        if (opcion == 1){
            int dim;
            int pasos;
            int repeticiones;

            cout << "\nIngrese la dimension del sistema (ej. 1, 2, 3...): ";
            cin >> dim;
            cout << "Ingrese el numero de pasos por caminata: ";
            cin >> pasos;
            cout << "Ingrese el numero de repeticiones (n): ";
            cin >> repeticiones;

            sim.setDimensiones(dim);
            sim.setNumPasos(pasos);
            sim.setRepeticiones(repeticiones);

            auto inicio = chrono::high_resolution_clock::now();
            sim.correrExperimento();
            auto fin = chrono::high_resolution_clock::now();

            double tiempoTotal = chrono::duration<double>(fin - inicio).count();
            sim.imprimirResultados(tiempoTotal);

        } else if (opcion == 2) {
            cout << "\nEjecutando bateria de pruebas para 1D y 2D...\n";
            sim.crearTablaPruebas();

        } else if (opcion != 3) {
            cout << "Opcion no valida. Intente de nuevo.\n";
        }

    } while (opcion != 3);

    cout << "Cerrando menu...";
    return 0;
}
