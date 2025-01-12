# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BOMs(db.Model):
    __tablename__ = 'BOMs_Placas'
    ID = db.Column(db.String(50), primary_key=True)
    Placa = db.Column(db.String(20))
    Versao = db.Column(db.String(4))
    Status = db.Column(db.String(100))
    Componente = db.Column(db.String(20))
    Quantidade = db.Column(db.Integer)
    Designator = db.Column(db.String(10000))

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
