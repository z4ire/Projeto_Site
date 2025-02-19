import pandas as pd
import logging
from datetime import datetime
from io import BytesIO
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func
from flask import Blueprint, request, render_template, redirect, flash, url_for, Response
from database.models.database_class import db, BOMs, BOMs_SAP, OITM, PNs, ALT, Data_Att, Versionamento


# Implementar:
#     Tela de confirmação de exclusão de linha.
#     Adicionar descrição dos componentes na tela de comparação
#     Adicionar botão para baixar lista de alternativos.
#     Barra de carregamento para BOMs (Contato em tempo real entre back e front)
#     Solicitar ao TI o espelhamento dos campos de descrição e quantidade da tela de alternativos do SAP

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp_BOM_route = Blueprint("BOM", __name__)

# Funções auxiliares
def processa_parametro(parametro: str) -> list:
    """Processa parâmetros de entrada, removendo espaços e dividindo por vírgula."""
    return parametro.replace(' ', '').split(',') if parametro else []

def constroi_consulta_base():
    """Constrói a consulta base para a listagem de BOMs."""
    return db.session.query(
        BOMs.ID,
        BOMs.Placa, 
        Versionamento.Versao, 
        Versionamento.Status, 
        BOMs.Componente, 
        BOMs.Quantidade, 
        BOMs.Designator, 
        OITM.Descricao,
        PNs.Fabricante,
        PNs.PN,
        PNs.Status_PN
    ).join(OITM, BOMs.Componente == OITM.Codigo) \
.join(Versionamento, (BOMs.Placa == Versionamento.Placa_V) & (BOMs.Versao == Versionamento.Versao)) \
.join(PNs, BOMs.Componente == PNs.Codigo_PN, isouter=True)

def constroi_consulta_versoes(placa):

    return  db.session.query(
            Versionamento.ID_V,
            Versionamento.Placa_V,
            Versionamento.Versao,
            Versionamento.Status,
            Versionamento.Data_Cri,
            Versionamento.Changelog,
            Versionamento.Observacoes,
            Versionamento.Eng_Resp,
            Versionamento.Data_Att,
            Versionamento.GPD_Resp,
            OITM.Descricao
        ).join(OITM, Versionamento.Placa_V == OITM.Codigo).filter(Versionamento.Placa_V == placa).order_by(Versionamento.Versao.desc()).all()
    
def aplica_filtros(query, placa: list, versao: list, status: list, componente: list):
    """Aplica filtros à consulta base."""
    filtros = []
    if placa:
        filtros.append(BOMs.Placa.in_(placa))
    if versao:
        filtros.append(Versionamento.Versao.in_(versao))
    if status:
        filtros.append(Versionamento.Status.in_(status))
    if componente:
        filtros.append(BOMs.Componente.in_(componente))

    # Retorna a consulta com filtros ou consulta vazia se não houver filtros
    return query.filter(*filtros) if filtros else query.filter(0 == 1)

def consulta_placas(placa: list):
    """Consulta as placas e retorna dados formatados."""
    dados_placas = db.session.query(OITM.Codigo, OITM.Descricao).filter(OITM.Codigo.in_(placa)).all()
    return [
        {
            "Codigo": p.Codigo,
            "Descricao": p.Descricao,
            "baixar": url_for("BOM.download_BOM", placa=p.Codigo)
        }
        for p in dados_placas
    ]

def verificar_e_inserir_versionamento(placa, versao):
    """
    Verifica se a combinação de placa e versão já existe na tabela de versionamento.
    Se não existir, insere uma nova entrada.
    """
    try:
        new_version = Versionamento(Placa_V=placa, Versao=versao, Data_Cri=datetime.now().strftime('%d/%m/%Y'), Data_Att=datetime.now().strftime('%d/%m/%Y'))
        db.session.add(new_version)
        db.session.commit()
        flash('Dados carregados com sucesso.', 'success')
        return True  # Indica que uma nova versão foi inserida
    except IntegrityError:
        db.session.rollback()
        flash('Já existe esta combinação de placa-versao.', 'success')
        return False  # Indica que a versão já existe

