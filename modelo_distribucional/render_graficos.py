import csv
import os
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURAÇÃO DE ENTRADA (HARDCODED)
# ==============================================================================
ARQUIVO_DADOS = "analise_flauta_bouree.csv"


# ==============================================================================
# FUNÇÃO DE LEITURA DOS DADOS
# ==============================================================================
def ler_metricas_unificadas(caminho_arquivo):
    """Lê o CSV unificado e extrai os vetores temporais das três métricas."""
    vetor_simples = []
    vetor_ponderada = []
    vetor_desvio = []

    with open(caminho_arquivo, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for linha in reader:
            vetor_simples.append(float(linha["media_simples"]))
            vetor_ponderada.append(float(linha["media_ponderada"]))
            vetor_desvio.append(float(linha["desvio_padrao"]))

    return vetor_simples, vetor_ponderada, vetor_desvio


# ==============================================================================
# GERADOR DE GRÁFICOS
# ==============================================================================
def plotar_analise_estatistica(v_simples, v_ponderada, v_desvio):
    """Gera os dois gráficos baseados nas métricas extraídas."""
    # Define o eixo X baseado no número de segmentos/compassos analisados
    eixo_x = list(range(1, len(v_simples) + 1))

    # Configuração da figura (2 subplots verticais)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(
        "",
        fontsize=14,
        fontweight="bold",
    )

    # --------------------------------------------------------------------------
    # Gráfico 1: Multivariado (Média Simples vs. Média Ponderada)
    # --------------------------------------------------------------------------
    ax1.plot(
        eixo_x,
        v_simples,
        color="blue",
        alpha=0.8,
        linewidth=2,
        marker="o",
        label="Média Simples",
    )
    ax1.plot(
        eixo_x,
        v_ponderada,
        color="red",
        alpha=0.8,
        linewidth=2,
        marker="o",
        label="Média Ponderada",
    )

    ax1.set_ylabel("Alturas MIDI", fontsize=11)
    ax1.set_title("Evolução das Médias", fontsize=12, loc="left")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="upper right")

    # --------------------------------------------------------------------------
    # Gráfico 2: Desvio Padrão (Vetor de Transformação)
    # --------------------------------------------------------------------------
    ax2.plot(
        eixo_x,
        v_desvio,
        color="black",
        linewidth=2,
        marker="o",
        label="Desvio Padrão",
    )

    ax2.set_xlabel("Segmento (unidade = dois compasso)", fontsize=11)
    ax2.set_ylabel("Índice de dispersão", fontsize=11)
    ax2.set_title("Transformação do Desvio Padrão", fontsize=12, loc="left")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="upper right")

    # Ajusta o espaçamento para não cortar textos
    plt.tight_layout()

    # Exibe os gráficos na tela
    plt.show()


# ==============================================================================
# EXECUÇÃO DO SCRIPT
# ==============================================================================
if __name__ == "__main__":
    if os.path.exists(ARQUIVO_DADOS):
        print(f"Carregando dados de '{ARQUIVO_DADOS}'...")
        simples, ponderada, desvio = ler_metricas_unificadas(ARQUIVO_DADOS)

        print("Gerando gráficos...")
        plotar_analise_estatistica(simples, ponderada, desvio)
    else:
        print(
            f"Erro: O arquivo '{ARQUIVO_DADOS}' não foi encontrado no diretório atual."
        )
