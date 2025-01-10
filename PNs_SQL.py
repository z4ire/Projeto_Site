import pandas as pd
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
SELECT U_ItemCode, U_NEO_DESCRI, U_NEO_PARTNUM, U_NEO_STPN
FROM CT_PF_OIDT
FULL JOIN CT_PF_IDT3 ON CT_PF_OIDT.Code = CT_PF_IDT3.Code
FULL JOIN OITM ON OITM.[cod-item] = CT_PF_OIDT.U_ItemCode
WHERE (U_ItemCode LIKE '6.%' OR U_ItemCode LIKE '7.%' OR U_ItemCode LIKE '8.%' OR U_ItemCode LIKE '9.%')
  AND (U_ItemCode IS NOT NULL AND U_NEO_DESCRI IS NOT NULL AND U_NEO_PARTNUM IS NOT NULL AND U_NEO_STPN IS NOT NULL)
ORDER BY U_ItemCode""")

dados_sqlserver = cursor_sqlserver.fetchall()

if dados_sqlserver:

    print("Dados recuperados do SQL Server:", dados_sqlserver)
    cursor_sqlite.execute('DELETE FROM PNs_SQL')
    cursor_sqlite.executemany('''
    INSERT INTO PNs_SQL (Codigo, Fabricante, PN, Status_PN)
    VALUES (?, ?, ?, ?)
    ''', dados_sqlserver)
    conexao_sqlite.commit()
else:
    # Caso não existam dados recuperados, exibe uma mensagem informando que nenhuma alteração foi feita.
    print("Nenhum dado foi retornado do SQL Server. Nenhuma alteração foi feita na tabela SQLite.")

# Fechando as conexões
# Fecha as conexões com ambos os bancos de dados, SQLite e SQL Server, para liberar recursos.
conexao_sqlite.close()
conexao_sqlserver.close()