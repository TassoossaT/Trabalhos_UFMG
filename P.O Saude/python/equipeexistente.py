import pandas as pd
import json

def process_professionals(professionals_csv, el_json, output_json, cnes_output_json):
    # Load the professionals CSV file with specified dtype
    dtype = {
        'NOME': str, 'CNS': str, 'SEXO': str, 'IBGE': str, 'UF': str, 'MUNICIPIO': str,
        'CBO': str, 'DESCRICAO CBO': str, 'CNES': str, 'CNPJ': str, 'ESTABELECIMENTO': str,
        'NATUREZA JURIDICA': str, 'DESCRICAO NATUREZA JURIDICA': str, 'GESTAO': str, 'SUS': str,
        'RESIDENTE': str, 'PRECEPTOR': str, 'VINCULO ESTABELECIMENTO': str, 'VINCULO EMPREGADOR': str,
        'DETALHAMENTO DO VINCULO': str, 'CH OUTROS': float, 'CH AMB.': float, 'CH HOSP.': float
    }
    df = pd.read_csv(professionals_csv, delimiter=';', dtype=dtype)

    # Load the EL JSON file
    with open(el_json, 'r', encoding='utf-8') as file:
        el_data = json.load(file)

    # Get the list of hospital IDs from the EL data
    hospital_ids = [el['name'] for el in el_data]

    # Filter professionals by SUS and those working in the hospitals
    df_sus = df[(df['SUS'] == 'S') & (df['ESTABELECIMENTO'].isin(hospital_ids))]

    # Divide the working hours by 40
    df_sus['CH HOSP.'] = df_sus['CH HOSP.'] / 40

    # Aggregate information
    total_ch_hosp = df_sus['CH HOSP.'].sum()
    descricao_cbo = df_sus.groupby('DESCRICAO CBO')['CH HOSP.'].sum().sort_values(ascending=False).to_dict()
    custo_cbo = df_sus.groupby('DESCRICAO CBO')['CH HOSP.'].apply(lambda x: (x * 1000).sum()).to_dict()  # Example cost calculation

    # Apply Pareto principle to include only the top 80% of working hours
    aggregated_data = {
        'total_ch_hosp': total_ch_hosp,
        'descricao_cbo': {},
        'custo_cbo': {}
    }
    cumulative_hours = 0
    for cbo, hours in descricao_cbo.items():
        if cumulative_hours / total_ch_hosp <= 1:
            aggregated_data['descricao_cbo'][cbo] = hours
            aggregated_data['custo_cbo'][cbo] = custo_cbo[cbo]
            cumulative_hours += hours
        else:
            break

    # Save the aggregated data to the output JSON file
    with open(output_json, 'w', encoding='utf-8') as file:
        json.dump(aggregated_data, file, ensure_ascii=False, indent=4)

    # Load the aggregated data to get the list of relevant CBO categories
    with open(output_json, 'r', encoding='utf-8') as file:
        equipe_data = json.load(file)

    relevant_cbo = set(equipe_data['descricao_cbo'].keys())

    # Create CNES data for professionals in the filtered SUS dataframe
    cnes_data = {}
    for el in el_data:
        cnes = el['name']
        cnes_data[cnes] = {cbo: 0 for cbo in relevant_cbo}  # Initialize with all relevant CBOs
        for _, row in df_sus[df_sus['ESTABELECIMENTO'] == cnes].iterrows():
            cbo_description = row['DESCRICAO CBO']
            if cbo_description in relevant_cbo:
                cnes_data[cnes][cbo_description] += row['CH HOSP.']

    # Save the CNES data to the CNES output JSON file
    with open(cnes_output_json, 'w', encoding='utf-8') as file:
        json.dump(cnes_data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    levels = ['1', '2', '3']
    for level in levels:
        professionals_csv = f'data_excel/profissionais-310620.csv'  # Replace with your professionals CSV file path
        el_json = f'dados_json/EL_{level}.json'  # Replace with your EL JSON file path
        output_json = f'dados_json/Equipe_{level}.json'  # Replace with your output JSON file path
        cnes_output_json = f'dados_json/CNES_{level}.json'  # Replace with your CNES output JSON file path

        process_professionals(professionals_csv, el_json, output_json, cnes_output_json)
