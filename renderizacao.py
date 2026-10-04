import sys
import csv
import os
import matplotlib.pyplot as plt
import math
import random

### ENTRADA ###

#Extensões dos métodos e etiqueta do gráfico
saidas = {
    "Média simples (alturas)": "media_simples_alturas",
    "Média simples (durações)": "media_simples_duracoes",
    "Média simples (som e silêncio)": "media_simples_som_e_silencio",
    "Média ponderada (alturas por durações)": "media_ponderada_alturas_por_duracao",
    "Desvio padrão (alturas)": "desvio_padrao_alturas",
    "Desvio padrão (durações)": "desvio_padrao_duracoes"
}

rotulos_y = {
    "Média simples (alturas)": "Altura MIDI",
    "Média simples (durações)": "Segundos",
    "Média simples (som e silêncio)": "Atividade sonora",
    "Média ponderada (alturas por durações)": "Altura MIDI",
    "Desvio padrão (alturas)": "Desvio padrão (MIDI)",
    "Desvio padrão (durações)": "Desvio padrão (segundos)"
}

# Leitura do arquivo CSV
def ler_dados_csv(metodo):

    dados_dicionario = {}
    analise = f"dados/results/{id_obra}_{saidas[metodo]}.csv"

    if not os.path.exists(analise):
        print(f"ERRO: A análise do método {metodo} não existe no banco de dados")
        sys.exit(2)

    with open(analise, mode="r", encoding="utf-8") as arq_csv:
        reader = csv.DictReader(arq_csv)

        for header in reader.fieldnames:
            dados_dicionario[header] = []

        for linha in reader:
            for header in reader.fieldnames:
                dados_dicionario[header].append(linha[header])

    return dados_dicionario


def definir_titulo(metodo):
    
    titulo = input(f'\nDigite o título do gráfico "{metodo}" da obra ID {id_obra}\n>>>')
    return titulo

### GRAFOS ###

#Representação do eixo x
def gerar_eixo_x(duracoes, eixo):

    tipo, label_x = eixo.split(",", 1)

    if tipo == "segundos":
        
        #Acumulador temporal de amostras
        eixo_x = []
        tempo = 0.0

        for duracao in duracoes:
            eixo_x.append(tempo)
            tempo += duracao

    elif tipo == "indice":

        eixo_x = list(range(len(duracoes)))

    return eixo_x, label_x

#Gráfico simples
def plotar_analise_simples(metodo, eixo):

    dados = ler_dados_csv(metodo)

    header_saida = saidas[metodo]

    duracoes = [float(valor) for valor in dados["amos_dur_sec"]]
    valores = [
        float("nan") if float(valor) == -1 else float(valor)
        for valor in dados[header_saida]
        ]

    eixo_x, label_x = gerar_eixo_x(duracoes, eixo)

    #Geração gráfica
    plt.figure(figsize=(10, 3.5))

    plt.plot(
        eixo_x,
        valores,
        marker="o",
        color="black",
        label=metodo
    )

    plt.xlabel(label_x)
    plt.ylabel(rotulos_y[metodo])
    
    #Título do gráfico
    titulo = definir_titulo(metodo)
    plt.title(
        titulo,
        loc="left",
        fontsize=12,
        fontweight="normal",
        pad=10
        )
    plt.legend(fontsize=8, markerscale=0.8)
    
    plt.grid(
        axis="both",
        linestyle=":",
        linewidth=1.0,
        color="black",
        alpha=0.32
        ) 
    
    plt.tight_layout()
    plt.rcParams["savefig.dpi"] = 300
    plt.show()

