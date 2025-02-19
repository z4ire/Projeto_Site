# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BOMs(db.Model):
    __tablename__ = 'BOMs_Placas'
    ID = db.Column(db.Integer, primary_key=True)
    Placa = db.Column(db.String(20))
    Versao = db.Column(db.String(4))
    Componente = db.Column(db.String(20))
    Quantidade = db.Column(db.Integer)
    Designator = db.Column(db.String(10000))

class BOMs_SAP(db.Model):
    __tablename__ = 'BOMs_SAP'
    ID = db.Column(db.Integer, primary_key=True)
    Placa = db.Column(db.String(20))
    Componente = db.Column(db.String(20))
    Quantidade = db.Column(db.Integer)

class OITM(db.Model):
    __tablename__ = 'OITM_SIMPLIFICADO'
    Codigo = db.Column(db.String(20), primary_key=True)
    Descricao = db.Column(db.String(100))
    Ativo = db.Column(db.String(10))

class PNs(db.Model):
    __tablename__ = 'PNs_SQL'
    Codigo_PN = db.Column(db.String(20))
    Fabricante = db.Column(db.String(50))
    PN = db.Column(db.String(50))
    Status_PN = db.Column(db.String(25))
    CONCAT = db.Column(db.String(100), primary_key=True)

class ALT(db.Model):
    __tablename__ = 'ALTERNATIVOS_SAP'
    ID_ALT = db.Column(db.Integer, primary_key=True)
    Placa_ALT = db.Column(db.String(20))
    Comp_Princ = db.Column(db.String(20))
    Comp_Alt = db.Column(db.String(20))

class Data_Att(db.Model):
    __tablename__ = 'Metadata'
    ID_att = db.Column(db.Integer, primary_key=True)
    last_update = db.Column(db.DateTime, server_default=db.func.current_timestamp())

class Versionamento(db.Model):
    __tablename__ = 'Versionamento'
    ID_V = db.Column(db.Integer, primary_key=True)
    Placa_V = db.Column(db.String(50), nullable=False)  # Tamanho corrigido para 50
    Versao = db.Column(db.String(50), nullable=False)   # Tamanho corrigido para 50
    Status = db.Column(db.String(50))                  # Tamanho corrigido para 50
    Data_Cri = db.Column(db.String(10), nullable=False)
    Changelog = db.Column(db.String(50))               # Tamanho corrigido para 50
    Observacoes = db.Column(db.String(50))
    Eng_Resp = db.Column(db.String(50))
    Data_Att = db.Column(db.String(50), nullable=False)
    GPD_Resp = db.Column(db.String(50))

    # Define a restrição de unicidade
    __table_args__ = (
        db.UniqueConstraint('Placa_V', 'Versao', name='uq_placa_versao'),
    )