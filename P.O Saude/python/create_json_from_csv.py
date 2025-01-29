import pandas as pd
import json

def create_json_from_csv(csv_file, json_file):
    # Load the CSV file
    df = pd.read_csv(csv_file)
    
    # Select the required columns
    df_selected = df[['ID_BAIRRO', 'geometria', 'pessoas']]
    
    # Convert the DataFrame to a list of dictionaries
    result = df_selected.to_dict(orient='records')
    
    # Save the result to a JSON file
    with open(json_file, 'w') as file:
        json.dump(result, file, indent=4)

def create_json_from_custom_csv(csv_file, json_file):
    # Load the CSV file with custom delimiter
    df = pd.read_csv(csv_file, delimiter=';')
    
    # Select the required columns
    df_selected = df[['NOME', 'QTDPESSOAS', 'ID_BAIRRO', 'GEOMETRIA']]
    
    # Convert the DataFrame to a list of dictionaries
    result = df_selected.to_dict(orient='records')
    
    # Save the result to a JSON file
    with open(json_file, 'w') as file:
        json.dump(result, file, indent=4)

# Example usage
# create_json_from_csv('data_excel/bquxjob_3a4be030_1936e8952e5.csv', 'dados_json/demanda_set.json')
create_json_from_custom_csv('data_excel/populacao_domicilio_bairro_2022.csv', 'dados_json/bairro_demanda_set.json')
