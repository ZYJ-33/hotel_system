from flask import (
    Blueprint,
    render_template,
    session,
)

blueprint = Blueprint("index", __name__)

@blueprint.route("/")
def index():
    user = session.get("username", None)
    print(user)
    return render_template("index.html", User=user)