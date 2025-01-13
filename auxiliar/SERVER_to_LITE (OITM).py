# O código tem o objetivo de conectar a dois bancos de dados (SQL Server e SQLite), 
# consultar dados específicos de uma tabela no SQL Server, e então transferir esses dados 
# para uma tabela no banco de dados SQLite, substituindo os dados antigos.
# Ele faz isso de maneira segura, com verificações de erro para garantir que dados sejam inseridos
# apenas quando existirem registros a serem transferidos.
import pyodbc
import sqlite3

server = "kimera"
database = "Repositorio_SAP"
username = "leitura_sap"
password = "Fx!74Xq0gBg@qit"
string_conexao = 'Driver={SQL Server};Server=' + server + ';Database=' + database + ';UID=' + username + ';PWD=' + password
conexao_sqlserver = pyodbc.connect(string_conexao)

conexao_sqlite = sqlite3.connect(r'C:\Users\zcouto\OneDrive - Padtec\Documents\Projeto_Site\instance\BOMs.db')

# Criando cursores para as conexões
# Um cursor é um objeto usado para executar comandos SQL e recuperar os resultados. 
# Aqui, são criados dois cursores, um para o SQL Server e outro para o SQLite.
cursor_sqlserver = conexao_sqlserver.cursor()
cursor_sqlite = conexao_sqlite.cursor()

# Consulta no SQL Server
# Executa uma consulta SQL no banco de dados do SQL Server. O objetivo é selecionar os campos 'cod-item', 'desc-item' e 'ativo'
# da tabela OITM onde o 'cod-item' começa com os números 7, 8, 9 ou 6.
# A consulta também ordena os resultados pela coluna 'cod-item'.
cursor_sqlserver.execute("""
SELECT [cod-item], [desc-item], ativo
FROM OITM
WHERE [cod-item] LIKE '7.%' 
   OR [cod-item] LIKE '8.%' 
   OR [cod-item] LIKE '9.%'
   OR [cod-item] LIKE '6.%'
ORDER BY [cod-item]
""")

# Recuperando os dados do SQL Server
# A função fetchall() é chamada para recuperar todos os resultados da consulta executada anteriormente.
# Os dados são armazenados na variável 'dados_sqlserver'.
dados_sqlserver = cursor_sqlserver.fetchall()

# Verificar se os dados não estão vazios antes de prosseguir
# Condição para garantir que a sequência de operações só será realizada caso existam dados retornados do SQL Server.
if dados_sqlserver:
    # Exibindo os dados para verificar
    # Exibe os dados recuperados do SQL Server para conferência.
    print("Dados recuperados do SQL Server:", dados_sqlserver)

    # Limpar a tabela antes de inserir os novos dados
    # Deleta todos os registros da tabela 'OITM_SIMPLIFICADO' no banco de dados SQLite para garantir que a tabela esteja limpa.
    # Isso é feito antes de inserir novos dados para evitar duplicações ou inconsistências.
    cursor_sqlite.execute('DELETE FROM OITM_SIMPLIFICADO')

    # Inserir os novos dados na tabela
    # A função executemany() é usada para inserir múltiplas linhas de dados na tabela 'OITM_SIMPLIFICADO' no SQLite.
    # O formato '?' é um placeholder, que será substituído pelos valores de 'dados_sqlserver'.
    cursor_sqlite.executemany('''
    INSERT INTO OITM_SIMPLIFICADO (Codigo, Descricao, Ativo)
    VALUES (?, ?, ?)
    ''', dados_sqlserver)

    # Commit para garantir que as alterações sejam salvas
    # O commit é realizado para garantir que todas as inserções feitas na tabela sejam salvas permanentemente no banco de dados.
    conexao_sqlite.commit()
else:
    # Caso não existam dados recuperados, exibe uma mensagem informando que nenhuma alteração foi feita.
    print("Nenhum dado foi retornado do SQL Server. Nenhuma alteração foi feita na tabela SQLite.")

# Fechando as conexões
# Fecha as conexões com ambos os bancos de dados, SQLite e SQL Server, para liberar recursos.
conexao_sqlite.close()
conexao_sqlserver.close()