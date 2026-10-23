#ifndef SISTEMA_H
#define SISTEMA_H
#include <iostream>

#include "particula.h"
#include <vector>

using namespace std;


class Sistema {
    private:
        int dimensiones;
        int n; //cantidad de repeticiones del experimento
        int numPasos; //cantidad de pasos que da la particula
        mt19937 generador; // generador de numeros aleatorios
        vector<double> distanciaMax;

    public:
        Sistema(int dimensiones, int n, int numPasos);

        void correrExperimento();
        void imprimirResultados(double tiempo);

        void crearTablaPruebas();

        // setters para poder modificarlo a través de la interfaz
        void setDimensiones(int dim);
        void setNumPasos(int pasos);
        void setRepeticiones(int n_rep);



};

#endif