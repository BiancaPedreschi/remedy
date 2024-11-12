import pandas as pd
import ast

# Funzione per espandere le liste in colonne
def expand_lists(df, column_name):
    return df[column_name].apply(ast.literal_eval).apply(pd.Series)

# Leggi il file CSV
df = pd.read_csv('/Users/foscagiannotti/Desktop/python_projects/space/remedy/data/output_wake/BLOCKS_Pseudowords_Pp2_session_2.csv')

# Rimuovi le colonne 'Commands', 'Participant' e 'Session'
df = df.drop(columns=['Commands', 'Participant', 'Session'])

# Stampa le colonne del DataFrame per il debug
print("Colonne del DataFrame:", df.columns)

# Espandi le colonne contenenti liste
image_names = expand_lists(df, 'ImageName')
categories = expand_lists(df, 'Category')
audios = expand_lists(df, 'Audios')

# Combina tutte le colonne in un nuovo DataFrame
expanded_df = pd.concat([image_names, categories, audios], axis=1)

# Rinomina le colonne in modo dinamico
num_elements = image_names.shape[1]
expanded_df.columns = [f'ImageName_{i+1}' for i in range(num_elements)] + \
                      [f'Category_{i+1}' for i in range(num_elements)] + \
                      [f'Audios_{i+1}' for i in range(num_elements)]

# Trasforma le colonne 'ImageName' e 'Category' in righe
image_names_df = pd.melt(expanded_df.iloc[:, :num_elements], var_name='Variable', value_name='ImageName')
categories_df = pd.melt(expanded_df.iloc[:, num_elements:2*num_elements], var_name='Variable', value_name='Category')

# Combina i DataFrame 'ImageName' e 'Category'
combined_df = pd.concat([image_names_df['ImageName'], categories_df['Category']], axis=1)

# Ordina il DataFrame per 'Category' e poi per 'ImageName'
sorted_df = combined_df.sort_values(by=['Category', 'ImageName'])

# Salva il nuovo DataFrame in un file CSV
sorted_df.to_csv('/Users/foscagiannotti/Desktop/python_projects/space/remedy/data/output_wake/BLOCKS_Pseudowords_Pp2_session_2_image_names_categories_sorted.csv', index=False)