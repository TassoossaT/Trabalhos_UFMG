#include "pacient.hpp"

Pacient::Pacient(int id, bool alta, int ano, int mes, int dia, int hora, int grauUrgencia, int medidasHospitalares, int testesLaboratorio, int examesImagem, int instrumentosMedicamentos)
    : id(id), alta(alta), ano(ano), mes(mes), dia(dia), hora(hora), grauUrgencia(grauUrgencia), medidasHospitalares(medidasHospitalares), testesLaboratorio(testesLaboratorio), examesImagem(examesImagem), instrumentosMedicamentos(instrumentosMedicamentos), estadoAtual(1), tempoOcioso(0), tempoAtendido(0) {}

int Pacient::getId() const { return id; }
bool Pacient::getAlta() const { return alta; }
int Pacient::getAno() const { return ano; }
int Pacient::getMes() const { return mes; }
int Pacient::getDia() const { return dia; }
int Pacient::getHora() const { return hora; }
int Pacient::getGrauUrgencia() const { return grauUrgencia; }
int Pacient::getMedidasHospitalares() const { return medidasHospitalares; }
int Pacient::getTestesLaboratorio() const { return testesLaboratorio; }
int Pacient::getExamesImagem() const { return examesImagem; }
int Pacient::getInstrumentosMedicamentos() const { return instrumentosMedicamentos; }
int Pacient::getEstadoAtual() const { return estadoAtual; }
int Pacient::getTempoOcioso() const { return tempoOcioso; }
int Pacient::getTempoAtendido() const { return tempoAtendido; }

int Pacient::getAdmissionDate() const {
    return ano * 10000 + mes * 100 + dia;
}

void Pacient::setId(int id) { this->id = id; }
void Pacient::setAlta(bool alta) { this->alta = alta; }
void Pacient::setAno(int ano) { this->ano = ano; }
void Pacient::setMes(int mes) { this->mes = mes; }
void Pacient::setDia(int dia) { this->dia = dia; }
void Pacient::setHora(int hora) { this->hora = hora; }
void Pacient::setGrauUrgencia(int grauUrgencia) { this->grauUrgencia = grauUrgencia; }
void Pacient::setMedidasHospitalares(int medidasHospitalares) { this->medidasHospitalares = medidasHospitalares; }
void Pacient::setTestesLaboratorio(int testesLaboratorio) { this->testesLaboratorio = testesLaboratorio; }
void Pacient::setExamesImagem(int examesImagem) { this->examesImagem = examesImagem; }
void Pacient::setInstrumentosMedicamentos(int instrumentosMedicamentos) { this->instrumentosMedicamentos = instrumentosMedicamentos; }
void Pacient::setEstadoAtual(int estadoAtual) { this->estadoAtual = estadoAtual; }
void Pacient::setTempoOcioso(int tempoOcioso) { this->tempoOcioso = tempoOcioso; }
void Pacient::setTempoAtendido(int tempoAtendido) { this->tempoAtendido = tempoAtendido; }

void Pacient::updateEstado(int novoEstado) {this->estadoAtual = novoEstado;}

void Pacient::addTempoOcioso(int tempo) {this->tempoOcioso += tempo;}

void Pacient::addTempoAtendido(int tempo) {this->tempoAtendido += tempo;}
