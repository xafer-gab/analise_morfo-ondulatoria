import csv
import mido


def midi_to_csv(midi_file_path, output_csv_path):
    # Carrega o arquivo MIDI
    mid = mido.MidiFile(midi_file_path)

    # Dicionário para rastrear quando uma nota começou: chave=(canal, nota), valor=tempo_de_inicio_em_segundos
    active_notes = {}
    # Lista para armazenar as notas finalizadas
    note_events = []

    current_time = 0.0

    # Correção: Iterar diretamente sobre o objeto 'mid' percorre os eventos de forma
    # mesclada e cronológica, convertendo automaticamente msg.time para SEGUNDOS (float)
    for msg in mid:
        # Avança o tempo absoluto com base no delta time da mensagem atual (já em segundos)
        current_time += msg.time

        if msg.is_meta:
            continue  # Ignora meta-eventos (andamento, compasso, texto) na extração de notas

        # Detecta o início de uma nota
        if msg.type == "note_on" and msg.velocity > 0:
            note_key = (msg.channel, msg.note)
            active_notes[note_key] = current_time

        # Detecta o fim de uma nota (note_off ou note_on com velocity=0)
        elif msg.type == "note_off" or (
            msg.type == "note_on" and msg.velocity == 0
        ):
            note_key = (msg.channel, msg.note)

            if note_key in active_notes:
                start_time = active_notes[note_key]
                duration = current_time - start_time

                note_events.append(
                    {
                        "nota_midi": int(msg.note),
                        "tempo_inicio": float(start_time),
                        "duracao_segundos": float(duration),
                    }
                )
                del active_notes[note_key]

    # Ordena a lista pelo tempo de início (garante a ordem cronológica estrita)
    note_events.sort(key=lambda x: x["tempo_inicio"])

    # Gravação do arquivo CSV
    with open(
        output_csv_path, mode="w", newline="", encoding="utf-8"
    ) as csv_file:
        fieldnames = ["nota_midi", "tempo_inicio", "duracao_segundos"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for event in note_events:
            writer.writerow(event)

    print(
        f"Sucesso! {len(note_events)} notas foram salvas em '{output_csv_path}'."
    )


# Execução em lote dos seus arquivos
if __name__ == "__main__":
    midi_to_csv("minueto_bach.mid", "cello_minueto.csv")
    midi_to_csv("preludio_bach.mid", "cello_preludio.csv")
    midi_to_csv("bouree_bach.mid", "flauta_bouree.csv")
    midi_to_csv("sarabanda_bach.mid", "flauta_sarabanda.csv")
