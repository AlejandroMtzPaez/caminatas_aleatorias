#ifndef PARTICULA_H
#define PARTICULA_H

#include <iostream>
#include <random>

class Particula{
    private: // atributos privados
        vector<int> coordenadas;
        int dimension;
        std::mt19937 generador;

    public: // atributos publicos
        Particula(int dim, std::mt19937 gen);

        void moverUnPaso();
        double calcularDistanciaEuclidiana();
        void regresarPosicionInicial();

        // getters para posiciones
        vector<int> getPosicion() const;

};

#endif 
