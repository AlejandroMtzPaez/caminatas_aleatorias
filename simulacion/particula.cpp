#include "particula.h"
using namespace std;
#include <iostream>
#include <cmath>

Particula::Particula(int dim, std::mt19937 gen) {
    dimension = dim;
    generador = gen;
}

void Particula::moverUnPaso() {
    uniform_int_distribution<int> distribucion(0, 2*dimension-1);
    int seleccion = distribucion(generador);

    int eje = seleccion/2;
    //int direccion = opcion *2



}

double Particula::calcularDistanciaEuclidiana() {
    return sqrt(x * x + y * y);
}

void Particula::regresarPosicionInicial() {
    x = 0;
    y = 0;
}

int Particula::getX() const {
    return x;
}

int Particula::getY() const {
    return y;
}