def diff_SAP(placa, v_max, version_a, version_b):

    def fetch_bom_data(version, placa, is_sap=False):
        if is_sap:
            query = db.session.query(func.replace(BOMs_SAP.Componente, ' ', '').label('Componente'),  # Remover espaços antes do join
            BOMs_SAP.Quantidade,
            OITM.Descricao).filter(BOMs_SAP.Placa == placa).join(OITM, func.replace(BOMs_SAP.Componente, ' ', '') == OITM.Codigo).all()

        else:
            query = db.session.query(
                BOMs.Componente, 
                BOMs.Quantidade,
                OITM.Descricao
            ).join(OITM, BOMs.Componente == OITM.Codigo).filter(BOMs.Versao == version, BOMs.Placa == placa).all()

        # Retorna uma lista de tuplas (componente, quantidade, descrição)
        return [(row.Componente.replace(" ", ""), row.Quantidade, row.Descricao) for row in query]

    # Obter os dados das versões
    bom_data_a = fetch_bom_data(version_a, placa, is_sap=(version_a == 'SAP'))
    bom_data_b = fetch_bom_data(version_b, placa, is_sap=(version_b == 'SAP'))

    # Criar dicionários {componente: (quantidade, descrição)}
    dict_a = {component: (quantity, description) for component, quantity, description in bom_data_a}
    dict_b = {component: (quantity, description) for component, quantity, description in bom_data_b}

    # Componentes exclusivos em BOMs
    exclusive_in_a = [
        {"componente": componente, "quantidade": dict_a[componente][0], "descricao": dict_a[componente][1]}
        for componente in dict_a if componente not in dict_b
    ]

    # Componentes exclusivos em BOMs_SAP
    exclusive_in_b = [
        {"componente": componente, "quantidade": dict_b[componente][0], "descricao": dict_b[componente][1]}
        for componente in dict_b if componente not in dict_a
    ]

    # Componentes comuns com quantidades diferentes
    comuns_com_diferencas = []
    for componente in dict_a:
        if componente in dict_b and dict_a[componente][0] != dict_b[componente][0]:
            comuns_com_diferencas.append({
                "componente": componente,
                "quantidade_BOMs": dict_a[componente][0],
                "quantidade_BOMs_SAP": dict_b[componente][0],
                "descricao": dict_a[componente][1]  # Ambas as listas usam a mesma descrição
            })

    # Retornar o resultado formatado
    diff = {
        "exclusivos_em_BOMs": exclusive_in_a,
        "exclusivos_em_BOMs_SAP": exclusive_in_b,
        "comuns_com_diferencas": comuns_com_diferencas
    }

    return diff

@bp_BOM_route.route('/', methods=['GET'])
def lista_BOMs():
    try:
        data_hora = Data_Att.query.first()
        last_update = data_hora.last_update.strftime("%Y-%m-%d %H:%M:%S") if data_hora else None

        # Processa parâmetros de entrada
        placa = processa_parametro(request.args.get('placa', ''))
        versao = processa_parametro(request.args.get('versao', ''))
        status = processa_parametro(request.args.get('status', '').strip())
        componente = processa_parametro(request.args.get('componente', ''))

        # Constrói a consulta base
        query = constroi_consulta_base()
        # Cria a lista de filtros dinamicamente
        query = aplica_filtros(query, placa, versao, status, componente)

        # Paginação
        page = request.args.get('page', 1, type=int)
        per_page = 100

        resultados = query.order_by(BOMs.Placa.asc(), Versionamento.Versao.desc()).paginate(page=page, per_page=per_page, error_out=False)

        # Consulta dados das placas
        dados_placas = consulta_placas(placa) if placa else []

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
            pagination=resultados,
            last_update=last_update
        )
    except Exception as e:
        logger.error(f"Erro ao listar BOMs: {str(e)}")
        flash("Ocorreu um erro ao listar os BOMs. Tente novamente.", "error")
        return redirect(url_for('BOM.lista_BOMs'))