#Gráfico composto
def plotar_analise_composto(metodos, eixo):

    #Gera cores aleatórias depois das primeiras
    cores = ["blue", "red", "black", "grey"]
    while len(cores) < len(metodos):
        cor = (
            random.random(),
            random.random(),
            random.random()
        )

        if cor not in cores:
            cores.append(cor)

    #Carrega as séries
    series = []
    label_x = None

    for metodo in metodos:

        dados = ler_dados_csv(metodo)
        header_saida = saidas[metodo]

        duracoes = [float(valor) for valor in dados["amos_dur_sec"]]
        valores = [
            float("nan") if float(valor) == -1 else float(valor)
            for valor in dados[header_saida]
        ]

        eixo_x, label_x = gerar_eixo_x(duracoes, eixo)

        series.append({
            "metodo": metodo,
            "eixo_x": eixo_x,
            "valores": valores,
            "label_y": rotulos_y[metodo]
        })

    #Agrupa por grandeza
    grupos = {}
    for serie in series:
        grupos.setdefault(serie["label_y"], []).append(serie)

    mesma_grandeza = len(grupos) == 1

    #Decide a escala de cada série
    if mesma_grandeza:
        # Escala natural compartilhada: nenhum reescalonamento
        for serie in series:
            serie["valores_plot"] = serie["valores"]
        label_y_final = series[0]["label_y"]
    else:
        # Normalização geométrica por grupo a 0–1
        for membros in grupos.values():

            validos = [
                v for serie in membros
                for v in serie["valores"]
                if not math.isnan(v)
            ]

            if not validos:
                for serie in membros:
                    serie["valores_plot"] = list(serie["valores"])
                continue

            valor_minimo = min(validos)
            valor_maximo = max(validos)

            for serie in membros:
                if valor_maximo == valor_minimo:
                    #Série constante: posição neutra 0.5
                    serie["valores_plot"] = [
                        0.5 if not math.isnan(valor) else float("nan")
                        for valor in serie["valores"]
                    ]
                else:
                    serie["valores_plot"] = [
                        (valor - valor_minimo) /
                        (valor_maximo - valor_minimo)
                        if not math.isnan(valor) else float("nan")
                        for valor in serie["valores"]
                    ]

        label_y_final = "Escala geométrica normalizada (0–1)"

    #Plotagem
    plt.figure(figsize=(10, 3.5))

    for indice, serie in enumerate(series):

        plt.plot(
            serie["eixo_x"],
            serie["valores_plot"],
            marker="o",
            color=cores[indice],
            label=serie["metodo"]
        )

    plt.xlabel(label_x)
    plt.ylabel(label_y_final)

    #Título do gráfico
    titulo = definir_titulo(metodos)
    plt.title(
        titulo,
        loc="left",
        fontsize=12,
        fontweight="normal",
        pad=10
        )

    if len(metodos) == 2:
        plt.legend(fontsize=7)
    else:
        plt.legend(fontsize=6, markerscale=0.6)

    plt.grid(
        axis="both",
        linestyle=":",
        linewidth=1.0,
        color="black",
        alpha=0.32
    )

    plt.tight_layout()
    plt.rcParams["savefig.dpi"] = 300
    plt.show()
        
if __name__ == "__main__":

    # Argumentos de entrada
    if len(sys.argv) < 5:
        print(
            "Uso: python3 renderizacao.py <id_obra> <simples|composto> <metodos> <eixo>\n"
            "Sintaxe de <metodos>: metodo1,metodo2,metodo3,etc\n"
            "Sintaxe de <eixo>: segundos,label|indice,label"
        )
        sys.exit(1)

    # ID da obra e tipo de grafo
    id_obra = sys.argv[1]
    tipo_grafo = sys.argv[2]

    # Converte métodos para lista
    metodos_entrada = sys.argv[3]
    metodos_nomes = metodos_entrada.split(',')
    
    # Definição do eixo X
    eixo = sys.argv[4]

    if tipo_grafo == "simples":
        for metodo in metodos_nomes:
            plotar_analise_simples(metodo, eixo)
            
    elif tipo_grafo == "composto" and len(metodos_nomes) == 1:
        plotar_analise_simples(metodos_nomes[0], eixo)

    elif tipo_grafo == "composto":
        plotar_analise_composto(metodos_nomes, eixo)

    else:
        print(
            f"ERRO: Tipo de gráfico '{tipo_grafo}' inválido.\n"
            "Use 'simples' ou 'composto'."
        )
        sys.exit(3)
