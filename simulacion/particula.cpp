#include "particula.h"
using namespace std;
#include <iostream>
#include <cmath>

Particula::Particula(int dim, std::mt19937 gen) {
    dimension = dim;
    generador = gen;
    // empieza en el origen
    coordenadas.assign(dimension, 0);
}

void Particula::moverUnPaso() {
    uniform_int_distribution<int> distribucion(0, 2*dimension-1);
    int seleccion = distribucion(generador);

    // decide el eje y la dirección en el que se va a mover
    int eje = seleccion/2;
    int direccion = seleccion % 2;

    if (direccion == 0){
        coordenadas[eje] = coordenadas[eje] + 1;
    } else {
        coordenadas[eje] = coordenadas[eje] - 1;
    }
}

double Particula::calcularDistanciaEuclidiana() {
    double sumaCuadrados = 0.0;
    //sumatoria con for para los valores de cada coordenada
    for (int val : coordenadas){
        sumaCuadrados += val*val;
    }
    return sqrt(sumaCuadrados);
}

void Particula::regresarPosicionInicial() {
    coordenadas.assign(dimension, 0);
}

vector<int> Particula::getPosicion() const {
    return coordenadas;
}
