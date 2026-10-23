#include "sistema.h"

#include <algorithm>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <vector>

using namespace std;

Sistema::Sistema(int dimensiones, int n, int numPasos) {
    this->dimensiones = dimensiones;
    this->n = n;
    this->numPasos = numPasos;

    random_device rd;
    generador = mt19937(rd());
}

void Sistema::setDimensiones(int dim) {
    if (dim < 1) {
        cout << "La dimension debe ser al menos 1" << endl;
        return;
    }
    dimensiones = dim;
}

void Sistema::setNumPasos(int pasos) {
    if (pasos < 1) {
        cout << "El numero de pasos debe ser al menos 1" << endl;
        return;
    }
    numPasos = pasos;
}

void Sistema::setRepeticiones(int n_rep) {
    if (n_rep < 1) {
        cout << "El numero de repeticiones debe ser al menos 1" << endl;
        return;
    }
    n = n_rep;
}

const vector<double>& Sistema::getDistanciasMaximas() const {
    return distanciaMax;
}

const vector<double>& Sistema::getTiemposCaminataUs() const {
    return tiempoCaminataUs;
}

void Sistema::correrExperimento() {
    distanciaMax.clear();
    distanciaMax.reserve(n);
    tiempoCaminataUs.clear();
    tiempoCaminataUs.reserve(n);
    mt19937 genParticula(generador());
    Particula particula(dimensiones, genParticula);

    for (int i = 0; i < n; i++) {
        const auto inicio = chrono::steady_clock::now();
        particula.regresarPosicionInicial();
        double maxima = 0.0;

        for (int paso = 0; paso < numPasos; paso++) {
            particula.moverUnPaso();
            double distancia = particula.calcularDistanciaEuclidiana();
            if (distancia > maxima) {
                maxima = distancia;
            }
        }
        const auto fin = chrono::steady_clock::now();
        distanciaMax.push_back(maxima);
        tiempoCaminataUs.push_back(
            chrono::duration<double, micro>(fin - inicio).count()
        );
    }
}

void Sistema::imprimirResultados(double tiempo) {
    if (distanciaMax.empty()) {
        cout << "No hay resultados. Corre primero el experimento." << endl;
        return;
    }

    double suma = accumulate(distanciaMax.begin(), distanciaMax.end(), 0.0);
    double promedio = suma / distanciaMax.size();
    double minimo = *min_element(distanciaMax.begin(), distanciaMax.end());
    double maximo = *max_element(distanciaMax.begin(), distanciaMax.end());

    cout << fixed << setprecision(4);
    cout << "\n===== RESULTADOS =====" << endl;
    cout << "Dimensiones:                  " << dimensiones << endl;
    cout << "Pasos por caminata:           " << numPasos << endl;
    cout << "Repeticiones (caminatas):     " << n << endl;
    cout << "Promedio de distancia maxima: " << promedio << endl;
    cout << "Distancia maxima minima:      " << minimo << endl;
    cout << "Distancia maxima maxima:      " << maximo << endl;
    cout << "Tiempo de ejecucion:          " << tiempo << " s" << endl;

    ofstream archivo("distancias_maximas.csv");
    if (!archivo) {
        cerr << "No se pudo crear distancias_maximas.csv" << endl;
        return;
    }
    archivo << "# dimensiones = " << dimensiones
            << ", pasos = " << numPasos
            << ", repeticiones = " << n
            << ", tiempo_s = " << tiempo << endl;

    archivo << "caminata,distancia_maxima,tiempo_us" << endl;
    for (size_t i = 0; i < distanciaMax.size(); i++) {
        archivo << (i + 1) << "," << distanciaMax[i] << ","
                << tiempoCaminataUs[i] << endl;
    }
    archivo.close();
    cout << "Distancias maximas guardadas en distancias_maximas.csv" << endl;
}


void Sistema::crearTablaPruebas() {
    int dimOriginal = dimensiones;
    int pasosOriginal = numPasos;
    int repOriginal = n;
    vector<double> resultadosOriginales = distanciaMax;

    int dims[] = {1, 2};
    int pasos[] = {100, 1000, 10000};
    int reps[] = {100, 1000, 10000};

    ofstream archivo("tabla_resultados.csv");
    if (!archivo.is_open()) {
        cout << "No se pudo crear tabla_resultados.csv" << endl;
        return;
    }
    archivo << "dimensiones,pasos,repeticiones,promedio_distancia_maxima,tiempo_s\n";

    cout << "TABLA DE PRUEBAS: " << endl;
    cout << left << setw(6) << "Dim" << setw(8) << "Pasos" << setw(8) << "Rep"
         << setw(18) << "Prom. dist. max" << setw(12) << "Tiempo (s)" << endl;
    cout << string(52, '-') << endl;

    for (int d : dims) {
        for (int p : pasos) {
            for (int r : reps) {
                dimensiones = d;
                numPasos = p;
                n = r;

                auto inicio = chrono::high_resolution_clock::now();
                correrExperimento();
                auto fin = chrono::high_resolution_clock::now();
                double tiempo = chrono::duration<double>(fin - inicio).count();

                double promedio = accumulate(distanciaMax.begin(), distanciaMax.end(), 0.0)
                                  / distanciaMax.size();

                archivo << d << "," << p << "," << r << ","
                        << fixed << setprecision(4) << promedio << ","
                        << setprecision(6) << tiempo << "\n";

                cout << left << setw(6) << d << setw(8) << p << setw(8) << r
                     << fixed << setprecision(4) << setw(18) << promedio
                     << setprecision(6) << setw(12) << tiempo << endl;
            }
        }
    }
    archivo.close();
    cout << endl << "Tabla guardada en tabla_resultados.csv" << endl;

    dimensiones = dimOriginal;
    numPasos = pasosOriginal;
    n = repOriginal;
    distanciaMax = resultadosOriginales;
}
