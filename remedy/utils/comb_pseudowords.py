import pandas as pd
import random
import os
import os.path as op

def generate_combinations(participant_id, categories, audio_labels, base_audio_path):

    # Assegna le etichette audio in modo sequenziale
    participant_audio_labels = audio_labels[(participant_id - 1) % len(audio_labels):] + audio_labels[:(participant_id - 1) % len(audio_labels)]

    # Crea i percorsi dei file audio basati sulle etichette
    pseudo_paths = [os.path.join(base_audio_path, f"pseudoparola_{label}.wav") for label in participant_audio_labels]

    # Divide le categorie in due gruppi (prima sessione e seconda sessione)
    first_session_categories = categories[:3]
    second_session_categories = categories[3:]

    # Crea il dataframe delle combinazioni per la prima sessione
    first_session_combinations = pd.DataFrame({
        'Participant_ID': [participant_id] * 3,
        'Session': [1] * 3,
        'Category': first_session_categories,
        'Pseudo': pseudo_paths[:3]
    })

    # Crea il dataframe delle combinazioni per la seconda sessione
    second_session_combinations = pd.DataFrame({
        'Participant_ID': [participant_id] * 3,
        'Session': [2] * 3,
        'Category': second_session_categories,
        'Pseudo': pseudo_paths[3:]
    })

    # Concatena i due dataframes
    all_combinations = pd.concat([first_session_combinations, second_session_combinations])

    return all_combinations

def main():
    categories = ['Buildings', 'Children', 'Food', 'Mammals', 'Vehicles', 'Water']
    audio_labels = ['A', 'B', 'C', 'D', 'E', 'F']  

    base_audio_path = op.join(os.getcwd(), 'data', 'pwd')

    all_combinations = pd.DataFrame()

    for participant_id in range(1, 46):
        combinations = generate_combinations(participant_id, categories, audio_labels, base_audio_path)
        all_combinations = pd.concat([all_combinations, combinations])
   # Verifica il bilanciamento delle combinazioni
    category_counts = all_combinations.groupby(['Session', 'Category']).size().unstack(fill_value=0)
    audio_counts = all_combinations.groupby(['Session', 'Pseudo']).size().unstack(fill_value=0)

    print("\nCounts per Category:")
    print(category_counts)

    print("\nCounts per Audio:")
    print(audio_counts)
    all_combinations.to_csv(op.join(os.getcwd(), 'combinations', 'all_combinations_pseudo_final.csv'), index=False)

if __name__ == "__main__":
    main()