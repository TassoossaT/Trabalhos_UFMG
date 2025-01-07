#ifndef PACIENT_HPP
#define PACIENT_HPP

class Pacient
{
private:
    int id;
    bool alta;
    int ano, mes, dia, hora;
    int medidasHospitalares;
    int testesLaboratorio;
    int examesImagem;
    int instrumentosMedicamentos;
    int estadoAtual;
    int tempoOcioso;
    int tempoAtendido;

public:
    int grauUrgencia;
    Pacient(int id, bool alta, int ano, int mes, int dia, int hora, int grauUrgencia, int medidasHospitalares, int testesLaboratorio, int examesImagem, int instrumentosMedicamentos);
    
    // Getters and setters for each attribute
    int getId() const;
    bool getAlta() const;
    int getAno() const;
    int getMes() const;
    int getDia() const;
    int getHora() const;
    int getGrauUrgencia() const;
    int getMedidasHospitalares() const;
    int getTestesLaboratorio() const;
    int getExamesImagem() const;
    int getInstrumentosMedicamentos() const;
    int getEstadoAtual() const;
    int getTempoOcioso() const;
    int getTempoAtendido() const;
    int getAdmissionDate() const;

    void setId(int id);
    void setAlta(bool alta);
    void setAno(int ano);
    void setMes(int mes);
    void setDia(int dia);
    void setHora(int hora);
    void setGrauUrgencia(int grauUrgencia);
    void setMedidasHospitalares(int medidasHospitalares);
    void setTestesLaboratorio(int testesLaboratorio);
    void setExamesImagem(int examesImagem);
    void setInstrumentosMedicamentos(int instrumentosMedicamentos);
    void setEstadoAtual(int estadoAtual);
    void setTempoOcioso(int tempoOcioso);
    void setTempoAtendido(int tempoAtendido);

    // Methods to update the state and statistics
    void updateEstado(int novoEstado);
    void addTempoOcioso(int tempo);
    void addTempoAtendido(int tempo);
};

#endif // PACIENT_HPP