#ifndef PARTICULA_H
#define PARTICULA_H

#include <iostream>
#include <random>
#include <vector>

class Particula{
    private: // atributos privados
        std::vector<int> coordenadas;
        int dimension;
        std::mt19937 generador;

    public: // atributos publicos
        Particula(int dim, std::mt19937 gen);

        void moverUnPaso();
        double calcularDistanciaEuclidiana();
        void regresarPosicionInicial();

        // getters para posiciones
        std::vector<int> getPosicion() const;

};

#endif 
