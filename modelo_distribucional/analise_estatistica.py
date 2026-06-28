import csv
import os

# ==============================================================================
# CONFIGURAÇÕES DE ENTRADA E SAÍDA (HARDCODED)
# ==============================================================================
ARQUIVO_ENTRADA = "analise.csv"
ARQUIVO_SAIDA_UNICO = "analise_flauta_sarabanda.csv"


# ==============================================================================
# PARTE 1: Leitura e armazenamento em dicionário
# ==============================================================================
def ler_dados_midi_csv(caminho_arquivo):
    """Abre o arquivo CSV contendo os dados extraídos do MIDI, armazena

    e retorna as informações estruturadas em um dicionário.
    """
    dados_dicionario = {
        "nota_midi": [],
        "tempo_inicio": [],
        "duracao_segundos": [],
    }

    with open(caminho_arquivo, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for linha in reader:
            dados_dicionario["nota_midi"].append(int(linha["nota_midi"]))
            dados_dicionario["tempo_inicio"].append(
                float(linha["tempo_inicio"])
            )
            dados_dicionario["duracao_segundos"].append(
                float(linha["duracao_segundos"])
            )

    return dados_dicionario


# ==============================================================================
# PARTE 2: Funções de Análise Estatística
# ==============================================================================
def calcular_media_alturas(dados):
    """Calcula a média simples de todas as alturas (nota_midi)."""
    lista_alturas = dados["nota_midi"]

    if not lista_alturas:
        return 0.0

    media_simples = sum(lista_alturas) / len(lista_alturas)
    return media_simples


def calcular_media_ponderada_alturas(dados):
    """Calcula a média ponderada das alturas usando a duração em segundos

    como peso de cada nota.
    """
    lista_alturas = dados["nota_midi"]
    lista_duracoes = dados["duracao_segundos"]

    if not lista_alturas or sum(lista_duracoes) == 0:
        return 0.0

    soma_ponderada = sum(
        nota * duracao for nota, duracao in zip(lista_alturas, lista_duracoes)
    )
    media_ponderada = soma_ponderada / sum(lista_duracoes)
    return media_ponderada


def calcular_desvio_padrao_alturas(dados):
    """Calcula a resposta do desvio padrão populacional das alturas (nota_midi)."""
    lista_alturas = dados["nota_midi"]

    if not lista_alturas:
        return 0.0

    num_elementos = len(lista_alturas)
    media = sum(lista_alturas) / num_elementos
    soma_quadrados_diferencas = sum((nota - media) ** 2 for nota in lista_alturas)
    variancia = soma_quadrados_diferencas / num_elementos
    desvio_padrao = variancia**0.5

    return desvio_padrao


# ==============================================================================
# PARTE 3: Gravação Unificada (Modo Append de Linha Completa)
# ==============================================================================
def gravar_linha_analise_unificada(
    caminho_arquivo, m_simples, m_ponderada, d_padrao
):
    """Grava as três métricas calculadas em uma única linha em modo 'append'.

    Caso o arquivo não exista, cria os três cabeçalhos na primeira linha.
    """
    arquivo_existe = os.path.exists(caminho_arquivo)
    cabecalhos = ["media_simples", "media_ponderada", "desvio_padrao"]

    with open(caminho_arquivo, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Escreve o cabeçalho triplo se o arquivo for novo
        if not arquivo_existe:
            writer.writerow(cabecalhos)

        # Escreve o vetor contendo as três métricas da análise atual
        writer.writerow([m_simples, m_ponderada, d_padrao])


# ==============================================================================
# EXECUÇÃO DO SCRIPT
# ==============================================================================
if __name__ == "__main__":
    try:
        print(f"Lendo dados de entrada: '{ARQUIVO_ENTRADA}'...")
        dados_musicais = ler_dados_midi_csv(ARQUIVO_ENTRADA)

        # 1. Processamento e cálculo das métricas
        m_simples = calcular_media_alturas(dados_musicais)
        m_ponderada = calcular_media_ponderada_alturas(dados_musicais)
        d_padrao = calcular_desvio_padrao_alturas(dados_musicais)

        # 2. Gravação unificada das métricas em uma nova linha (Vetor temporal)
        gravar_linha_analise_unificada(
            ARQUIVO_SAIDA_UNICO, m_simples, m_ponderada, d_padrao
        )

        print(
            f"\n--- Análise concluída! Métricas adicionadas em '{ARQUIVO_SAIDA_UNICO}' ---"
        )
        print(f"Média Simples:    {m_simples:.4f}")
        print(f"Média Ponderada:  {m_ponderada:.4f}")
        print(f"Desvio Padrão:    {d_padrao:.4f}\n")

    except FileNotFoundError:
        print(
            f"Erro: O arquivo de entrada '{ARQUIVO_ENTRADA}' não foi encontrado. "
            f"Verifique se o arquivo gerador rodou corretamente."
        )
