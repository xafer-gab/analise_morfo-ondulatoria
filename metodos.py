import sys
import json
import os
import csv

#Leitura do arquivo CSV
def ler_dados_midi_csv(caminho_arquivo):
    dados_dicionario = {
        "nota_midi": [],
        "tempo_inicio": [],
        "duracao_segundos": [],
    }

    with open(caminho_arquivo, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for linha in reader:
            dados_dicionario["nota_midi"].append(int(linha["nota_midi"]))
            dados_dicionario["tempo_inicio"].append(float(linha["tempo_inicio"]))
            dados_dicionario["duracao_segundos"].append(float(linha["duracao_segundos"]))
    return dados_dicionario

#Particionamento do dicionário por janela temporal
def particionamento_temporal(dados, intervalo):

    # Descobre o tempo total da música para saber onde parar as janelas
    tempo_maximo = dados["tempo_inicio"][-1] + dados["duracao_segundos"][-1]
    idx_max = len(dados["duracao_segundos"])
    partes_lis = []
    inicio_janela = 0.0
    c = 0

    # Cria blocos de tempo fixos
    while inicio_janela < tempo_maximo and c < idx_max:
        fim_janela = inicio_janela + intervalo

        # Estrutura para armazenar as notas que passam por esta janela
        parte_atual = {"nota_midi": [], "duracao_segundos": []}
        amos = 0
        while amos < intervalo:
            if c >= idx_max:
                    break
            t_ini = dados["tempo_inicio"][c]
            t_fim = dados["tempo_inicio"][c] + dados["duracao_segundos"][c]

            #Garante que há evento na amostra
            if t_fim <= inicio_janela:
                c += 1
                continue
            if t_ini >= fim_janela:
                break

            #Calcula a diferença entre início e fim
            dif_inicio = t_ini - inicio_janela
            dif_fim = t_fim - fim_janela

            #Transforma em diferença de fase
            fase_inicio = dif_inicio / intervalo #0 = começo
            fase_fim = dif_fim / intervalo #0 = fim

            #Observa se está dentro da fase
            if fase_inicio < 0:
                duracao_ini = inicio_janela
            else:
                duracao_ini = t_ini
            if fase_fim > 0:
                duracao_fim = fim_janela
                acc = dif_fim
            else:
                duracao_fim = t_fim
                acc = 0
            duracao = duracao_fim - duracao_ini
            parte_atual["nota_midi"].append(dados["nota_midi"][c])
            parte_atual["duracao_segundos"].append(duracao_fim - duracao_ini)
            if acc == 0:
                c += 1
            amos += duracao

        partes_lis.append(parte_atual)
        inicio_janela = fim_janela

    return partes_lis

###########
# MÉTODOS #
###########

#Entrada: {"nota_midi": [], "duracao_segundos": []}
def retira_pausas(dados: dict): 
    saida = {"nota_midi": [], "duracao_segundos": []}
    for alt, dur in zip(dados["nota_midi"], dados["duracao_segundos"]):
        if alt != -1:
            saida["nota_midi"].append(alt)
            saida["duracao_segundos"].append(dur)
        
    return saida

### MÉDIA SIMPLES ###

#Média simples das alturas
def media_simples_alturas(dados):
    dados_sem_pausa = retira_pausas(dados)
    lista_alturas = dados_sem_pausa["nota_midi"]
    if not lista_alturas:
        return -1

    media_simples = sum(lista_alturas) / len(lista_alturas)
    return media_simples

#Média simples das durações
def media_simples_duracoes(dados):
    dados_sem_pausa = retira_pausas(dados)
    lista_duracoes = dados_sem_pausa["duracao_segundos"]
    if not lista_duracoes:
        return -1

    media_simples = sum(lista_duracoes) / len(lista_duracoes)
    return media_simples

#Média simples de som e silêncio
def media_simples_som_e_silencio(dados):
    lista_alturas = dados["nota_midi"]
    if not lista_alturas:
        return 0.0
    
    som_silencio = []
    for alt in lista_alturas:
        if alt != -1:
            som_silencio.append(1) #Som
        else:
            som_silencio.append(0) #Silêncio
    
    media_simples = sum(som_silencio) / len(som_silencio)
    return media_simples

### MÉDIA PONDERADA ###

#Pondera as alturas pela duração do evento
def media_ponderada_altura_por_duracao(dados):
    dados_sem_pausa = retira_pausas(dados)
    lista_alturas = dados_sem_pausa["nota_midi"]
    lista_duracoes = dados_sem_pausa["duracao_segundos"]

    if not lista_alturas or sum(lista_duracoes) == 0:
        return -1

    soma_ponderada = sum(
        nota * duracao for nota, duracao in zip(lista_alturas, lista_duracoes)
    )
    media_ponderada = soma_ponderada / sum(lista_duracoes)
    return media_ponderada

### VARIÂNCIA ###

#Calcula a resposta do desvio padrão populacional das alturas
def desvio_padrao_alturas(dados):
    dados_sem_pausa = retira_pausas(dados)
    lista_alturas = dados_sem_pausa["nota_midi"]
    if not lista_alturas:
        return -1

    num_elementos = len(lista_alturas)
    media = sum(lista_alturas) / num_elementos
    soma_quadrados_diferencas = sum((nota - media) ** 2 for nota in lista_alturas)
    variancia = soma_quadrados_diferencas / num_elementos
    desvio_padrao = variancia**0.5

    return desvio_padrao

#Calcula a resposta do desvio padrão populacional das durações
def desvio_padrao_duracoes(dados):
    dados_sem_pausa = retira_pausas(dados)
    lista_duracoes = dados_sem_pausa["duracao_segundos"]
    if not lista_duracoes:
        return -1

    num_elementos = len(lista_duracoes)
    media = sum(lista_duracoes) / num_elementos
    soma_quadrados_diferencas = sum((duracao - media) ** 2 for duracao in lista_duracoes)
    variancia = soma_quadrados_diferencas / num_elementos
    desvio_padrao = variancia**0.5

    return desvio_padrao


#Gravar análise no banco de dados
def gravar_analise(caminho_arquivo, calculo: list):
    cabecalhos = calculo[0]
    colunas = calculo[1]

    with open(caminho_arquivo, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        #Cabeçalhos
        writer.writerow(cabecalhos)


        #Colunas
        l_coluna = 0
        while l_coluna < len(colunas[0]):
            linha = []
            for col in colunas:
                linha.append(col[l_coluna])
            writer.writerow(linha)
            l_coluna += 1

#Variáveis 
#Método de análise
metodos = {
	"Média simples (alturas)": media_simples_alturas,
	"Média simples (durações)": media_simples_duracoes,
	"Média simples (som e silêncio)": media_simples_som_e_silencio,
	"Média ponderada (alturas por durações)": media_ponderada_altura_por_duracao,
	"Desvio padrão (alturas)": desvio_padrao_alturas,
	"Desvio padrão (durações)": desvio_padrao_duracoes
}

# Extensões de saída
saidas = {
	"Média simples (alturas)": "media_simples_alturas",
	"Média simples (durações)": "media_simples_duracoes",
	"Média simples (som e silêncio)": "media_simples_som_e_silencio",
	"Média ponderada (alturas por durações)": "media_ponderada_alturas_por_duracao",
	"Desvio padrão (alturas)": "desvio_padrao_alturas",
	"Desvio padrão (durações)": "desvio_padrao_duracoes"
}

#Execução
if __name__ == "__main__":
	
	#Argumentos de entrada
	if len(sys.argv) < 4:
		print("Uso: python3 metodos.py <id_obra> <metodo> <janela_temporal>")
		sys.exit(1)

	id_obra = sys.argv[1]
	metodo = sys.argv[2]
	janela_temporal = sys.argv[3]

	#Verifica entrada
	arq_entrada = f"dados/parsed/{id_obra}.csv"
	if not os.path.exists(arq_entrada):
		print(f"ERRO: O arquivo {arq_entrada} não existe no banco de dados")
		sys.exit(2)

	try:
		janela_temporal = float(janela_temporal)
	except:
		print("ERRO: A janela temporal deve ser segundos em float (ex. 4.0)")
		sys.exit(3)

	#Identifica saída
	arq_saida = f"dados/results/{id_obra}_{saidas[metodo]}.csv"

	try:
		print(f'\nAnálise de "{metodo}" da obra ID {id_obra}')

		dados_musicais = ler_dados_midi_csv(arq_entrada)

		# Particiona os dados em janelas temporais
		partes = particionamento_temporal(dados_musicais, janela_temporal)

		funcao_metodo = metodos[metodo]

		# Calcula a análise para cada janela
		resultados = []

		for parte in partes:
			resultados.append(funcao_metodo(parte))

		# Monta os dados para gravação
		cabecalhos = ["amos_idx", "amos_dur_sec", saidas[metodo]]
		colunas = [
			list(range(len(resultados))),
			[janela_temporal] * len(resultados),
			resultados
		]

		# Grava o resultado
		gravar_analise(arq_saida, [cabecalhos, colunas])

		print(f"--- Análise concluída: '{arq_saida}'")
		print(f"--- Janelas processadas: {len(resultados)}")

	except FileNotFoundError:
		print(f"ERRO: O arquivo de entrada '{arq_entrada}' não foi encontrado.")
