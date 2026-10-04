# Análise Morfo-Ondulatória: Um Modelo Distribucional de Perfis Melódicos

## Descrição Geral

Este repositório contém a implementação computacional do modelo analítico proposto no trabalho **Modelo distribucional de perfis melódicos: uma abordagem morfológica**. O sistema operacionaliza, por meio de um conjunto de scripts em Python, um procedimento de análise musical fundamentado na estatística descritiva, cujo objetivo é descrever a morfologia de perfis melódicos não apenas em termos de relações ordinais entre alturas (contorno intervalar), mas também segundo propriedades de distribuição dos eventos musicais na tessitura.

### Fundamentação Teórica

A análise musical tradicional de perfis melódicos, conforme desenvolvida por autores como Morris (1993) e Polansky e Bassein (1992), concentra-se na descrição das relações de contorno, isto é, nas configurações de intervalos entre elementos contíguos ou não contíguos de uma sequência melódica. Esses modelos, embora eficazes para a caracterização da forma enquanto rede de relações ordinais, suspendem o papel da tessitura e da distribuição dos eventos no registro.

O modelo aqui implementado parte da hipótese de que a morfologia melódica é igualmente constituída por propriedades distribucionais: a densidade, a dispersão e a concentração dos eventos ao longo do registro. Para tanto, recorre-se à estatística descritiva, reinterpretando medidas de tendência central (média simples, média ponderada) e de dispersão (desvio padrão) como descritores da configuração do perfil melódico ao longo do tempo.

O procedimento analítico adotado compreende as seguintes etapas:

1. **Codificação dos dados musicais**: conversão de arquivos MIDI em tabelas estatísticas (CSV), nas quais cada evento é representado por sua altura (nota MIDI), tempo de início e duração em segundos. Pausas são codificadas como eventos de altura -1.

2. **Segmentação temporal**: particionamento da série de eventos em janelas temporais de duração fixa, definidas pelo analista. Cada janela constitui uma amostra do perfil melódico.

3. **Cálculo de descritores estatísticos**: para cada janela, aplicam-se métodos de análise que produzem índices numéricos representativos da distribuição dos eventos na tessitura (média simples de alturas, média simples de durações, média simples de som e silêncio, média ponderada de alturas por durações, desvio padrão de alturas, desvio padrão de durações).

4. **Visualização gráfica**: geração de gráficos que representam a evolução temporal dos descritores, permitindo a correlação entre as transformações do perfil e aspectos formais observados qualitativamente no texto musical.

### Estrutura Computacional

O sistema é composto por quatro scripts principais, que operam de forma modular e sequencial.

#### 1. codificacao.py

Responsável pela conversão de arquivos MIDI em tabelas CSV e pelo registro das obras no banco de dados. O script realiza as seguintes operações:

- Verificação e criação dos diretórios do banco de dados (dados/, dados/parsed/, dados/results/, dados/src/).
- Leitura do arquivo MIDI, extração de eventos de nota (note_on, note_off) e cálculo das durações absolutas em segundos.
- Identificação de pausas entre eventos e inserção de registros com altura -1.
- Gravação do arquivo CSV resultante em dados/parsed/{ID}.csv.
- Coleta de metadados da obra (compositor, título, movimento, formação instrumental, tonalidade) e registro no índice geral (dados/indice.json).
- Cópia do arquivo MIDI original para dados/src/{ID}.mid.

A codificação atual restringe-se a obras monódicas ou à extração de uma única voz (uma clave), uma vez que o algoritmo não realiza a separação de vozes simultâneas.

#### 2. metodos.py

Implementa o particionamento temporal e os métodos de análise estatística. O script recebe como argumentos o ID da obra, o nome do método e a janela temporal (em segundos), e produz um arquivo CSV com os resultados da análise.

O particionamento temporal divide a série de eventos em janelas de duração fixa, calculando para cada janela a contribuição de cada evento em termos de duração efetiva dentro da janela. Eventos que atravessam os limites da janela são fracionados, e sua duração é proporcionalmente atribuída a cada janela.

