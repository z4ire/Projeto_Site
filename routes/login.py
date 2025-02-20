from flask import Blueprint, render_template
from flask import Blueprint, request, session, redirect, url_for

bp_login_route = Blueprint("login", __name__)

users = {
    'zaire': 'zaire123',
    'usuario2': 'senha2'
}

@bp_login_route.route('/')
def home():
    return redirect(url_for('login.login'))

@bp_login_route.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('BOM.lista_BOMs'))
        else:
            return render_template('login.html', error='Usuário ou senha incorretos')

    return render_template('login.html')

@bp_login_route.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login.login'))

