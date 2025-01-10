import pandas as pd
from flask import Blueprint, request, render_template, redirect, flash
from database.models.database_class import db, BOMs, OITM

bp_BOM_route = Blueprint("BOM", __name__)

"""
Rota de BOMs

    - /BOMs/                - (GET) - Listar BOMs
    - /BOMs/                - (POST) - Inserir BOM no servidor (Filtrar)
    - /BOMs/new             - (GET) - Rendenizar um formulário para criar uma BOM
    - /BOMs/<código>        - (GET) - Obter dados de uma BOM (Retrabalho, versões, changelog e etc)
    - /BOMs/<códugo>/edit   - (GET) - Rendenizar um formulário para editar uma BOM
    - /BOMs/<códugo>/update - (PUT) - Atualizar  os dados da BOM
    - /BOMs/<códugo>/delete - (DELETE) - Deleta BOM

"""

@bp_BOM_route.route('/', methods=['GET'])

def lista_BOMs():
    placa = request.args.get('placa', '').strip()
    versao = request.args.get('versao', '').strip()
    status = request.args.get('status', '').strip()
    componente = request.args.get('componente', '').strip()

    # Se os parâmetros forem passados com valores separados por vírgula, convertemos em listas
    placas_filtro = placa.split(',') if placa else []
    versoes_filtro = versao.split(',') if versao else []
    status_filtro = status.split(',') if status else []
    componentes_filtro = componente.split(',') if componente else []

     # Inicia a consulta base
    query = db.session.query(BOMs.Placa, 
        BOMs.Versao, 
        BOMs.Status, 
        BOMs.Componente, 
        BOMs.Quantidade, 
        BOMs.Designator, 
        OITM.Descricao
    )  # Seleciona as duas tabelas

    # Adiciona o join entre BOMs e Componentes com base no campo 'Componente'
    query = query.join(BOMs, BOMs.Componente == OITM.Codigo)
    resultados_placas = []

        # Aplica filtros dinâmicos se presentes
    if placas_filtro:
        query = query.filter(BOMs.Placa.in_(placas_filtro))
        placas_descricao = db.session.query(OITM.Codigo, OITM.Descricao).filter(OITM.Codigo.in_(placas_filtro))
        resultados_placas = placas_descricao.all()

    if versoes_filtro:
        query = query.filter(BOMs.Versao.in_(versoes_filtro))
    if status_filtro:
        query = query.filter(BOMs.Status.in_(status_filtro))
    if componentes_filtro:
        query = query.filter(BOMs.Componente.in_(componentes_filtro))

    # Executa a consulta
    resultados = query.all()

    return render_template('BOMs.html', 
                           dados=resultados,
                           dados_placa = resultados_placas,
                           placa=placa,
                           versao=versao,
                           status=status,
                           componente=componente)

@bp_BOM_route.route('/new', methods=['POST'])
 
def add_BOMs():
    # new_placa = request.form.get('new_placa', '').strip()  # Correto: use parênteses
    # new_versao = request.form.get('new_versao', '').strip()  # Correto: use parênteses
    # new_status = request.form.get('new_status', '').strip()  # Correto: use parênteses
    # new_componente = request.form.get('new_componente', '').strip()  # Correto
    # new_quantidade = request.form.get('new_quantidade', '').strip()  # Correto
    # new_designator = request.form.get('new_designator', '').strip()

    # print("Concater:", new_placa+new_versao+new_status+new_componente+str(new_quantidade)+new_designator)
    # edit = BOMs(ID=new_placa+new_versao+new_status+new_componente+str(new_quantidade)+new_designator,
    #             Placa=new_placa,
    #             Versao=new_versao,
    #             Status=new_status,
    #             Componente=new_componente,
    #             Quantidade=new_quantidade,
    #             Designator=new_designator)
    
    # db.session.add(edit)
    # db.session.commit()
    # print("foi")
    # return redirect('/BOMs')

    file = request.files['file']

    if file and file.filename.endswith('.xlsx'):  # Verifica a extensão
        try:
            # Lê o arquivo Excel diretamente da memória com pandas
            data = pd.read_excel(file)
            # Itera pelas linhas do DataFrame e adiciona ao banco de dados
            for _, row in data.iterrows():
                new_BOM = BOMs(
                    ID=f"{row['Placa']}{row['Versao']}{row['Status']}{row['Componente']}{row['Quantidade']}{row['Designator']}",
                    Placa=row['Placa'],
                    Versao=row['Versao'],
                    Status=row['Status'],
                    Componente=row['Componente'],
                    Quantidade=row['Quantidade'],
                    Designator=row['Designator']
                )
                db.session.add(new_BOM)

            db.session.commit()
            flash('Dados carregados com sucesso.')
            return render_template('formulario_cadastro_BOM.html')
        
        except Exception as e:
            flash(f"Ocorreu um erro ao processar o arquivo: {str(e)}", 'error')
            print("to qui")
            return render_template('formulario_cadastro_BOM.html')           
    else:
        print("to qui TBM")
        flash('Erro: Apenas arquivos Excel (.xlsx) são permitidos.')
        return "Não é um xlsx"


@bp_BOM_route.route('/new', methods=['GET'])
def form_cadastro_BOM():
    "Formulário para cadastrar uma BOM"
    return render_template('formulario_cadastro_BOM.html')

@bp_BOM_route.route('/', methods=['GET'])
def detalhes_BOM(codigo_BOM):
    "Exibe detalhes da BOM"
    return render_template('detalhes_BOM.html')

@bp_BOM_route.route('/edit', methods=['GET'])
def form_edit_BOM():
    
    return render_template('fomulario_edit_BOM.html')

@bp_BOM_route.route('<codigo_BOM>/update', methods=['PUT'])
def update_BOM(codigo_BOM):
    "Atualizar BOM"
    pass   

@bp_BOM_route.route('delete', methods=['DELETE'])
def deletar_cliente():
    "Deletar informações BOM"
    pass   
