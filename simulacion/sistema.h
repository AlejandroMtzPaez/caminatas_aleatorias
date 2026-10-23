#ifndef SISTEMA_H
#define SISTEMA_H
#include <iostream>
#include <random>
#include <vector>

#include "particula.h"


class Sistema {
    private:
        int dimensiones;
        int n; //cantidad de repeticiones del experimento
        int numPasos; //cantidad de pasos que da la particula
        std::mt19937 generador; // generador de numeros aleatorios
        std::vector<double> distanciaMax;
        std::vector<double> tiempoCaminataUs;

    public:
        Sistema(int dimensiones, int n, int numPasos);

        void correrExperimento();
        void imprimirResultados(double tiempo);

        void crearTablaPruebas();

        // setters para poder modificarlo a través de la interfaz
        void setDimensiones(int dim);
        void setNumPasos(int pasos);
        void setRepeticiones(int n_rep);

        const std::vector<double>& getDistanciasMaximas() const;
        const std::vector<double>& getTiemposCaminataUs() const;
};

#endif