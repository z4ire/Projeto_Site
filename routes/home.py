from flask import Blueprint, render_template

bp_home_route = Blueprint("home", __name__)

@bp_home_route.route('/', methods=['GET', 'POST'])
def home():
    
    return render_template("index.html")