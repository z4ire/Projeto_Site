import pandas as pd
from io import BytesIO
from flask import Blueprint, request, render_template, redirect, flash, url_for, Response
from database.models.database_class import db, BOMs, OITM, PNs, ALT

bp_BOM_route = Blueprint("BOM", __name__)

@bp_BOM_route.route('/', methods=['GET'])
def lista_BOMs():

    placa = request.args.get('placa', '').strip()
    versao = request.args.get('versao', '').strip()
    status = request.args.get('status', '').strip()
    componente = request.args.get('componente', '').strip()

    # Conversão de parâmetros para listas
    placas_filtro = placa.split(',') if placa else []
    versoes_filtro = versao.split(',') if versao else []
    status_filtro = status.split(',') if status else []
    componentes_filtro = componente.split(',') if componente else []

    # Inicia a consulta base
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

    # Filtros
    if placas_filtro:
        query = query.filter(BOMs.Placa.in_(placas_filtro))
    if versoes_filtro:
        query = query.filter(BOMs.Versao.in_(versoes_filtro))
    if status_filtro:
        query = query.filter(BOMs.Status.in_(status_filtro))
    if componentes_filtro:
        query = query.filter(BOMs.Componente.in_(componentes_filtro))

    query = query.order_by(BOMs.Placa.desc(), BOMs.Versao.desc())

    # Executa a consulta se algum filtro for passado
    resultados = query.all() if (placa or versao or status or componente) else []

    # Processamento de placas
    df_dados_placas = []
    if placas_filtro:
        dados_placas = db.session.query(OITM.Codigo, OITM.Descricao).filter(OITM.Codigo.in_(placas_filtro))
        query_placas = dados_placas.all()
        df_dados_placas = [
            {
                "Codigo": placa.Codigo,
                "Descricao": placa.Descricao,
                "Link": f'<a href="http://loki/PADTEC%20-%20Campinas/Tecnologia/Hardware/Transferencia_PRO/Produto/IMTA" target="_blank">IMTA</a>',
                "baixar": f'<a href="{url_for("BOM.download_BOM", placa=placa.Codigo)}" target="_blank">xlsx</a>'
            }
            for placa in query_placas
        ]

    # Agrupamento dos resultados
    dados_agrupados = {}
    for bom in resultados:
        chave = bom.ID
        if chave not in dados_agrupados:
            dados_agrupados[chave] = []
        dados_agrupados[chave].append(bom)

    return render_template('BOMs.html', 
                           dados_agrupados=dados_agrupados,
                           dados_placa=df_dados_placas,
                           placa=placa,
                           versao=versao,
                           status=status,
                           componente=componente)

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
            ID=f"{new_placa}{new_versao}{new_status}{new_componente}{new_quantidade}{new_designator}",
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
    print("Toaqui hein")
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
    
    # Filtra a consulta para a placa específica
    df = pd.DataFrame(baixar, columns=[
        "Placa", "Versao", "Status", "Componente", "Quantidade", "Designator",
        "Descricao", "Fabricante", "PN", "Status_PN"
    ])

    # Gera o arquivo Excel em memória (em vez de CSV)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="BOMs")
    output.seek(0)  # Volta para o começo do arquivo

    # Configura a resposta para o download do arquivo Excel
    response = Response(output.getvalue(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers['Content-Disposition'] = f'attachment; filename=BOM_{placa}.xlsx'
    return response

@bp_BOM_route.route('edit/<bom_id>', methods=['POST'])
def form_edit_BOM(bom_id):
    # query.get sempre pega a chave primária
    linha = BOMs.query.get(bom_id)
    if linha:
        linha.Componente = request.form['new_componente']
        linha.ID = linha.Placa + linha.Versao + linha.Status + linha.Componente + linha.Quantidade + linha.Designator
        print(linha.ID)
        db.session.commit()

        flash('ITEM MODIFICADO', 'success')
    else:
        flash('Item não encontrado!', 'error')
    
    return redirect(request.referrer or url_for('home'))
