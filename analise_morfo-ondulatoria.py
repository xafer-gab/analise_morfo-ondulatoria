import os
import json
import subprocess

versao = "1.1"
ano = "2026"
header = f"\nUtilitário para Análise Morfo-Ondulatória ({versao})\nGabriel F. Xavier, {ano}"

#Dicionário com métodos de análise
lista_metodos = {
    1: "Média simples (alturas)",
    2: "Média simples (durações)",
    3: "Média simples (som e silêncio)",
    4: "Média ponderada (alturas por durações)",
    5: "Desvio padrão (alturas)",
    6: "Desvio padrão (durações)"
}

##################
# 1. UTILITÁRIOS #
##################

def pausa():
    input('\nPressione ENTER para continuar...')

def limpa_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def carrega_banco():
    
    #Banco de dados geral
    caminho = "dados/indice.json"
   
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)     
    except FileNotFoundError:
        dados = []
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo)
        return dados
    except json.JSONDecodeError:
        print('ERRO: o índice contém JSON inválido.')
        pausa()
        return []

def utilitario_amostragem():
    bpm = input("\nInsira o valor de batidas por minuto da obra\n>>>")
    
    try:
        res = 60 / float(bpm)
    except:
        print(f"\nDigite um valor de inteiro válido (digitou: {bpm})")
        return
    
    print(f'\nValores de referência:\n1 tempo = {res:.2f}' +
        f'\n2 tempos = {res*2:.2f}' +
        f'\n3 tempos = {res*3:.2f}' +
        f'\n4 tempos = {res*4:.2f}' +
        f'\n6 tempos = {res*6:.2f}' +
        f'\n8 tempos = {res*8:.2f}' +
        f'\n9 tempos = {res*9:.2f}' +
        f'\n12 tempos = {res*12:.2f}' +
        f'\n16 tempos = {res*16:.2f}'
    )

def produz_analise(selec_metodos, obra_id, amostragem):
    limpa_tela()
    print("\n------ ANÁLISE ------\n")
    for metodo in selec_metodos:
        subprocess.run([
            'python3', 
            'metodos.py', 
            str(obra_id), 
            str(metodo), 
            str(amostragem)
            ])
    
def renderizacao_grafos(selec_metodos, modelo_grafico, obra_id, eixo):
    limpa_tela()
    print("\n------ RENDERIZAÇÃO ------\n")
    
    if modelo_grafico[0] == 'padrao':
        for metodo in selec_metodos:
            subprocess.run([
                'python3', 
                'renderizacao.py', 
                str(obra_id), 
                'simples', 
                str(metodo), 
                str(eixo)
                ])
    
    else:
        lista_metodos_str = ""
        for i in range(len(modelo_grafico)):
            if i < len(modelo_grafico) - 1:
                lista_metodos_str += str(modelo_grafico[i]) + ","
            else:
                lista_metodos_str += str(modelo_grafico[i])
        subprocess.run([
            'python3', 
            'renderizacao.py', 
            str(obra_id), 
            'composto', 
            str(lista_metodos_str),
            str(eixo)
            ])
        
def seleciona_id(indice, ids):
    if not indice:
        print('ERRO: o índice encontra-se vazio\n')
        pausa()
        return []
    
    itens = []
    for entrada in indice:
        if entrada['id'] in ids:
            itens.append(entrada)
    return itens

def busca_termo(indice, termo):
    if not indice:
        print('ERRO: o índice encontra-se vazio\n')
        pausa()
        return [], []
    
    termo = termo.lower()
    encontrados_print = []
    encontrados_lista = []
    for entrada in indice:
        entrada_possui = False
        for chave, valor in entrada.items():
            texto = str(valor).lower()
            if termo in texto:
                entrada_possui = True
                achado = f"ID {entrada['id']} - {entrada['obra']} ({entrada['compositor']}) / {chave} = {valor}"
                encontrados_print.append(achado)
        if entrada_possui:
            encontrados_lista.append(entrada)
    return encontrados_lista, encontrados_print

