from routes.home import bp_home_route
from routes.BOM import bp_BOM_route
from flask import Flask
from config import Config
from database.models.database_class import db

# Criação da instância da aplicação Flask
app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(bp_home_route)
app.register_blueprint(bp_BOM_route, url_prefix = '/BOMs')
app.secret_key = 'apppadtec'

db.init_app(app)
if __name__ == '__main__':
    # Executa a aplicação Flask com o modo debug ativado e na porta 5002
    app.run(debug=True, port=5002)