from flask import Blueprint, render_template

bp_home_route = Blueprint("home", __name__)

@bp_home_route.route('/', methods=['GET', 'POST'])
def home():
    
    return render_template("index.html")

# <form action="{{ url_for('BOM.form_delete_BOM', bom_id=itens[0].ID) }}" method="POST" style="display: inline;">
#                                         <button type="submit">X</button>
#                                     </form>