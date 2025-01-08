from flask import Blueprint, request, render_template

bp_home_route = Blueprint("home", __name__)

@bp_home_route.route('/index', methods=['GET', 'POST'])
def home():
    
    return render_template("index.html")