def lista_obras(indice):
    if not indice:
        print('ERRO: o índice encontra-se vazio\n')
        pausa()
    
    for entrada in indice:
        print(f"{entrada['id']}: {entrada['obra']} ({entrada['compositor']})")

########################
# 2. MENUS INTERATIVOS #
########################

menu_principal = '''
MENU PRINCIPAL
1 - Produzir análises e gráficos
2 - Adicionar obra no banco de dados
3 - Pesquisar obras por termo
4 - Exibir lista completa de obras
5 - Encerrar programa

>>>'''

menu_analise = '''
ANÁLISE E RENDERIZAÇÃO
1 - Selecionar obras
2 - Selecionar métodos
3 - Análise
4 - Renderização
5 - Retornar ao menu principal

>>>'''

menu_render = '''
RENDERIZAÇÃO
1 - Renderizar grafos
2 - Configurações
3 - Retornar ao menu anterior

>>>'''

menu_config = '''
CONFIGURAÇÃO GRÁFICA
1 - Adicionar modelo gráfico
2 - Visualizar modelos
3 - Retornar ao menu anterior

>>>'''

menu_eixo_x = '''
Selecione a referência do eixo X:
1 - Tempo transcorrido em segundos
2 - Índice de amostra
>>>'''

menu_eixo_x_etiqueta = '''
Selecione a etiqueta do eixo X:
1 - Padrão
2 - Personalizada
>>>'''

# 2.1. ANÁLISE E RENDERIZAÇÃO

def seleciona_obras_menu(indice, selec_obras):
    sair = False
    while not sair:

        limpa_tela()
        idx = input("\nDigite os ID's das obras separados por vírgula e sem espaço (ex. 1,2,3):\n>>>")
        try:
            idx_numeros = idx.split(',')
            idx_numeros = [int(chave) for chave in idx_numeros]
            selec_obras = seleciona_id(indice, idx_numeros)
        except:
            selec_obras = []
        
        if not selec_obras:
            print("\nDigite uma entrada válida de ID's")
            pausa()
            break

        while True:
            limpa_tela()
            print("\nVocê deseja selecionar as obras abaixo? (s/n)\n")
            
            for entrada in selec_obras:
                print(f'ID {entrada["id"]} - {entrada["obra"]} ({entrada["compositor"]})')
            s_n = (input("\n>>>")).lower()
            
            if s_n == "s":
                sair = True
                break
            elif s_n == "n":
                selec_obras = []
                sair = True
                print("\nSeleção cancelada.\n")
                pausa()
                break
            else:
                print("\nSelecione uma opção válida\n")
                pausa()
    return selec_obras

def seleciona_metodos_menu(selec_metodos):
    sair = False
    while not sair:
        limpa_tela()
        print("Digite o número dos métodos separados por vírgula e sem espaço (ex. 1,2,3):")
        
        for chave in lista_metodos.keys():
            print(f'{chave} - {lista_metodos[chave]}')
        metodos_input = input("\n>>>")
        
        try:
            metodos_nums = metodos_input.split(',')
            metodos_nums = [int(chave) for chave in metodos_nums]
            selec_metodos = [lista_metodos[chave] for chave in metodos_nums]
        except:
            selec_metodos = []
        
        if not selec_metodos:
            print("\nDigite uma entrada válida de métodos")
            pausa()
            break

        while True:
            limpa_tela()
            print("\nVocê deseja selecionar os métodos abaixo? (s/n)\n")
            for entrada in selec_metodos:
                print(entrada)
            s_n = (input("\n>>>")).lower()
            
            if s_n == "s":
                sair = True
                break
            elif s_n == "n":
                selec_metodos = []
                sair = True
                print("\nSeleção cancelada.\n")
                pausa()
                break
            else:
                print("\nSelecione uma opção válida\n")
                pausa()
    return selec_metodos

