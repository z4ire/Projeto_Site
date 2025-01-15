import pandas as pd

# Função para comparar as versões e gerar o changelog
def gerar_changelog(df_versao_antiga, df_versao_nova, versao_antiga, versao_nova):
    changelog = []

    # Identificar inserções (componentes presentes na nova versão mas não na antiga)
    insercoes = df_versao_nova[~df_versao_nova['Componente'].isin(df_versao_antiga['Componente'])]
    for _, row in insercoes.iterrows():
        changelog.append({
            'placa': row['Placa'],
            'componente': row['Componente'],
            'quantidade': row['Quantidade'],
            'versao_antiga': versao_antiga,
            'versao_nova': versao_nova,
            'operacao': 'INSERT',
            'data_alteracao': pd.to_datetime('now')
        })

    # Identificar atualizações (componentes com a mesma placa e componente, mas quantidades diferentes)
    atualizacoes = pd.merge(df_versao_antiga, df_versao_nova, on=['Placa', 'Componente'], suffixes=('_antiga', '_nova'))
    atualizacoes = atualizacoes[atualizacoes['Quantidade_antiga'] != atualizacoes['Quantidade_nova']]
    for _, row in atualizacoes.iterrows():
        changelog.append({
            'placa': row['Placa'],
            'componente': row['Componente'],
            'quantidade': row['Quantidade_nova'],
            'versao_antiga': versao_antiga,
            'versao_nova': versao_nova,
            'operacao': 'UPDATE',
            'data_alteracao': pd.to_datetime('now')
        })

    # Identificar deleções (componentes presentes na versão antiga, mas não na nova)
    delecoes = df_versao_antiga[~df_versao_antiga['Componente'].isin(df_versao_nova['Componente'])]
    for _, row in delecoes.iterrows():
        changelog.append({
            'placa': row['Placa'],
            'componente': row['Componente'],
            'quantidade': row['Quantidade'],
            'versao_antiga': versao_antiga,
            'versao_nova': versao_nova,
            'operacao': 'DELETE',
            'data_alteracao': pd.to_datetime('now')
        })

    return pd.DataFrame(changelog)

# Exemplo de uso

# Criar DataFrames de exemplo para versões V2 e V3
dados_v2 = {
    'Placa': ['Placa 1', 'Placa 1', 'Placa 2', 'Placa 2', 'Placa 3'],
    'Componente': ['Componente a', 'Componente b', 'Componente g', 'Componente h', 'Componente c'],
    'Quantidade': [1, 3, 1, 3, 6],
    'Versao': ['V2', 'V2', 'V2', 'V2', 'V2']
}

dados_v3 = {
    'Placa': ['Placa 1', 'Placa 1', 'Placa 2', 'Placa 2', 'Placa 3'],
    'Componente': ['Componente a', 'Componente b', 'Componente c', 'Componente d', 'Componente z'],
    'Quantidade': [1, 3, 6, 8, 8],
    'Versao': ['V3', 'V3', 'V3', 'V3', 'V3']
}

df_v2 = pd.DataFrame(dados_v2)
df_v3 = pd.DataFrame(dados_v3)

# Gerar o changelog entre as versões V2 e V3
changelog = gerar_changelog(df_v2, df_v3, 'V2', 'V3')

# Exibir o changelog
print(changelog)