Os métodos de análise implementados são:

| Método | Descrição |
|--------|-----------|
| Média simples (alturas) | Média aritmética das alturas MIDI dos eventos sonoros (excluindo pausas). |
| Média simples (durações) | Média aritmética das durações dos eventos sonoros (excluindo pausas). |
| Média simples (som e silêncio) | Proporção de eventos sonoros em relação ao total de eventos (incluindo pausas). |
| Média ponderada (alturas por durações) | Média das alturas ponderada pela duração de cada evento. |
| Desvio padrão (alturas) | Desvio padrão populacional das alturas MIDI dos eventos sonoros. |
| Desvio padrão (durações) | Desvio padrão populacional das durações dos eventos sonoros. |

Os resultados são gravados em dados/results/{ID}_{metodo}.csv, com as colunas: amos_idx (índice da janela), amos_dur_sec (duração da janela) e o valor calculado.

#### 3. renderizacao.py

Gera representações gráficas dos resultados das análises. O script suporta dois modos de renderização:

- **Gráfico simples**: plota uma única série temporal (um método) ao longo do eixo X, que pode representar o tempo transcorrido em segundos ou o índice da janela amostral.
- **Gráfico composto**: sobrepõe múltiplas séries temporais (múltiplos métodos) no mesmo gráfico. Quando os métodos compartilham a mesma grandeza (por exemplo, todos medem alturas em semitons), os valores são plotados em escala natural. Quando os métodos medem grandezas distintas (por exemplo, alturas e durações), os valores são normalizados para o intervalo 0-1, permitindo a comparação visual das tendências.

Os gráficos incluem título personalizável, rótulos de eixo, legenda, grade e são exportados com resolução de 300 DPI.

#### 4. analise_morfo-ondulatoria.py

Constitui a interface principal do sistema, oferecendo um menu interativo que integra todas as funcionalidades:

- **Produzir análises e gráficos**: permite selecionar obras, métodos, definir a janela de amostragem, executar as análises e renderizar os gráficos.
- **Adicionar obra no banco de dados**: invoca o script codificacao.py para inserir novas obras.
- **Pesquisar obras por termo**: realiza busca textual no índice de obras.
- **Exibir lista completa de obras**: lista todas as obras registradas.
- **Encerrar programa**.

A interface também permite a configuração de modelos gráficos compostos, nos quais múltiplos métodos são agrupados em um único gráfico.

### Fluxo de Trabalho

O fluxo típico de utilização compreende as seguintes etapas:

1. **Codificação**: o usuário insere um arquivo MIDI e fornece os metadados da obra. O sistema gera o CSV correspondente e registra a obra no índice.

2. **Seleção**: o usuário seleciona as obras e os métodos de análise desejados.

3. **Análise**: para cada obra, o usuário define a janela de amostragem (em segundos). O sistema particiona a série temporal e calcula os descritores para cada janela, gravando os resultados em CSV.

4. **Renderização**: o usuário seleciona o modelo gráfico (simples ou composto) e define as configurações do eixo X (referência temporal ou índice de amostra, etiqueta personalizada). O sistema gera os gráficos.

5. **Interpretação**: os gráficos resultantes são analisados em conjunto com a partitura e com considerações qualitativas sobre a obra, permitindo a identificação de correlações entre registro e dispersão, bem como de estratégias composicionais distintas.

## Instalação e Dependências

### Requisitos

- Python 3.7 ou superior.
- Bibliotecas Python:
  - mido (para leitura de arquivos MIDI)
  - matplotlib (para geração de gráficos)
  - csv, json, os, sys, subprocess, shutil, math, random (bibliotecas padrão)

### Instalação

1. Clone o repositório:

   git clone https://github.com/xafer-gab/analise_morfo-ondulatoria.git

   cd analise_morfo-ondulatoria

2. Instale as dependências:

   pip install mido matplotlib