@bp_BOM_route.route('/new', methods=['POST'])
def add_BOMs():

    # Verifica se a requisição contém um arquivo (Excel)
    file = request.files.get('file')
    if file and file.filename.endswith('.xlsx'):  # Caso o arquivo seja Excel
        try:
            # Lê o arquivo Excel diretamente da memória com pandas
            data = pd.read_excel(file)
            data = data.dropna(how='all')  # Remove linhas vazias
            
            # Itera pelas linhas do DataFrame e adiciona ao banco de dados
            for _, row in data.iterrows():

                verificar_e_inserir_versionamento(row['Placa'], row['Versao'])

                new_BOM = BOMs(
                    Placa=row['Placa'],
                    Versao=row['Versao'],
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
        new_componente = request.form.get('new_componente', '').strip()
        new_quantidade = request.form.get('new_quantidade', '').strip()
        new_designator = request.form.get('new_designator', '').strip()

       # Verifica se todos os campos foram preenchidos
        if any([new_placa, new_versao, new_componente, new_quantidade, new_designator]):

            if all([new_placa, new_versao, new_componente, new_quantidade, new_designator]):

                verificar_e_inserir_versionamento(new_placa, new_versao)

                # Cria o novo BOM a partir dos dados do formulário
                new_BOM = BOMs(
                    Placa=new_placa,
                    Versao=new_versao,
                    Componente=new_componente,
                    Quantidade=new_quantidade,
                    Designator=new_designator
                )

                # Adiciona o novo BOM ao banco de dados
                db.session.add(new_BOM)
                db.session.commit()
                
            else:  
                flash('Nem todos os campos foram preenchidos', 'success')
        else:
            flash('Não é um xlsx', 'success')

    return redirect(request.referrer or url_for('home'))

@bp_BOM_route.route('/new', methods=['GET'])
def versoes():
    """Lista as versões das placas cadastradas."""
    try:

        placa = processa_parametro(request.args.get('placa', ''))

        # Verifica se a lista não está vazia antes de tentar acessar o primeiro item
        if placa:
            placa = placa[0]  # Acessa o primeiro item, se a lista não estiver vazia
        else:
            placa = ''  # Ou outro valor padrão, se a lista estiver vazia

        # Executa a consulta
        resultados = constroi_consulta_versoes(placa)

        v_max = resultados[0].Versao if resultados else None

        try:
            Va = processa_parametro(request.args.get('Va', ''))[0]
            Vb = processa_parametro(request.args.get('Vb', ''))[0]
        
        except (IndexError, TypeError):
            Va = v_max
            Vb = v_max

        diff = diff_SAP(placa, v_max, Va, Vb)

        return render_template('formulario_cadastro_BOM.html', versoes=resultados, placa=placa, diferencas=diff, v_max=v_max, Va=Va, Vb=Vb)
    
    except SQLAlchemyError as e:
        logger.error(f"Erro ao consultar versões: {str(e)}")
        flash("Ocorreu um erro ao consultar as versões. Tente novamente.", "error")
        return redirect(url_for('BOM.lista_BOMs'))
    except Exception as e:
        logger.error(f"Erro inesperado ao consultar versões: {str(e)}")
        flash("Ocorreu um erro inesperado. Tente novamente.", "error")
        print("Mensagem de erro:", e)
        return redirect(url_for('BOM.lista_BOMs'))

@bp_BOM_route.route('/alt', methods=['GET'])
def alternativos_BOM():

    """Lista componentes alternativos com base na placa fornecida."""
    try:
        placa = request.args.get('placa', '').strip()

        # Constrói a consulta base
        query = db.session.query(
            OITM.Codigo,
            ALT.Placa_ALT,
            ALT.Comp_Princ,
            ALT.Comp_Alt,
            PNs.Fabricante,
            PNs.PN,
            PNs.Status_PN
        ).join(OITM, OITM.Codigo == ALT.Placa_ALT).join(PNs, PNs.Codigo_PN == ALT.Comp_Alt)

        # Aplica filtro de placa, se fornecido
        if placa:
            query = query.filter(OITM.Codigo == placa)
            dados_placas = db.session.query(OITM.Codigo, OITM.Descricao).filter(OITM.Codigo == placa).all()
        else:
            dados_placas = []

        # Ordena os resultados
        query = query.order_by(ALT.Comp_Princ.desc())

        # Executa a consulta
        resultados = query.all() if placa else []

        return render_template('Alt.html', dados=resultados, dados_placa=dados_placas)
    except SQLAlchemyError as e:
        logger.error(f"Erro ao consultar alternativos: {str(e)}")
        flash("Ocorreu um erro ao consultar os componentes alternativos. Tente novamente.", "error")
        return redirect(url_for('BOM.lista_BOMs'))
    except Exception as e:
        logger.error(f"Erro inesperado ao consultar alternativos: {str(e)}")
        flash("Ocorreu um erro inesperado. Tente novamente.", "error")
        return redirect(url_for('BOM.lista_BOMs'))

@bp_BOM_route.route('/delete/linha/<bom_id>', methods=['POST'])
def Exclui_Componente(bom_id):
    """Exclui um BOM com base no ID."""
    try:
        linha = BOMs.query.get(bom_id)
        if linha:
            db.session.delete(linha)
            db.session.commit()
            flash("Item excluído com sucesso.", "success")
        else:
            flash("Item não encontrado.", "error")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erro ao excluir BOM: {str(e)}")
        flash("Erro ao excluir o item. Tente novamente.", "error")
    return redirect(request.referrer or url_for('home'))

@bp_BOM_route.route('/delete/versao/<bom_id>', methods=['POST'])
def Exclui_Versao(bom_id):
    
    """Exclui um BOM com base no ID."""
    print(f'ID recebido: {bom_id}')
    try:
        linha = Versionamento.query.get(bom_id)
        if linha:
            placa = linha.Placa_V  # Pegando a placa antes de deletar a versão
            versao = linha.Versao   # Pegando a versão antes de deletar a versão
            
            # Excluindo todas as entradas da tabela BOMs que possuem a mesma placa
            BOMs.query.filter_by(Placa=placa, Versao=versao).delete()
            
            # Agora exclui a versão no versionamento
            db.session.delete(linha)
            db.session.commit()
        else:
            flash("Item não encontrado.", "error")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erro ao excluir BOM: {str(e)}")
        flash("Erro ao excluir o item. Tente novamente.", "error")
    return redirect(request.referrer or url_for('home'))

@bp_BOM_route.route('/download/<placa>', methods=['GET'])
def download_BOM(placa):
    # Refaça a consulta para este caso específico da placa
    try:
        query = constroi_consulta_base()

        query = query.filter(BOMs.Placa == placa)
        baixar = query.all()

        # Converte os dados para DataFrame
        df = pd.DataFrame(baixar, columns=[
            "ID", "Placa", "Versao", "Versão", "Componente", "Quantidade", "Designator",
            "Descricao", "Fabricante", "PN", "Status_PN"
        ])

        output = BytesIO()
        df.to_csv(output, index=False, sep=';', encoding='utf-8-sig')
        output.seek(0)

        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename=BOM_{placa}.csv'
        return response
    
    except Exception as e:
        logger.error(f"Erro ao gerar CSV: {str(e)}")
        flash("Ocorreu um erro ao gerar o arquivo. Tente novamente.", "error")
        return redirect(url_for('BOM.lista_BOMs'))

#EDIÇÃO DE COMPONENTE DE UMA BOM
@bp_BOM_route.route('/edit/componente/<bom_id>', methods=['POST'])
def edit_BOM(bom_id):
    """Edita um BOM com base no ID."""
    try:
        linha = BOMs.query.get(bom_id)
        if linha:
            linha.Componente = request.form['new_componente']
            linha.Quantidade = request.form['new_quantidade']
            linha.Designator = request.form['new_designator']
            db.session.commit()
            flash("Item modificado com sucesso.", "success")
        else:
            flash("Item não encontrado.", "error")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erro ao editar BOM: {str(e)}")
        flash("Erro ao modificar o item. Tente novamente.", "error")
    return redirect(request.referrer or url_for('home'))

#EDIÇÃO DE VERSÃO DE UMA BOM
@bp_BOM_route.route('/edit/versao/<bom_id>', methods=['POST'])
def edit_versao_BOM(bom_id):
    try:
        linha = Versionamento.query.get(bom_id)
        if linha:
            linha.Status = request.form['new_status']
            linha.Changelog = request.form['new_changelog']
            linha.Eng_Resp = request.form['new_eng']
            linha.GPD_Resp = request.form['new_gpd']
            linha.Data_Att = request.form['new_data_att']
            linha.Observacoes = request.form['new_obs']
            db.session.commit()
            flash("Versão modificada com sucesso.", "success")
        else:
            flash("Versão não encontrada", "error")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erro ao editar BOM: {str(e)}")
        flash("Erro ao modificar o item. Tente novamente.", "error")
    return redirect(request.referrer or url_for('home'))

@bp_BOM_route.route('/old', methods=['GET'])
def versoes2():
    """Lista as versões das placas cadastradas."""
    try:

        placa = processa_parametro(request.args.get('placa', ''))

        # Verifica se a lista não está vazia antes de tentar acessar o primeiro item
        if placa:
            placa = placa[0]  # Acessa o primeiro item, se a lista não estiver vazia
        else:
            placa = ''  # Ou outro valor padrão, se a lista estiver vazia

        # Executa a consulta
        resultados = constroi_consulta_versoes(placa)

        v_max = resultados[0].Versao if resultados else None

        try:
            Va = processa_parametro(request.args.get('Va', ''))[0]
            Vb = processa_parametro(request.args.get('Vb', ''))[0]

        except (IndexError, TypeError):
            Va = v_max
            Vb = v_max
            
        diff = diff_SAP(placa, v_max, Va, Vb)

        return render_template('add_bom.html', versoes=resultados, placa=placa, diferencas=diff, v_max=v_max, Va=Va, Vb=Vb)
    
    except SQLAlchemyError as e:
        logger.error(f"Erro ao consultar versões: {str(e)}")
        flash("Ocorreu um erro ao consultar as versões. Tente novamente.", "error")
        return redirect(url_for('BOM.lista_BOMs'))
    except Exception as e:
        logger.error(f"Erro inesperado ao consultar versões: {str(e)}")
        flash("Ocorreu um erro inesperado. Tente novamente.", "error")
        print("Mensagem de erro:", e)
        return redirect(url_for('BOM.lista_BOMs'))