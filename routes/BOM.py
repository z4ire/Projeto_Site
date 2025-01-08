from flask import Blueprint, request, render_template
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
    versao = request.args.get('versao', '').strip()
    status = request.args.get('status', '').strip()
    componente = request.args.get('componente', '').strip()

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

    # Aplicar filtros dinâmicos se presentes
    if status:
        query = query.filter(BOMs.Status == status)
    if componente:
        query = query.filter(BOMs.Componente == componente)
    if versao:
        query = query.filter(BOMs.Versao == versao)

    # Executa a consulta
    resultados = query.all()

    return render_template('BOMs.html', 
                           dados=resultados,
                           versao=versao,
                           status=status,
                           componente=componente)


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