3. Verifique a estrutura de diretórios. O sistema criará automaticamente as pastas necessárias na primeira execução.

### Execução

Para iniciar a interface principal:

   python3 analise_morfo-ondulatoria.py

Alternativamente, os scripts podem ser executados individualmente.

Codificação de uma obra:

   python3 codificacao.py caminho/para/arquivo.mid

Análise de uma obra:

   python3 metodos.py <id_obra> <metodo> <janela_temporal>

Exemplo:

   python3 metodos.py 1 "Média simples (alturas)" 4.0

Renderização:

   python3 renderizacao.py <id_obra> <simples|composto> <metodos> <eixo>

Exemplo:

   python3 renderizacao.py 1 simples "Média simples (alturas)" "segundos,Segundos"

## Exemplo de Uso

### 1. Codificação de uma obra

Suponha que se deseje analisar o Minueto II da Suíte nº 1 para violoncelo de J. S. Bach. O arquivo MIDI correspondente é bach_minueto.mid.

   python3 codificacao.py bach_minueto.mid

O sistema solicitará os metadados:

   Nome do(a) compositor(a): 
   >>> Johann Sebastian Bach
   Título da obra: 
   >>> Suíte nº 1 para violoncelo solo
   Título do movimento: 
   >>> Minueto II
   Formação instrumental: 
   >>> Violoncelo
   Tonalidade ou sistema harmônico: 
   >>> Sol menor

Após a codificação, a obra recebe o ID 1 e os arquivos são gerados:

- dados/parsed/1.csv
- dados/src/1.mid
- dados/indice.json (atualizado)

### 2. Análise

Para calcular a média simples das alturas com janela temporal de 2 segundos:

   python3 metodos.py 1 "Média simples (alturas)" 2.0

O resultado é gravado em dados/results/1_media_simples_alturas.csv.

### 3. Renderização

Para gerar um gráfico simples da média das alturas ao longo do tempo:

   python3 renderizacao.py 1 simples "Média simples (alturas)" "segundos,Segundos"

O gráfico é exibido na tela e pode ser salvo manualmente.

Para gerar um gráfico composto que sobrepõe a média simples e a média ponderada das alturas:

   python3 renderizacao.py 1 composto "Média simples (alturas),Média ponderada (alturas por durações)" "segundos,Segundos"

### 4. Utilização da interface interativa

A interface principal oferece um menu que guia o usuário por todas as etapas:

   MENU PRINCIPAL
   1 - Produzir análises e gráficos
   2 - Adicionar obra no banco de dados
   3 - Pesquisar obras por termo
   4 - Exibir lista completa de obras
   5 - Encerrar programa

   >>>

Ao selecionar a opção 1, o usuário acessa o menu de análise e renderização, onde pode selecionar obras, métodos, executar análises e gerar gráficos.

## Referência

XAVIER, Gabriel F. **Modelo distribucional de perfis melódicos: uma abordagem morfológica**. 2026. Texto em prelo.

## Referências Complementares

- BUSSAB, Wilton de Oliveira; MORETTIN, Pedro Alberto. **Estatística básica**. 6. ed. São Paulo: Saraiva, 2010.
- MORRIS, Robert D. New directions in the theory and analysis of musical contour. **Music Theory Spectrum**, Oxford, v. 15, n. 2, p. 205-228, outono 1993.
- PEUSNER, Leonardo. A graph topological representation of melody scores. **Leonardo Music Journal**, Cambridge, v. 12, p. 33-40, 2002.
- POLANSKY, Larry; BASSEIN, Richard. Possible and impossible melody: some formal aspects of contour. **Journal of Music Theory**, Durham, v. 36, n. 2, p. 259-284, outono 1992.
- MEREDITH, David (org.). **Computational music analysis**. Cham: Springer, 2016.
- MARSDEN, Alan. Introduction: music analysis and software. In: MEREDITH, David (org.). **Computational music analysis**. Cham: Springer, 2016. p. 1-10.
