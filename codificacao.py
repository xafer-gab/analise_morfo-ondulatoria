import sys
import os
import json
import mido
import csv
import shutil

def verifica_diretorios():
    
    #Verifica diretórios
    pastas = ['dados', 'dados/parsed', 'dados/results', 'dados/src']
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)
    
    #Valida a existência de indice.json
    if not os.path.exists('dados/indice.json'):
        with open('dados/indice.json', 'w', encoding='utf-8') as idx:
            json.dump([], idx)

#A função atualmente apenas codifica obras solo (uma clave)
#Pausas são representadas por nota_midi = -1
def midi_to_csv(midi_entrada, ID):
    nota = [None, None, None, False]
    serie_notas = []
    
    mid = mido.MidiFile(midi_entrada)
    dur_abs = 0.0
    
    for msg in mid:
        
        #Tempo delta de todos os eventos
        dur_abs += msg.time
        
        #Define tipo de evento
        tipo_evento = msg.type
        if tipo_evento == "note_on" and msg.velocity == 0:
            tipo_evento = "note_off"
        if msg.is_meta and not tipo_evento == "end_of_track":
            continue
        
        #Verifica o caráter do evento
        if tipo_evento == "note_on" and not nota[3]:        
            nota = [msg.channel, msg.note, dur_abs, True]
        elif tipo_evento == "note_on" and nota[3]:
            serie_notas.append({
                "nota_midi": nota[1],
                "tempo_inicio": nota[2],
                "duracao_segundos": dur_abs - nota[2]
                })
            nota = [msg.channel, msg.note, dur_abs, True]
        elif tipo_evento == "note_off":
            nota_parada = [msg.channel, msg.note]
            if nota_parada[:2] == nota[:2]:
                serie_notas.append({
                "nota_midi": nota[1],
                "tempo_inicio": nota[2],
                "duracao_segundos": dur_abs - nota[2]
                })
                nota = [None, None, None, False]
        elif tipo_evento == "end_of_track" and nota[3]:
            serie_notas.append({
            "nota_midi": nota[1],
            "tempo_inicio": nota[2],
            "duracao_segundos": dur_abs - nota[2]
            })
        
    if not serie_notas:
        print("ERRO: o arquivo MIDI não contém notas.")
        sys.exit(3)
            
    #Calcula pausas entre itens
    serie_notas_pausas = []
    
    # Pausa inicial
    if serie_notas[0]["tempo_inicio"] > 0:
        serie_notas_pausas.append({
            "nota_midi": -1,
            "tempo_inicio": 0,
            "duracao_segundos": serie_notas[0]["tempo_inicio"]
            })
    
    for i in range(len(serie_notas) - 1):
        a_fim = serie_notas[i]["tempo_inicio"] + serie_notas[i]["duracao_segundos"]
        b_ini = serie_notas[i+1]["tempo_inicio"]
        dif = b_ini - a_fim
        if dif != 0:
            if dif > 0:
                serie_notas_pausas.append(serie_notas[i])
                serie_notas_pausas.append({
                    "nota_midi": -1,
                    "tempo_inicio": a_fim,
                    "duracao_segundos": dif
                    })
            else:
                print("ERRO: o arquivo MIDI apresentou erro no parsing [sobreposição de notas]")
                sys.exit(4)
        else:
            serie_notas_pausas.append(serie_notas[i])
    
    #Última nota sem pausa
    serie_notas_pausas.append(serie_notas[-1])

    # Gravação do arquivo CSV
    saida_csv = f'dados/parsed/{ID}.csv'
    with open(saida_csv, mode="w", encoding="utf-8") as csv_file:
        fieldnames = ["nota_midi", "tempo_inicio", "duracao_segundos"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for nota_gravada in serie_notas_pausas:
            writer.writerow(nota_gravada)

def fluxo_entrada():
    
    #Valida a variável posicional
    if len(sys.argv) < 2:
        print('Uso: python3 codificacao_csv.py <arquivo.mid>')
        sys.exit(1)
    
    #Valida a extensão
    midi_input = sys.argv[1]
    if not midi_input.lower().endswith((".mid", ".midi")):
        print(f'O caminho {midi_input} não é um arquivo MIDI (i.e. .mid ou .midi)')
        sys.exit(2)
        
    #Verifica/cria diretórios do banco de dados
    verifica_diretorios()   
        
    #Atribui um ID e coleta informações da entrada
    with open('dados/indice.json', 'r', encoding='utf-8') as idx:
        indice = json.load(idx)
    
    #Calcula índice
    if indice:
        ID = indice[-1]['id'] + 1
    else:
        ID = 1
        
    #Entradas de referência
    compositor = input("Nome do(a) compositor(a): \n>>> ")
    obra = input("Título da obra: \n>>> ")
    movimento = input("Título do movimento: \n>>> ") or "não informado"
    formacao = input("Formação instrumental: \n>>> ") or "não informado"
    tonalidade = input("Tonalidade ou sistema harmônico: \n>>> ") or "não informado"
    
    #Sanitiza entrada para apresentar valores essenciais
    if not compositor or not obra:
        print("O nome do compositor ou obra não foi informado. Registro interrompido")
        sys.exit(3)

    #Formata o dicionário
    dicionario_entrada = {
        'id':ID,
        'compositor':compositor,
        'obra':obra,
        'movimento':movimento,
        'formacao':formacao,
        'tonalidade':tonalidade
        }
        
    #Codifica, copia e salva o arquivo MIDI no banco de dados
    try:
        midi_to_csv(midi_input, ID)
        shutil.copy(midi_input, f"dados/src/{ID}.mid")
    except Exception as e:
        print(f"Erro ao codificar o arquivo MIDI: {e}")
        sys.exit(4)
    
    #Registra a entrada no banco de dados
    indice.append(dicionario_entrada)
    indice_saida = json.dumps(indice, indent = 4)
    with open('dados/indice.json', 'w', encoding='utf-8') as idx:
        idx.write(indice_saida)
    print(f"Arquivo {midi_input} codificado com sucesso")
    
#Execução
if __name__ == "__main__":
    fluxo_entrada()
