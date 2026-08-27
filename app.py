from flask import Flask, render_template

app = Flask(__name__)

# Banco de dados central da Liga da Resenha
LIGA_DADOS = {
    "campeonato": "Liga da Resenha",
    "formato": "Fase de grupos em turno único + Final em jogo único",
    "calendario": [
        {"id": 1, "rodada": "1ª Rodada", "data": "12/09/2026", "horario": "18:00 - 20:00", "mandante": "Casados F.C", "visitante": "Atlético Jóquei", "odd_casa": 1.85, "odd_empate": 3.40, "odd_fora": 2.10},
        {"id": 2, "rodada": "1ª Rodada", "data": "12/09/2026", "horario": "20:00 - 22:00", "mandante": "WCMT F.C", "visitante": "Clube Desportivo Panteras", "odd_casa": 1.90, "odd_empate": 3.30, "odd_fora": 2.00},
        {"id": 3, "rodada": "2ª Rodada", "data": "26/09/2026", "horario": "18:00 - 20:00", "mandante": "Casados F.C", "visitante": "WCMT F.C", "odd_casa": 2.20, "odd_empate": 3.20, "odd_fora": 1.75},
        {"id": 4, "rodada": "2ª Rodada", "data": "26/09/2026", "horario": "20:00 - 22:00", "mandante": "Atlético Jóquei", "visitante": "Clube Desportivo Panteras", "odd_casa": 2.05, "odd_empate": 3.10, "odd_fora": 1.80},
        {"id": 5, "rodada": "3ª Rodada", "data": "10/10/2026", "horario": "18:00 - 20:00", "mandante": "Casados F.C", "visitante": "Clube Desportivo Panteras", "odd_casa": 1.95, "odd_empate": 3.25, "odd_fora": 1.95},
        {"id": 6, "rodada": "3ª Rodada", "data": "10/10/2026", "horario": "20:00 - 22:00", "mandante": "Atlético Jóquei", "visitante": "WCMT F.C", "odd_casa": 2.15, "odd_empate": 3.30, "odd_fora": 1.70},
        {"id": 7, "rodada": "Grande Final", "data": "31/10/2026", "horario": "18:00 - 20:00", "mandante": "1º Colocado da Fase", "visitante": "2º Colocado da Fase", "odd_casa": 1.80, "odd_empate": 3.50, "odd_fora": 1.90}
    ],
    "mercados_especiais": [
        {"mercado": "Total de Gols", "opcoes": ["Mais de 2.5 (1.75)", "Menos de 2.5 (2.00)"]},
        {"mercado": "Cartões Amarelos/Vermelhos", "opcoes": ["Mais de 3.5 cartões (1.80)", "Menos de 3.5 cartões (1.90)"]},
        {"mercado": "Escanteios", "opcoes": ["Mais de 8.5 escanteios (1.85)", "Menos de 8.5 escanteios (1.85)"]}
    ],
    "elencos": {
        "Casados F.C": [
            {"nome": "Elenco em cadastro", "numero": "-", "posicao": "Geral"}
        ],
        "Atlético Jóquei": [
            {"nome": "Elenco em cadastro", "numero": "-", "posicao": "Geral"}
        ],
        "WCMT F.C": [
            {"nome": "Paulo", "numero": 7, "posicao": "Armador, central"},
            {"nome": "Warllyson", "numero": 14, "posicao": "MEI, central, armador"},
            {"nome": "Ryan", "numero": 73, "posicao": "Saga, Fixo"},
            {"nome": "Euner", "numero": 12, "posicao": "Armador/Central"},
            {"nome": "Jonathan", "numero": 23, "posicao": "Goleiro"},
            {"nome": "Queiroz", "numero": 9, "posicao": "Armador/Meia"},
            {"nome": "Hugo F.", "numero": 5, "posicao": "Zagueiro/Fixo"},
            {"nome": "Nicolas", "numero": 8, "posicao": "Fixo/Zagueiro"},
            {"nome": "Anderson", "numero": 69, "posicao": "Ala"},
            {"nome": "Regino", "numero": 11, "posicao": "Ala/Atacante"},
            {"nome": "Ronaldo", "numero": 21, "posicao": "Zagueiro/Fixo"},
            {"nome": "Patrick", "numero": 17, "posicao": "Ala/Pivô"}
        ],
        "Clube Desportivo Panteras": [
            {"nome": "Fernando", "numero": 9, "posicao": "Ala, Pivô, meio"},
            {"nome": "Leal", "numero": 18, "posicao": "Ala, Pivô"},
            {"nome": "GLM", "numero": 10, "posicao": "Pivô, Zaga, meio"},
            {"nome": "William", "numero": 8, "posicao": "Ala, Zaga, meio"},
            {"nome": "Felipe", "numero": 21, "posicao": "Ala, pivô e zaga"},
            {"nome": "Marcelo", "numero": 13, "posicao": "Zaga e ala"},
            {"nome": "Leão", "numero": 4, "posicao": "Ala"},
            {"nome": "War", "numero": 67, "posicao": "Zaga, meio"},
            {"nome": "Pedro Constrol", "numero": 5, "posicao": "Zaga, meio"},
            {"nome": "Lucas", "numero": 7, "posicao": "Meio"},
            {"nome": "Nivaldo", "numero": 11, "posicao": "Pivô"},
            {"nome": "Greg", "numero": 31, "posicao": "Goleiro"}
        ]
    }
}

@app.route('/')
def index():
    return render_template('index.html', liga=LIGA_DADOS, aba_ativa='partidas')

@app.route('/apostas')
def apostas():
    return render_template('index.html', liga=LIGA_DADOS, aba_ativa='apostas')

@app.route('/elencos')
def elencos():
    return render_template('index.html', liga=LIGA_DADOS, aba_ativa='elencos')

if __name__ == '__main__':
    app.run(debug=True)