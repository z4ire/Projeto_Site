
import pyodbc
import sqlite3

server = "kimera"
database = "Repositorio_SAP"
username = "leitura_sap"
password = "Fx!74Xq0gBg@qit"
string_conexao = 'Driver={SQL Server};Server=' + server + ';Database=' + database + ';UID=' + username + ';PWD=' + password

conexao_sqlserver = pyodbc.connect(string_conexao)
conexao_sqlite = sqlite3.connect(r'C:\Users\zcouto\OneDrive - Padtec\Documents\Projeto_Site\instance\BOMs.db')


cursor_sqlserver = conexao_sqlserver.cursor()
cursor_sqlite = conexao_sqlite.cursor()

cursor_sqlserver.execute("""
SELECT DISTINCT
    NEO_ALT_CB.[U_NEO_ITEM_PRO],
    NEO_ALT_LINHAS.[U_NEO_ITEM],
    NEO_ALT_LINHAS.[U_NEO_ITEM_AL]
FROM 
    [Repositorio_SAP].[dbo].[NEO_ALT_LINHAS]
JOIN 
    [Repositorio_SAP].[dbo].[NEO_ALT_CB]
    ON NEO_ALT_LINHAS.[DocEntry] = NEO_ALT_CB.[DocEntry]
WHERE 
    NEO_ALT_CB.[U_NEO_ITEM_PRO] LIKE '6.%'
""")

dados_sqlserver = cursor_sqlserver.fetchall()

if dados_sqlserver:
    print("Dados recuperados do SQL Server:", dados_sqlserver)

    # Limpar a tabela antes de inserir os novos dados
    cursor_sqlite.execute('DELETE FROM ALTERNATIVOS_SAP')

    dados_para_inserir = []

    for row in dados_sqlserver:
        U_NEO_ITEM_PRO, U_NEO_ITEM, U_NEO_ITEM_AL = row
        U_NEO_ITEM_PRO = (U_NEO_ITEM_PRO or "").strip()
        U_NEO_ITEM = (U_NEO_ITEM or "").strip()
        U_NEO_ITEM_AL = (U_NEO_ITEM_AL or "").strip()
        concatenado = f"{U_NEO_ITEM_PRO}{U_NEO_ITEM}{U_NEO_ITEM_AL}"
        dados_para_inserir.append((U_NEO_ITEM_PRO, U_NEO_ITEM, U_NEO_ITEM_AL, concatenado))

    # Exibindo os dados concatenados para conferência
    print("\nDados para inserção:", dados_para_inserir)

    # Inserir os novos dados na tabela SQLite
    cursor_sqlite.executemany('''
    INSERT INTO ALTERNATIVOS_SAP (Placa_ALT, Comp_Princ, Comp_Alt, CONCAT)
    VALUES (?, ?, ?, ?)
    ''', dados_para_inserir)  # Usar 'dados_para_inserir', não 'dados_sqlserver'

    # Commit para garantir que as alterações sejam salvas
    conexao_sqlite.commit()

else:
    print("Nenhum dado foi retornado do SQL Server. Nenhuma alteração foi feita na tabela SQLite.")

# Fechar as conexões
conexao_sqlite.close()
conexao_sqlserver.close()