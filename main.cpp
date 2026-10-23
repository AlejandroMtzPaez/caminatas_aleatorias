#include <iostream>
#include "simulacion/sistema.h"
using namespace std;

#include <chrono>

void menu(){
    cout << "\n- SIMULADOR: CAMINATA ALEATORIA -\n";
    cout << "1. Personalizar parámetros.\n";
    cout << "2. Generar tabla.\n";
    cout << "3. Salir.\n";
    cout << "Seleccione una opcion: ";
}

int main(){
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
