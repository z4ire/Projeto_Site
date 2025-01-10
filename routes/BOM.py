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