def executa_analise(selec_obras, selec_metodos):
    if not selec_obras or not selec_metodos:
        if not selec_obras:
            print("\nERRO: Não há obras selecionadas para análise")
        if not selec_metodos:
            print("\nERRO: Não há métodos selecionados para análise")
        pausa()
        return
    
    limpa_tela()
    print("\nANÁLISE MUSICAL")
    for obra in selec_obras:
        while True:
            print(f"\nID {obra['id']} - {obra['obra']} ({obra['compositor']})\n")
            amos = input('Indique a janela de amostragem da análise em segundos (ex. 1.0) ou digite "UTIL" para acessar o utilitário.\n>>>')
            
            if amos.lower() == "util":
                utilitario_amostragem()
                pausa()
                continue
            
            try:
                amos = float(amos)
                if amos <= 0:
                    print(f"\nDigite um valor de ponto flutuante maior que zero (digitou: {amos})")
                    continue
                #Executa análise    
                produz_analise(selec_metodos, obra['id'], amos)
                break
            except:
                print(f"\nDigite um valor de ponto flutuante válido (digitou: {amos})")
                continue
    
    print("\nProcesso concluído.")
    pausa()
    return
    
def configuracao(selec_metodos, render_config):
    while True:
        limpa_tela()
        opc = input(menu_config)
        
        #Cria modelos gráficos sobrepondo métodos
        if opc == "1":
            limpa_tela()
            print ("\nCONFIGURAÇÃO GRÁFICA")
            print("\nDigite o número dos métodos separados por vírgula e sem espaço (ex. 1,2,3) que serão agrupados no mesmo gráfico:")
            
            for i, metodo_nome in enumerate(selec_metodos):
                print(f'{i+1} - {metodo_nome}')
            modelo_input = input("\n>>>")
            
            try:
                modelo_nums = modelo_input.split(',')
                modelo_nums = [int(idx) - 1 for idx in modelo_nums]
                modelo = [selec_metodos[idx] for idx in modelo_nums if 0 <= idx < len(selec_metodos)]
                if not modelo:
                    raise ValueError("Nenhum método válido selecionado.")
                render_config.append(modelo)
            except (ValueError, IndexError):
                print("\nDigite uma entrada válida de métodos")
                pausa()
                continue
        
        #Exibe os modelos criados
        elif opc == "2":
            print("\nModelos Gráficos:\n")
            for i, mod in enumerate(render_config):
                print(f'{i} - {mod}')
            pausa()
            continue
        
        #Retorna ao menu de renderização
        elif opc == "3":
            return render_config
        
        else:
            print("\nSelecione uma opção válida\n")
            pausa()
    
def renderiza_grafico(selec_obras, selec_metodos, render_config):
    if not selec_obras or not selec_metodos:
        if not selec_obras:
            print("\nERRO: Não há obras selecionadas para renderização")
        if not selec_metodos:
            print("\nERRO: Não há métodos selecionados para renderização")
        pausa()
        return render_config
    
    while True:
        limpa_tela()
        print("\nRENDERIZAÇÃO DE GRÁFICOS")
        renderiza = input(menu_render)
        
        #Renderiza gráfico
        if renderiza == "1":
            
            #Modelo gráfico para plotar
            print("\nSelecione o modelo gráfico:\n")
            for i, mod in enumerate(render_config):
                print(f'{i} - {mod}')
            modelo_graf_idx = input("\n>>>")
            
            try:
                modelo_selec = render_config[int(modelo_graf_idx)]
            except (ValueError, IndexError):
                print("\nSelecione uma opção válida\n")
                pausa()
                continue
            
            #Define a referência do eixo X
            while True:
                eixo_idx = input(menu_eixo_x)
                if eixo_idx == "1":
                    eixo_tipo = "segundos"
                    break
                elif eixo_idx == "2":
                    eixo_tipo = "indice"
                    break
                else:
                    print("\nSelecione uma opção válida\n")
                    pausa()
                    continue
                
            #Define a etiqueta do eixo X
            while True:
                eixo_etiqueta = input(menu_eixo_x_etiqueta)
                if eixo_etiqueta == "1":
                    if eixo_tipo == "segundos":
                        eixo = "segundos,Segundos"
                    else:
                        eixo = "indice,Índice de janela amostral"
                    break
                elif eixo_idx == "2":
                    etiqueta = input("\nDigite o nome da etiqueta:\n>>>")
                    eixo = f"{eixo_tipo},{etiqueta}"
                    break
                else:
                    print("\nSelecione uma opção válida\n")
                    pausa()
                    continue
            
            #Executa função de renderização
            for obra in selec_obras:
                print(f"\nID {obra['id']} - {obra['obra']} ({obra['compositor']})\n")
                renderizacao_grafos(selec_metodos, modelo_selec, obra['id'], eixo)
            print("\nProcesso concluído.")
            pausa()
        
        #Opção de gerar modelos gráficos
        elif renderiza == "2":
            render_config = configuracao(selec_metodos, render_config)
        
        #Expõem modelos criados e disponíveis
        elif renderiza == "3":
            return render_config
        
        else:
            print("\nSelecione uma opção válida\n")
            pausa()

