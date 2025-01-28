import pandas as pd
import uuid
from io import BytesIO
from flask import Blueprint, request, render_template, redirect, flash, url_for, Response
from database.models.database_class import db, BOMs, OITM, PNs, ALT

bp_BOM_route = Blueprint("BOM", __name__)

@bp_BOM_route.route('/', methods=['GET'])
def lista_BOMs():
    # Processa os parâmetros de entrada
    def processa_parametro(parametro):
        return parametro.replace(' ', '').split(',') if parametro else []

    placa = processa_parametro(request.args.get('placa', ''))
    versao = processa_parametro(request.args.get('versao', ''))
    status = processa_parametro(request.args.get('status', '').strip())
    componente = processa_parametro(request.args.get('componente', ''))

    # Constrói a consulta base
    query = db.session.query(
        BOMs.ID,
        BOMs.Placa, 
        BOMs.Versao, 
        BOMs.Status, 
        BOMs.Componente, 
        BOMs.Quantidade, 
        BOMs.Designator, 
        OITM.Descricao,
        PNs.Fabricante,
        PNs.PN,
        PNs.Status_PN
    ).join(OITM, BOMs.Componente == OITM.Codigo).join(PNs, BOMs.Componente == PNs.Codigo_PN, isouter=True)

    # Cria a lista de filtros dinamicamente
    filtros = []
    if placa:
        filtros.append(BOMs.Placa.in_(placa))
    if versao:
        filtros.append(BOMs.Versao.in_(versao))
    if status:
        filtros.append(BOMs.Status.in_(status))
    if componente:
        filtros.append(BOMs.Componente.in_(componente))

    # Se ao menos um filtro for passado, aplica os filtros à consulta
    if filtros:
        query = query.filter(*filtros)
    else:
        # Se não houver filtros, retorna uma lista vazia
        resultados = []
        return render_template(
            'BOMs.html', 
            dados_agrupados={},
            dados_placa=[],
            placa=','.join(placa),
            versao=','.join(versao),
            status=','.join(status),
            componente=','.join(componente),
            pagination=resultados
        )

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 100
    resultados = query.order_by(BOMs.Placa.desc(), BOMs.Versao.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # Consulta para placas (se necessário)
    dados_placas = []
    if placa:
        dados_placas = db.session.query(OITM.Codigo, OITM.Descricao).filter(OITM.Codigo.in_(placa)).all()
        dados_placas = [
            {
                "Codigo": p.Codigo,
                "Descricao": p.Descricao,
                "baixar": url_for("BOM.download_BOM", placa=p.Codigo)
            }
            for p in dados_placas
        ]

    # Agrupamento dos resultados
    dados_agrupados = {}
    for bom in resultados.items:
        dados_agrupados.setdefault(bom.ID, []).append(bom)

    # Renderiza o template
    return render_template(
        'BOMs.html', 
        dados_agrupados=dados_agrupados,
        dados_placa=dados_placas,
        placa=','.join(placa),
        versao=','.join(versao),
        status=','.join(status),
        componente=','.join(componente),
        pagination=resultados
    )

@bp_BOM_route.route('/new', methods=['POST'])
def add_BOMs():

    # Verifica se a requisição contém um arquivo (Excel)
    file = request.files.get('file')
    if file and file.filename.endswith('.xlsx'):  # Caso o arquivo seja Excel
        try:
            # Lê o arquivo Excel diretamente da memória com pandas
            data = pd.read_excel(file)
            data = data.dropna(how='all')  # Remove linhas vazias
            print("Data from Excel:", data)
            
            # Itera pelas linhas do DataFrame e adiciona ao banco de dados
            for _, row in data.iterrows():
                new_BOM = BOMs(
                    Placa=row['Placa'],
                    Versao=row['Versao'],
                    Status=row['Status'],
                    Componente=row['Componente'],
                    Quantidade=row['Quantidade'],
                    Designator=row['Designator']
                )
                db.session.add(new_BOM)
            db.session.commit()
            flash('Dados carregados com sucesso.', 'success')
        except Exception as e:
            db.session.rollback()  # Reverte em caso de erro
            flash(f'Ocorreu um erro ao processar o arquivo: {str(e)}', 'error')

    else:  # Caso o formulário manual seja enviado
        # Obtém os dados do formulário
        new_placa = request.form.get('new_placa', '').strip()
        new_versao = request.form.get('new_versao', '').strip()
        new_status = request.form.get('new_status', '').strip()
        new_componente = request.form.get('new_componente', '').strip()
        new_quantidade = request.form.get('new_quantidade', '').strip()
        new_designator = request.form.get('new_designator', '').strip()

        # Cria o novo BOM a partir dos dados do formulário
        new_BOM = BOMs(
            Placa=new_placa,
            Versao=new_versao,
            Status=new_status,
            Componente=new_componente,
            Quantidade=new_quantidade,
            Designator=new_designator
        )
        
        # Adiciona o novo BOM ao banco de dados
        db.session.add(new_BOM)
        db.session.commit()
        flash('Dados carregados com sucesso.')

    return render_template('formulario_cadastro_BOM.html')

@bp_BOM_route.route('/new', methods=['GET'])
def form_cadastro_BOM():
    "Formulário para cadastrar uma BOM"
    return render_template('formulario_cadastro_BOM.html')

@bp_BOM_route.route('/alt', methods=['GET'])
def alternativos_BOM():

    placa = request.args.get('placa', '').strip()

    query = db.session.query(
        OITM.Codigo,
        ALT.Placa_ALT,
        ALT.Comp_Princ,
        ALT.Comp_Alt,
        PNs.Fabricante,
        PNs.PN,
        PNs.Status_PN
    )  # Seleciona as duas tabelas

    query = query.join(OITM, OITM.Codigo == ALT.Placa_ALT)
    query = query.join(PNs, PNs.Codigo_PN == ALT.Comp_Alt)

    resultados =[]   
    if placa:
        query = query.filter(OITM.Codigo==placa)
        dados_placas = db.session.query(OITM.Codigo, OITM.Descricao).filter(OITM.Codigo==placa)
        query_placas = dados_placas.all()
    else:
        query_placas = []

    query = query.order_by(ALT.Comp_Princ.desc())

    print(str(query))


    if placa:
        resultados = query.all()
    else:
        resultados =[]

    print(resultados)

    return render_template('Alt.html', dados=resultados, dados_placa = query_placas)

@bp_BOM_route.route('/delete/<bom_id>', methods=['POST'])
def form_delete_BOM(bom_id):
    linha = BOMs.query.get(bom_id)
    if linha:
        db.session.delete(linha)
        db.session.commit()
        flash('Item excluído com sucesso!', 'success')
    else:
        flash('Item não encontrado!', 'error')

    return redirect(request.referrer or url_for('home'))

@bp_BOM_route.route('/download/<placa>', methods=['GET'])
def download_BOM(placa):
    # Refaça a consulta para este caso específico da placa
    query = db.session.query(BOMs.Placa, 
        BOMs.Versao, 
        BOMs.Status, 
        BOMs.Componente, 
        BOMs.Quantidade, 
        BOMs.Designator, 
        OITM.Descricao,
        PNs.Fabricante,
        PNs.PN,
        PNs.Status_PN
    ).join(OITM, BOMs.Componente == OITM.Codigo).join(PNs, BOMs.Componente == PNs.Codigo_PN)

    query = query.filter(BOMs.Placa == placa)
    baixar = query.all()

    # Converte os dados para DataFrame
    df = pd.DataFrame(baixar, columns=[
        "Placa", "Versao", "Status", "Componente", "Quantidade", "Designator",
        "Descricao", "Fabricante", "PN", "Status_PN"
    ])

    # Gera o arquivo CSV em memória
    output = BytesIO()
    df.to_csv(output, index=False, sep=';', encoding='utf-8-sig')  # utf-8-sig para compatibilidade com Excel
    output.seek(0)

    # Configura a resposta para o download do arquivo CSV
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=BOM_{placa}.csv'
    return response

@bp_BOM_route.route('edit/<bom_id>', methods=['POST'])
def form_edit_BOM(bom_id):
    # query.get sempre pega a chave primária
    linha = BOMs.query.get(bom_id)
    if linha:
        linha.Componente = request.form['new_componente']
        # linha.Designator = request.form['new_designator']
        print(linha.ID)
        db.session.commit()

        flash('ITEM MODIFICADO', 'success')
    else:
        flash('Item não encontrado!', 'error')
    
    return redirect(request.referrer or url_for('home'))