def menu_analise_interface(indice, selec_obras, selec_metodos, render_config):
    while True:
        limpa_tela()
        analise = input(menu_analise)
        
        #Seleção de obras para análise e renderização
        if analise == "1":
            selec_obras = seleciona_obras_menu(indice, selec_obras)
        
        #Seleção de métodos de análise
        elif analise == "2":
            selec_metodos = seleciona_metodos_menu(selec_metodos)
        
        #Execução das análises com os referidos métodos
        elif analise == "3":
            executa_analise(selec_obras, selec_metodos)
        
        #Produção de gráficos a partir de análises realizadas
        elif analise == "4":
            render_config = renderiza_grafico(selec_obras, selec_metodos, render_config)
        
        #Retornar ao menu anterior
        elif analise == "5":
            break
        
        else:
            print("\nSelecione uma opção válida\n")
            pausa()
    
    return selec_obras, selec_metodos, render_config

# 2.2. ATUALIZAÇÃO, PESQUISA E VISUALIZAÇÃO DO BANCO DE DADOS

def adiciona_obra(indice):
    limpa_tela()
    midi = input("\nInsira o caminho do arquivo MIDI\n>>>")
    subprocess.run(['python3', 'codificacao.py', str(midi)])
    indice = carrega_banco()
    pausa()
    return indice

def pesquisa_obras(indice):
    limpa_tela()
    termo = input("\nDigite o termo para a pesquisa\n>>>")
    _, l_obras = busca_termo(indice, termo)
    if not l_obras:
        print(f"\nNão foi encontrada nenhuma correspondência para o termo '{termo}'.")
        pausa()
    else:
        print("\nObras com correspondência de termo:\n")
        for item in l_obras:
            print(item)
        pausa()

def exibe_obras(indice):
    limpa_tela()
    print("\nLista completa de obras:\n")
    lista_obras(indice)
    pausa()

# 2.3. MENU PRINCIPAL

def interface():
    indice = carrega_banco()
    selec_obras = []
    selec_metodos = []
    
    #Configuração padrão
    render_config = [['padrao']] 

    while True:
        limpa_tela()
        print(header)
        entrada = input(menu_principal)
        
        #Seção de análise
        if entrada == "1":
            selec_obras, selec_metodos, render_config = menu_analise_interface(indice, selec_obras, selec_metodos, render_config)
        
        #Adicionar obra no banco de dados
        elif entrada == "2":
            indice = adiciona_obra(indice)
        
        #Pesquisa simples de obras no banco de dados
        elif entrada == "3":
            pesquisa_obras(indice)
        
        #Exibe apenas o id, título e compositor(a) das obras no banco de dados
        elif entrada == "4":
            exibe_obras(indice)
        
        #Encerra o programa
        elif entrada == "5":
            limpa_tela()
            break
        
        else:
            print("Selecione uma opção válida\n")
            pausa()

if __name__ == "__main__":
    interface()
